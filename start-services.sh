#!/bin/bash
set -e

# Detectar PUBLIC_BASE_URL automáticamente desde FLY_APP_NAME
if [ -n "$FLY_APP_NAME" ]; then
    export PUBLIC_BASE_URL="https://${FLY_APP_NAME}.fly.dev"
else
    export PUBLIC_BASE_URL="${PUBLIC_BASE_URL:-http://localhost:8000}"
fi

echo "🚀 Iniciando servicios en Fly.io..."
echo "📌 PUBLIC_BASE_URL: $PUBLIC_BASE_URL"

# Crear directorios necesarios en el volumen persistente
mkdir -p /data/redis /data/minio

# Iniciar Redis en segundo plano con persistencia
echo "▶️  Iniciando Redis..."
redis-server --daemonize yes \
    --bind 0.0.0.0 \
    --port 6379 \
    --dir /data/redis \
    --dbfilename dump.rdb \
    --save 60 1 \
    --appendonly yes \
    --appendfilename appendonly.aof

# Iniciar MinIO en segundo plano
echo "▶️  Iniciando MinIO..."
MINIO_ROOT_USER=admin MINIO_ROOT_PASSWORD=admin12345 \
    minio server /data/minio --address 0.0.0.0:9000 --console-address :9001 > /tmp/minio.log 2>&1 &

# Esperar a que Redis y MinIO estén listos
echo "⏳ Esperando servicios..."
sleep 5

# Crear bucket en MinIO si no existe
echo "📦 Verificando bucket MinIO..."
# Esperar un poco más para MinIO
sleep 3

# Iniciar workers en segundo plano
echo "▶️  Iniciando Workers..."
cd /app/worker
WORKER_ID=worker_a METRICS_PORT=9101 python worker.py > /tmp/worker_a.log 2>&1 &
WORKER_ID=worker_b METRICS_PORT=9102 python worker.py > /tmp/worker_b.log 2>&1 &

# Iniciar API en primer plano
echo "▶️  Iniciando API en puerto 8000..."
cd /app/api
exec uvicorn main:app --host 0.0.0.0 --port 8000 --log-level info
