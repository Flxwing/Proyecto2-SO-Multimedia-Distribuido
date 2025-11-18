import os, time, json, subprocess, tempfile, socket
from pathlib import Path
from datetime import datetime
from prometheus_client import Gauge, Counter, Histogram, start_http_server
from minio import Minio
import redis
import urllib.parse
import psutil

# Métricas Prometheus
CPU_LOAD = Gauge("worker_cpu_load", "Carga CPU del worker")
MEMORY_USAGE = Gauge("worker_memory_usage_mb", "Uso de memoria en MB")
JOBS_IN_PROGRESS = Gauge("worker_jobs_in_progress", "Jobs en progreso")
CONV_DONE = Counter("worker_conversions_done_total", "Conversiones completadas", ["status"])
CONV_DURATION = Histogram("worker_conversion_duration_seconds", "Duración de conversión")
FILE_SIZE_REDUCTION = Histogram("worker_file_size_reduction_percent", "Porcentaje de reducción de tamaño")

# Configuración
WORKER_ID = socket.gethostname()
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
METRICS_PORT = int(os.getenv("METRICS_PORT", "9101"))

# MinIO
endpoint_url = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
parsed = urllib.parse.urlparse(endpoint_url)
endpoint = parsed.netloc or parsed.path
secure = parsed.scheme == "https"

MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "admin12345")
BUCKET = os.getenv("MINIO_BUCKET", "media")

minio = Minio(endpoint, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=secure)
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Redis keys
JOBS_QUEUE = "conversion:queue"
JOBS_STATUS_PREFIX = "job:status:"
WORKER_QUEUE = f"conversion:queue:{WORKER_ID}"  # Cola específica del worker
WORKER_STATUS_KEY = f"worker:status:{WORKER_ID}"

CURRENT_JOBS = 0
SUCCESS_COUNT = 0
FAILED_COUNT = 0

def update_job_status(job_id, updates):
    """Actualizar estado del job en Redis"""
    job_key = f"{JOBS_STATUS_PREFIX}{job_id}"
    job_data = redis_client.get(job_key)
    if job_data:
        job = json.loads(job_data)
        job.update(updates)
        redis_client.set(job_key, json.dumps(job))
        return job
    return None

def publish_worker_status(cpu_percent: float, memory_mb: float):
    payload = {
        "worker_id": WORKER_ID,
        "status": "busy" if CURRENT_JOBS > 0 else "available",
        "cpu_load": round(cpu_percent / 100.0, 4),
        "memory_mb": round(memory_mb, 2),
        "jobs_in_progress": CURRENT_JOBS,
        "load_score": min(100, round(cpu_percent)),
        "conversions_success": SUCCESS_COUNT,
        "conversions_failed": FAILED_COUNT,
        "updated_at": datetime.utcnow().isoformat()
    }
    redis_client.set(WORKER_STATUS_KEY, json.dumps(payload), ex=15)

def get_file_extension(filename):
    """Obtener extensión del archivo"""
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

def convert_audio(input_path, output_path, output_format, options=None):
    """Convertir archivo de audio con FFmpeg"""
    options = options or {}
    
    # Comandos base para cada formato
    cmd = ["ffmpeg", "-i", input_path, "-y"]
    
    if output_format == "mp3":
        bitrate = options.get("bitrate", "192k")
        cmd.extend(["-codec:a", "libmp3lame", "-b:a", bitrate])
    elif output_format == "flac":
        compression = options.get("compression", "5")
        cmd.extend(["-codec:a", "flac", "-compression_level", str(compression)])
    elif output_format == "wav":
        cmd.extend(["-codec:a", "pcm_s16le"])
    elif output_format == "aac":
        bitrate = options.get("bitrate", "192k")
        cmd.extend(["-codec:a", "aac", "-b:a", bitrate])
    elif output_format == "ogg":
        quality = options.get("quality", "5")
        cmd.extend(["-codec:a", "libvorbis", "-q:a", str(quality)])
    
    cmd.append(output_path)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"FFmpeg error: {result.stderr}")
    
    return True

