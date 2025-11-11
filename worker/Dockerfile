FROM python:3.11-slim
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN pip install --no-cache-dir prometheus-client redis minio psutil
COPY worker.py .
CMD ["python","worker.py"]
