from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
import os

app = FastAPI(title="Multimedia API")

REQUESTS = Counter("api_requests_total", "Total de requests")
ACTIVE_SESSIONS = Gauge("active_sessions", "Sesiones activas")

@app.get("/health")
def health():
    REQUESTS.inc()
    return {"ok": True}

@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