def convert_video(input_path, output_path, output_format, options=None):
    """Convertir archivo de video con FFmpeg"""
    options = options or {}
    
    cmd = ["ffmpeg", "-i", input_path, "-y"]
    
    # Configuración común
    video_codec = options.get("video_codec", "libx264")
    crf = options.get("crf", "23")  # Calidad (0-51, menor = mejor)
    preset = options.get("preset", "medium")  # ultrafast, fast, medium, slow
    
    if output_format == "mp4":
        cmd.extend([
            "-codec:v", video_codec,
            "-crf", str(crf),
            "-preset", preset,
            "-codec:a", "aac",
            "-b:a", "128k"
        ])
    elif output_format == "avi":
        cmd.extend([
            "-codec:v", "mpeg4",
            "-q:v", "5",
            "-codec:a", "libmp3lame",
            "-b:a", "128k"
        ])
    elif output_format == "mkv":
        cmd.extend([
            "-codec:v", video_codec,
            "-crf", str(crf),
            "-preset", preset,
            "-codec:a", "aac"
        ])
    elif output_format == "webm":
        cmd.extend([
            "-codec:v", "libvpx-vp9",
            "-crf", str(crf),
            "-b:v", "0",
            "-codec:a", "libopus"
        ])
    elif output_format == "mov":
        cmd.extend([
            "-codec:v", video_codec,
            "-crf", str(crf),
            "-preset", preset,
            "-codec:a", "aac"
        ])
    
    cmd.append(output_path)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"FFmpeg error: {result.stderr}")
    
    return True

def process_job(job_id):
    """Procesar un trabajo de conversión"""
    global CURRENT_JOBS, SUCCESS_COUNT, FAILED_COUNT
    print(f"[{WORKER_ID}] Procesando job {job_id}")

    # Obtener detalles del job
    job_data = redis_client.get(f"{JOBS_STATUS_PREFIX}{job_id}")
    if not job_data:
        print(f"[{WORKER_ID}] Job {job_id} no encontrado")
        return

    job = json.loads(job_data)
    owner = job.get("owner")
    input_object = job.get("input_object") or job.get("input_file")
    display_name = job.get("input_file") or (os.path.basename(input_object) if input_object else None)
    output_format = job["output_format"]
    options = job.get("options", {})

    if not input_object or not display_name:
        print(f"[{WORKER_ID}] Job {job_id} no tiene archivo válido")
        return

    JOBS_IN_PROGRESS.inc()
    CURRENT_JOBS += 1
    
    try:
        # Actualizar estado
        update_job_status(job_id, {
            "status": "processing",
            "worker_id": WORKER_ID,
            "started_at": datetime.utcnow().isoformat(),
            "progress": 10
        })
        
        start_time = time.time()
        
        # Crear archivos temporales
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{get_file_extension(display_name)}") as tmp_input:
            input_path = tmp_input.name
            
            # Descargar de MinIO
            print(f"[{WORKER_ID}] Descargando {input_object}")
            minio.fget_object(BUCKET, input_object, input_path)
            input_size = os.path.getsize(input_path)
            
            update_job_status(job_id, {"progress": 30})
            
            # Determinar nombre de salida
            base_name = Path(display_name).stem or "output"
            output_file = f"{base_name}_converted.{output_format}"
            target_object = f"{owner}/{output_file}" if owner else output_file
            output_path = f"{tempfile.gettempdir()}/{output_file}"
            
            # Convertir
            print(f"[{WORKER_ID}] Convirtiendo a {output_format}")
            update_job_status(job_id, {"progress": 50})
            
            # Detectar tipo de archivo
            input_ext = get_file_extension(display_name)
            audio_formats = ["mp3", "flac", "wav", "aac", "ogg", "m4a"]
            video_formats = ["mp4", "avi", "mkv", "webm", "mov", "flv"]
            
            if output_format in audio_formats:
                convert_audio(input_path, output_path, output_format, options)
            elif output_format in video_formats:
                convert_video(input_path, output_path, output_format, options)
            else:
                raise Exception(f"Formato no soportado: {output_format}")
            
            update_job_status(job_id, {"progress": 80})
            
            # Subir resultado a MinIO
            print(f"[{WORKER_ID}] Subiendo {target_object}")
            output_size = os.path.getsize(output_path)
            
            with open(output_path, "rb") as f:
                minio.put_object(
                    BUCKET, target_object, f,
                    length=output_size,
                    content_type=f"video/{output_format}" if output_format in video_formats else f"audio/{output_format}"
                )
            
            # Calcular métricas
            duration = time.time() - start_time
            size_reduction = ((input_size - output_size) / input_size) * 100 if input_size > 0 else 0
            
            CONV_DURATION.observe(duration)
            FILE_SIZE_REDUCTION.observe(size_reduction)
            CONV_DONE.labels(status="success").inc()
            SUCCESS_COUNT += 1
            
            # Actualizar estado final
            update_job_status(job_id, {
                "status": "completed",
                "output_file": output_file,
                "output_object": target_object,
                "completed_at": datetime.utcnow().isoformat(),
                "progress": 100,
                "duration_seconds": round(duration, 2),
                "input_size_bytes": input_size,
                "output_size_bytes": output_size,
                "size_reduction_percent": round(size_reduction, 2)
            })
            
            print(f"[{WORKER_ID}] Job {job_id} completado en {duration:.2f}s")
            
            # Limpiar archivos temporales
            os.unlink(input_path)
            os.unlink(output_path)
            
    except Exception as e:
        error_msg = str(e)
        print(f"[{WORKER_ID}] Error en job {job_id}: {error_msg}")
        
        CONV_DONE.labels(status="failed").inc()
        FAILED_COUNT += 1
        
        update_job_status(job_id, {
            "status": "failed",
            "error": error_msg,
            "completed_at": datetime.utcnow().isoformat()
        })
    
    finally:
        JOBS_IN_PROGRESS.dec()
        CURRENT_JOBS = max(0, CURRENT_JOBS - 1)

