import os, time, random
from prometheus_client import Gauge, Counter, start_http_server

CPU_LOAD = Gauge("worker_cpu_load", "Carga del worker (demo)")
JOBS_IN_PROGRESS = Gauge("worker_jobs_in_progress", "Jobs en progreso")
CONV_DONE = Counter("worker_conversions_done_total", "Conversiones completadas")

def main():
    port = int(os.getenv("METRICS_PORT", "9101"))
    start_http_server(port)
    while True:
        # Señales dummy para probar el pipeline de métricas
        CPU_LOAD.set(random.uniform(0.05, 0.35))
        JOBS_IN_PROGRESS.set(random.randint(0, 2))
        time.sleep(5)

if __name__ == "__main__":
    main()
