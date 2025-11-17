from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
from minio import Minio
from pydantic import BaseModel
import os, mimetypes, urllib.parse, json, redis, uuid, httpx
from datetime import datetime
from typing import Optional, List, Dict

app = FastAPI(title="Multimedia API")

REQUESTS = Counter("api_requests_total", "Total de requests")
ACTIVE_SESSIONS = Gauge("active_sessions", "Sesiones activas")
CONVERSION_REQUESTS = Counter("conversion_requests_total", "Total de conversiones solicitadas")
JOBS_ENQUEUED = Gauge("jobs_enqueued", "Trabajos en cola")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class ConversionRequest(BaseModel):
    input_file: str
    output_format: str
    options: Optional[dict] = None

class JobStatus(BaseModel):
    job_id: str
    status: str  # pending, processing, completed, failed
    input_file: str
    output_format: str
    output_file: Optional[str] = None
    worker_id: Optional[str] = None
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    progress: Optional[int] = 0

endpoint_url = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
parsed = urllib.parse.urlparse(endpoint_url)
endpoint = parsed.netloc or parsed.path
secure = parsed.scheme == "https"

MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "admin12345")
BUCKET = os.getenv("MINIO_BUCKET", "media")

minio = Minio(endpoint, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=secure)

# Redis connection
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Redis keys
JOBS_QUEUE = "conversion:queue"
JOBS_STATUS_PREFIX = "job:status:"

# Prometheus configuration
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")

# Worker configuration
WORKERS = [
    {"id": "worker_a", "host": "worker_a", "metrics_port": 9101},
    {"id": "worker_b", "host": "worker_b", "metrics_port": 9102},
]

