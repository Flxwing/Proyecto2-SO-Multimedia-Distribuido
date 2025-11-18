# 🎬 Sistema Multimedia Distribuido

Plataforma completa de gestión multimedia con procesamiento distribuido, autenticación, conversión de formatos y monitoreo en tiempo real.

**🌐 Demo en vivo**: https://multimedia-distribuido.fly.dev

---

## 🚀 Inicio Rápido

### Opción 1: Usar la Versión en Producción (Recomendado)

Simplemente abre en tu navegador:

1. **Player**: [web/player.html](./web/player.html) *(apunta automáticamente a https://multimedia-distribuido.fly.dev)*
2. **Admin Dashboard**: [web/admin.html](./web/admin.html)

No necesitas instalar nada. El sistema ya está desplegado en Fly.io.

### Opción 2: Desarrollo Local con Docker

```powershell
git clone https://github.com/Flxwing/Proyecto2-SO-Multimedia-Distribuido.git
cd Proyecto2-SO-Multimedia-Distribuido
docker compose up -d
```

Abre `web/player.html` y cambia el endpoint en el badge a `http://localhost:8000`.

---

## ✨ Funcionalidades

✅ **Autenticación JWT** - Registro y login seguro  
✅ **Subida/Descarga** - Almacenamiento en MinIO (S3-compatible)  
✅ **Conversión Distribuida** - Workers FFmpeg con balanceo de carga  
✅ **Formatos Soportados**:
  - Audio: MP3, FLAC, WAV, AAC, OGG
  - Video: MP4, AVI, MKV, WEBM, MOV  
✅ **Compartir Públicamente** - Enlaces temporales con TTL configurable  
✅ **Player Multimedia** - Audio playlist + reproductor de video  
✅ **Dashboard de Monitoreo** - CPU, RAM, jobs en tiempo real (Chart.js)  
✅ **Métricas Prometheus** - Exportadas para Grafana

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                    Usuario (Frontend)                    │
│              player.html │ admin.html                    │
└────────────────┬────────────────────────────────────────┘
                 │ HTTPS
                 ▼
┌─────────────────────────────────────────────────────────┐
│                  API (FastAPI)                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │ /auth │ /media │ /convert │ /jobs │ /share      │  │
│  └──────────────────────────────────────────────────┘  │
└──┬──────────┬─────────────┬──────────────────────────┬─┘
   │          │             │                          │
   ▼          ▼             ▼                          ▼
┌─────┐  ┌─────────┐  ┌──────────┐           ┌──────────────┐
│Redis│  │  MinIO  │  │Worker A  │           │  Worker B    │
│Queue│  │ Storage │  │(FFmpeg)  │           │  (FFmpeg)    │
└─────┘  └─────────┘  └──────────┘           └──────────────┘
```

**Componentes**:
- **API**: Autenticación, gestión de archivos, enrutamiento de jobs
- **Workers**: Procesamiento paralelo de conversiones multimedia
- **Redis**: Cola de trabajos + estado de workers
- **MinIO**: Almacenamiento S3 de archivos multimedia
- **Prometheus + Grafana**: Monitoreo y visualización

---

## 📦 Despliegue en Producción

### Fly.io (Recomendado)

1. Instala Fly CLI:
   ```powershell
   iwr https://fly.io/install.ps1 -useb | iex
   ```

2. Login y despliega:
   ```powershell
   fly auth login
   fly apps create multimedia-distribuido
   fly volumes create media_data --region mia --size 10
   fly deploy
   ```

**Guía completa**: Ver [DEPLOY.md](./DEPLOY.md)

**Ventajas**:
- ✅ Free tier generoso (3 VMs, 3GB storage)
- ✅ HTTPS automático
- ✅ Zero-downtime deployments
- ✅ Sin limitaciones de túnel como ngrok

### Alternativas

- **Render.com**: `render.yaml` incluido
- **Railway.app**: Un clic desde GitHub
- **DigitalOcean**: $5/mes con App Platform

---

## 🎯 Requisitos del Proyecto Cumplidos

| # | Requisito | Estado | Detalles |
|---|-----------|--------|----------|
| 1 | **Arquitectura Distribuida** | ✅ | API + 2 Workers + Redis + MinIO |
| 2 | **Gestión de Procesos** | ✅ | Concurrencia con asyncio, colas Redis |
| 3 | **Monitoreo Dinámico** | ✅ | Dashboard Chart.js + métricas Prometheus |
| 4 | **Conversión Multimedia** | ✅ | FFmpeg: 5 formatos audio + 5 video |
| 5 | **Compartir Archivos** | ✅ | Enlaces públicos con TTL |
| 6 | **Interfaz de Usuario** | ✅ | Player moderno + Admin dashboard |
| 7 | **Documentación** | ✅ | README + DEPLOY + arquitectura |

**Peso total cumplido**: 100% según [rúbrica](./PROYECTO_INFO.md)

---

## 🧪 Testing

### API Endpoints

```powershell
# Health check
Invoke-RestMethod https://multimedia-distribuido.fly.dev/health

# Workers stats (público)
Invoke-RestMethod https://multimedia-distribuido.fly.dev/workers/stats

# Crear usuario
$body = @{username='test'; password='test1234'} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri https://multimedia-distribuido.fly.dev/auth/signup `
  -Body $body -ContentType 'application/json'
```

### Frontend Local

1. Abre `web/player.html`
2. Crea cuenta o inicia sesión
3. Sube un archivo MP3
4. Conviértelo a FLAC
5. Comparte el enlace resultante

---

## 📊 Monitoreo

### Prometheus (Local)
```
http://localhost:9090
```

Métricas expuestas:
- `api_requests_total`
- `worker_cpu_load`
- `worker_jobs_in_progress`
- `api_jobs_enqueued_total`

### Grafana (Local)
```
http://localhost:3000
```

Dashboards incluidos:
- Worker Performance
- Job Queue Stats
- API Request Rate

### Fly.io Dashboard
```powershell
fly dashboard
```

Monitoreo cloud con alertas.

---

## 🛠️ Desarrollo Local

### Requisitos
- Docker Desktop
- PowerShell 5.1+

### Levantar Servicios

```powershell
docker compose up -d
```

Servicios disponibles:
- API: http://localhost:8000
- MinIO Console: http://localhost:9001 (admin/admin12345)
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- Redis: localhost:6379

### Ver Logs

```powershell
docker compose logs -f api worker_a worker_b
```

### Rebuild

```powershell
docker compose build api worker_a worker_b
docker compose up -d
```

---

## 📁 Estructura del Proyecto

```
Proyecto2-SO-Multimedia-Distribuido/
├── api/
│   ├── main.py              # FastAPI endpoints
│   ├── Dockerfile
│   └── requirements.txt
├── worker/
│   ├── worker.py            # FFmpeg worker con métricas
│   ├── Dockerfile
│   └── requirements.txt
├── web/
│   ├── player.html          # UI principal
│   └── admin.html           # Dashboard monitoreo
├── monitoring/
│   └── prometheus.yml       # Configuración scraping
├── fly.toml                 # Config Fly.io
├── Dockerfile.flyio         # Build para producción
├── start-services.sh        # Script inicio multi-servicio
├── docker-compose.yml       # Orquestación local
├── DEPLOY.md                # Guía despliegue detallada
├── PROYECTO_INFO.md         # Requisitos y rúbrica
└── README.md                # Este archivo
```

---

## 🐛 Troubleshooting

### Frontend muestra "Unexpected token '<'"

**Causa**: Endpoint apunta a servidor caído.

**Solución**: Haz clic en el badge "API:" y verifica la URL.

### Conversiones fallan

**Logs**:
```powershell
docker compose logs worker_a
```

Verifica que FFmpeg esté instalado en el worker.

### Enlaces de compartir devuelven 404

**Causa**: `PUBLIC_BASE_URL` mal configurada.

**Solución**: En Fly.io se configura automáticamente. En local, verifica `docker-compose.yml`.

---

## 🎓 Tecnologías

- **Backend**: Python 3.11, FastAPI, Uvicorn
- **Workers**: FFmpeg, Prometheus Client, psutil
- **Storage**: MinIO (S3-compatible)
- **Queue**: Redis
- **Frontend**: HTML5, JavaScript (Vanilla), Chart.js
- **Monitoreo**: Prometheus, Grafana
- **Deploy**: Fly.io, Docker, Docker Compose

---

## 👥 Autores

- **Alonso** - Backend/Workers
- **Maikel** - Frontend/Player
- **Equipo** - Integración y despliegue

---

## 📝 Licencia

Proyecto académico para el curso de Sistemas Operativos, TEC Costa Rica.

---

## 🔗 Enlaces Útiles

- [Documentación Fly.io](https://fly.io/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [FFmpeg Formatos](https://ffmpeg.org/ffmpeg-formats.html)
- [Prometheus Metrics](https://prometheus.io/docs/concepts/metric_types/)

---

*Última actualización: 18 de noviembre de 2025*