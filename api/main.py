from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
from minio import Minio
import os, mimetypes, urllib.parse

app = FastAPI(title="Multimedia API")

REQUESTS = Counter("api_requests_total", "Total de requests")
ACTIVE_SESSIONS = Gauge("active_sessions", "Sesiones activas")

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
def list_media():
    try:
        return {"objects": [o.object_name for o in minio.list_objects(BUCKET, recursive=True)]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/media/{name}")
def stream_media(name: str):
    try:
        resp = minio.get_object(BUCKET, name)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"No existe: {name}. {e}")
    mime, _ = mimetypes.guess_type(name)
    if mime is None:
        mime = "application/octet-stream"
    def it():
        try:
            while True:
                chunk = resp.read(1024 * 1024)
                if not chunk: break
                yield chunk
        finally:
            resp.close(); resp.release_conn()
    return StreamingResponse(it(), media_type=mime)

@app.post("/upload")
def upload_media(file: UploadFile = File(...)):
    try:
        minio.put_object(
            BUCKET, file.filename, file.file,
            length=-1, part_size=10*1024*1024,
            content_type=file.content_type or "application/octet-stream",
        )
        return {"ok": True, "name": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