async def get_worker_metrics(worker_id: str, metric_name: str) -> Optional[float]:
    """Obtener métrica de un worker desde Prometheus"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            query = f'{metric_name}{{job=~"workers.*"}}'
            response = await client.get(
                f"{PROMETHEUS_URL}/api/v1/query",
                params={"query": query}
            )
            data = response.json()
            
            if data.get("status") == "success":
                results = data.get("data", {}).get("result", [])
                for result in results:
                    # Buscar el worker específico por su puerto de métricas
                    instance = result.get("metric", {}).get("instance", "")
                    if worker_id in instance or str(WORKERS[0 if worker_id == "worker_a" else 1]["metrics_port"]) in instance:
                        return float(result.get("value", [None, 0])[1])
            return None
    except Exception as e:
        print(f"Error obteniendo métrica {metric_name} de {worker_id}: {e}")
        return None

async def get_worker_stats(worker_id: str) -> Dict:
    """Obtener estadísticas completas de un worker"""
    cpu_load = await get_worker_metrics(worker_id, "worker_cpu_load")
    memory_usage = await get_worker_metrics(worker_id, "worker_memory_usage_mb")
    jobs_in_progress = await get_worker_metrics(worker_id, "worker_jobs_in_progress")
    
    # Obtener conversiones completadas
    conversions_success = await get_worker_metrics(worker_id, 'worker_conversions_done_total{status="success"}')
    conversions_failed = await get_worker_metrics(worker_id, 'worker_conversions_done_total{status="failed"}')
    
    return {
        "worker_id": worker_id,
        "cpu_load": cpu_load if cpu_load is not None else 0.0,
        "memory_mb": memory_usage if memory_usage is not None else 0.0,
        "jobs_in_progress": int(jobs_in_progress) if jobs_in_progress is not None else 0,
        "conversions_success": int(conversions_success) if conversions_success is not None else 0,
        "conversions_failed": int(conversions_failed) if conversions_failed is not None else 0,
        "available": True,  # TODO: Implementar health check real
    }

async def select_best_worker() -> str:
    """Seleccionar el worker con menor carga para asignar trabajo"""
    workers_stats = []
    
    for worker in WORKERS:
        stats = await get_worker_stats(worker["id"])
        workers_stats.append(stats)
    
    # Ordenar por carga (prioridad: jobs en progreso, luego CPU)
    # Worker con menos jobs y menor CPU es el mejor
    best_worker = min(
        workers_stats,
        key=lambda w: (w["jobs_in_progress"], w["cpu_load"])
    )
    
    print(f"[BALANCEO] Seleccionado {best_worker['worker_id']} (jobs: {best_worker['jobs_in_progress']}, CPU: {best_worker['cpu_load']:.2f})")
    
    return best_worker["worker_id"]

@app.on_event("startup")
def ensure_bucket():
    if not minio.bucket_exists(BUCKET):
        minio.make_bucket(BUCKET)

# Montar archivos estáticos (HTML)
app.mount("/static", StaticFiles(directory="/app/web"), name="static")

@app.get("/")
def root():
    """Redirigir a player.html"""
    return FileResponse("/app/web/player.html")

@app.get("/admin.html")
def admin():
    """Servir dashboard de monitoreo"""
    return FileResponse("/app/web/admin.html")

@app.get("/player.html")
def player():
    """Servir interfaz de usuario"""
    return FileResponse("/app/web/player.html")

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

@app.post("/convert")
async def request_conversion(req: ConversionRequest):
    """Solicitar conversión de archivo multimedia con balanceo de carga inteligente"""
    CONVERSION_REQUESTS.inc()
    
    # Verificar que el archivo existe en MinIO
    try:
        minio.stat_object(BUCKET, req.input_file)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {req.input_file}")
    
    # Validar formato de salida
    valid_audio = ["mp3", "flac", "wav", "aac", "ogg"]
    valid_video = ["mp4", "avi", "mkv", "webm", "mov"]
    valid_formats = valid_audio + valid_video
    
    output_fmt = req.output_format.lower()
    if output_fmt not in valid_formats:
        raise HTTPException(status_code=400, detail=f"Formato no soportado: {output_fmt}")
    
    # Seleccionar el mejor worker según carga actual
    assigned_worker = await select_best_worker()
    
    # Crear job
    job_id = str(uuid.uuid4())
    job_data = {
        "job_id": job_id,
        "status": "pending",
        "input_file": req.input_file,
        "output_format": output_fmt,
        "options": req.options or {},
        "created_at": datetime.utcnow().isoformat(),
        "progress": 0,
        "assigned_worker": assigned_worker,  # Nuevo: worker asignado
    }
    
    # Guardar estado del job
    redis_client.set(f"{JOBS_STATUS_PREFIX}{job_id}", json.dumps(job_data))
    
    # Encolar job en cola específica del worker
    worker_queue = f"conversion:queue:{assigned_worker}"
    redis_client.rpush(worker_queue, job_id)
    
    # También en cola general (fallback)
    redis_client.rpush(JOBS_QUEUE, job_id)
    
    JOBS_ENQUEUED.inc()
    
    return {
        "ok": True, 
        "job_id": job_id, 
        "status": "pending",
        "assigned_worker": assigned_worker
    }

@app.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    """Obtener estado de un trabajo de conversión"""
    job_data = redis_client.get(f"{JOBS_STATUS_PREFIX}{job_id}")
    if not job_data:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    
    return json.loads(job_data)

@app.get("/jobs")
def list_jobs(status: Optional[str] = None, limit: int = 50):
    """Listar trabajos de conversión"""
    # Obtener todas las keys de jobs
    keys = redis_client.keys(f"{JOBS_STATUS_PREFIX}*")
    jobs = []
    
    for key in keys[:limit]:
        job_data = redis_client.get(key)
        if job_data:
            job = json.loads(job_data)
            if status is None or job.get("status") == status:
                jobs.append(job)
    
    # Ordenar por fecha de creación (más reciente primero)
    jobs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    return {"jobs": jobs, "total": len(jobs)}

@app.get("/queue/stats")
def queue_stats():
    """Estadísticas de la cola de trabajos"""
    queue_length = redis_client.llen(JOBS_QUEUE)
    
    # Contar jobs por estado
    keys = redis_client.keys(f"{JOBS_STATUS_PREFIX}*")
    stats = {"pending": 0, "processing": 0, "completed": 0, "failed": 0}
    
    for key in keys:
        job_data = redis_client.get(key)
        if job_data:
            job = json.loads(job_data)
            status = job.get("status", "unknown")
            if status in stats:
                stats[status] += 1
    
    return {
        "queue_length": queue_length,
        "stats": stats,
        "total_jobs": len(keys)
    }

@app.get("/workers/stats")
async def workers_stats():
    """Estadísticas de todos los workers para dashboard de monitoreo"""
    workers_data = []
    
    for worker in WORKERS:
        stats = await get_worker_stats(worker["id"])
        
        # Agregar información adicional
        stats["host"] = worker["host"]
        stats["metrics_port"] = worker["metrics_port"]
        
        # Calcular score de carga (0-100, donde 100 es completamente ocupado)
        load_score = min(100, int(
            (stats["jobs_in_progress"] * 30) +  # 30 puntos por job
            (stats["cpu_load"] * 50)            # 50 puntos por CPU completo
        ))
        stats["load_score"] = load_score
        stats["status"] = "busy" if load_score > 60 else "available" if load_score > 30 else "idle"
        
        workers_data.append(stats)
    
    # Estadísticas generales
    total_jobs = sum(w["jobs_in_progress"] for w in workers_data)
    avg_cpu = sum(w["cpu_load"] for w in workers_data) / len(workers_data) if workers_data else 0
    total_success = sum(w["conversions_success"] for w in workers_data)
    total_failed = sum(w["conversions_failed"] for w in workers_data)
    
    return {
        "workers": workers_data,
        "summary": {
            "total_workers": len(workers_data),
            "active_workers": sum(1 for w in workers_data if w["available"]),
            "total_jobs_processing": total_jobs,
            "average_cpu_load": round(avg_cpu, 2),
            "total_conversions_success": total_success,
            "total_conversions_failed": total_failed,
        }
    }