def update_system_metrics():
    """Actualizar métricas del sistema"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        memory_mb = memory_info.used / 1024 / 1024

        CPU_LOAD.set(cpu_percent / 100)
        MEMORY_USAGE.set(memory_mb)  # MB
        publish_worker_status(cpu_percent, memory_mb)
    except Exception as e:
        print(f"Error actualizando métricas: {e}")

def main():
    print(f"[{WORKER_ID}] Iniciando worker...")
    print(f"[{WORKER_ID}] Métricas en puerto {METRICS_PORT}")
    print(f"[{WORKER_ID}] Cola específica: {WORKER_QUEUE}")
    
    # Iniciar servidor de métricas
    start_http_server(METRICS_PORT)
    
    print(f"[{WORKER_ID}] Esperando trabajos en cola...")
    
    while True:
        try:
            # Actualizar métricas del sistema
            update_system_metrics()
            
            # Prioridad 1: Verificar cola específica del worker (trabajos asignados)
            result = redis_client.blpop(WORKER_QUEUE, timeout=1)
            
            if result:
                _, job_id = result
                print(f"[{WORKER_ID}] ⭐ Trabajo ASIGNADO recibido: {job_id}")
                process_job(job_id)
                continue
            
            # Prioridad 2: Verificar cola general (si no hay trabajos asignados)
            result = redis_client.blpop(JOBS_QUEUE, timeout=5)
            
            if result:
                _, job_id = result
                print(f"[{WORKER_ID}] 📋 Trabajo de cola GENERAL recibido: {job_id}")
                process_job(job_id)
            
        except KeyboardInterrupt:
            print(f"[{WORKER_ID}] Deteniendo worker...")
            break
        except Exception as e:
            print(f"[{WORKER_ID}] Error en loop principal: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
