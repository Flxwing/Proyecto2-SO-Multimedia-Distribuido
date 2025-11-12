from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
from minio import Minio
import os, mimetypes, urllib.parse
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from minio.error import S3Error
import re
from pydantic import BaseModel
import redis, time

app = FastAPI(title="Multimedia API")

# --- Redis client ---
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
# decode_responses=False -> redis devuelve bytes (tu código ya hace .decode())
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=False)

REQUESTS = Counter("api_requests_total", "Total de requests")
ACTIVE_SESSIONS = Gauge("active_sessions", "Sesiones activas")
API_UPLOADS        = Counter("api_uploads_total",        "Total de subidas exitosas")
API_STREAMS        = Counter("api_streams_total",        "Total de streams exitosos")
API_LOGINS         = Counter("api_logins_total",         "Logins exitosos")
API_DELETES       = Counter("api_deletes_total", "Borrados exitosos")
API_JOBS_ENQUEUED  = Counter("api_jobs_enqueued_total",  "Jobs de conversión encolados")   # si usan conversión
QUEUE_LEN          = Gauge  ("redis_media_jobs_len",     "Items en cola media_jobs")       # si usan conversión

# ==== AUTH (demo) ====
SECRET_KEY = "cambia_esto_por_un_valor_secreto_largo"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_.-]{3,32}$")

def user_key(u: str) -> str:
    return f"user:{u}"

def user_exists(u: str) -> bool:
    return bool(r.exists(user_key(u)))

def get_user_hash(u: str) -> str | None:
    h = r.hget(user_key(u), "password_hash")
    return h.decode() if h else None

def create_user(u: str, p: str):
    pwd_hash = pwd_context.hash(p)
    r.hset(user_key(u), mapping={
        "password_hash": pwd_hash,
        "created_at": datetime.utcnow().isoformat()
    })

def create_access_token(data: dict, minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(minutes=minutes)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_user(username: str, password: str) -> bool:
    h = get_user_hash(username)
    return bool(h) and pwd_context.verify(password, h)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    cred_exc = HTTPException(status_code=401, detail="Invalid credentials",
                             headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username or not user_exists(username):
            raise cred_exc
        return {"username": username}
    except JWTError:
        raise cred_exc
    
class SignupReq(BaseModel):
    username: str
    password: str

@app.on_event("startup")
def wait_for_redis():
    for _ in range(30):
        try:
            r.ping()
            return
        except Exception:
            time.sleep(1)
    # Si no responde en ~30s, fallamos el arranque (opcional)
    raise RuntimeError("Redis no disponible")


@app.post("/auth/signup")
def signup(req: SignupReq):
    u = req.username.strip(); p = req.password
    if not USERNAME_RE.match(u):
        raise HTTPException(status_code=400, detail="Usuario inválido (3–32, letras/números/._-)")
    if len(p) < 8:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 8 caracteres")
    if user_exists(u):
        raise HTTPException(status_code=409, detail="El usuario ya existe")

    create_user(u, p)
    token = create_access_token({"sub": u})
    API_LOGINS.inc()
    return {"ok": True, "access_token": token, "token_type": "bearer"}

@app.post("/auth/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    if not verify_user(form.username, form.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    API_LOGINS.inc()
    token = create_access_token({"sub": form.username})
    return {"access_token": token, "token_type": "bearer"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

endpoint_url = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
parsed = urllib.parse.urlparse(endpoint_url)
endpoint = parsed.netloc or parsed.path
secure = parsed.scheme == "https"

MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "admin12345")
BUCKET = os.getenv("MINIO_BUCKET", "media")

minio = Minio(endpoint, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=secure)

@app.on_event("startup")
def ensure_bucket():
    if not minio.bucket_exists(BUCKET):
        minio.make_bucket(BUCKET)

@app.get("/health")
def health():
    REQUESTS.inc()
    return {"ok": True}

@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/media")
def list_media(user: dict = Depends(get_current_user)):
    prefix = f"{user['username']}/"
    try:
        objs = minio.list_objects(BUCKET, prefix=prefix, recursive=True)
        return {"objects": [o.object_name[len(prefix):] for o in objs]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Stream de MI archivo
@app.get("/media/{name}")
def stream_media(name: str, user: dict = Depends(get_current_user)):
    object_name = f"{user['username']}/{name}"
    try:
        resp = minio.get_object(BUCKET, object_name)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"No existe: {name}. {e}")

    mime, _ = mimetypes.guess_type(name)
    if mime is None: mime = "application/octet-stream"

    def it():
        try:
            while True:
                chunk = resp.read(1024 * 1024)
                if not chunk: break
                yield chunk
        finally:
            resp.close(); resp.release_conn()

    API_STREAMS.inc()  # <-- aquí
    return StreamingResponse(it(), media_type=mime)

# Subir a MI carpeta
@app.post("/upload")
def upload_media(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    object_name = f"{user['username']}/{file.filename}"
    try:
        minio.put_object(
            BUCKET, object_name, file.file,
            length=-1, part_size=10*1024*1024,
            content_type=file.content_type or "application/octet-stream",
        )
        API_UPLOADS.inc()  # <-- aquí (solo si no hubo excepción)
        return {"ok": True, "name": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/share/{name}")
def share(name: str, minutes: int = 60, user: dict = Depends(get_current_user)):
    object_name = f"{user['username']}/{name}"
    try:
        url = minio.presigned_get_object(BUCKET, object_name, expires=timedelta(minutes=minutes))
        return {"url": url, "expires_in_min": minutes}
    except S3Error as e:
        raise HTTPException(status_code=404, detail=str(e))
    
# DELETE /media/{name} — quita API_STREAMS.inc() y usa API_DELETES.inc()
@app.delete("/media/{name}")
def delete_media(name: str, user: dict = Depends(get_current_user)):
    object_name = f"{user['username']}/{name}"
    try:
        minio.remove_object(BUCKET, object_name)
        API_DELETES.inc()   # <-- métrica correcta para borrado
        return {"ok": True}
    except S3Error as e:
        raise HTTPException(status_code=404, detail=str(e))
