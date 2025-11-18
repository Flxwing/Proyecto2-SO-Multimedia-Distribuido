# 🚀 Despliegue en Fly.io - Guía Paso a Paso

## 📋 Requisitos

1. Cuenta gratuita en [fly.io](https://fly.io)
2. CLI de Fly instalado
3. Docker Desktop corriendo (opcional para testing local)

---

## 🔧 Instalación de Fly CLI

### Windows (PowerShell)
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

### Linux/Mac
```bash
curl -L https://fly.io/install.sh | sh
```

Verifica instalación:
```powershell
fly version
```

---

## 🎯 Pasos de Despliegue

### 1. Login en Fly.io

```powershell
fly auth login
```

Esto abrirá tu navegador para autenticarte.

### 2. Crear la Aplicación

Desde la raíz del proyecto:

```powershell
cd "d:\TEC\Sistemas Operativos\Proyecto2-SO-Multimedia-Distribuido"
fly apps create multimedia-distribuido
```

**Nota**: Si el nombre ya está tomado, usa `multimedia-distribuido-{tu-inicial}` (ej: `multimedia-distribuido-am`)

### 3. Crear Volumen Persistente

Para almacenar archivos de MinIO y Redis:

```powershell
fly volumes create media_data --region mia --size 10
```

- `mia` = Miami (más cercano a Costa Rica)
- Otras regiones: `iad` (Virginia), `gru` (São Paulo)

### 4. Configurar Secretos (Opcional)

Si quieres cambiar las credenciales por defecto:

```powershell
fly secrets set MINIO_ROOT_USER=admin MINIO_ROOT_PASSWORD=tu_password_seguro
```

### 5. Desplegar la Aplicación

```powershell
fly deploy
```

Este comando:
1. Construye la imagen Docker usando `Dockerfile.flyio`
2. Sube la imagen a Fly.io
3. Despliega en la región seleccionada
4. Asigna URL automática: `https://multimedia-distribuido.fly.dev`

**Tiempo estimado**: 3-5 minutos

### 6. Verificar Despliegue

```powershell
fly status
```

Deberías ver:

```
Machines
PROCESS ID              VERSION REGION  STATE   ROLE    CHECKS  LAST UPDATED
app     148ed4c8e45d89  1       mia     started                 2m ago
```

### 7. Ver Logs en Tiempo Real

```powershell
fly logs
```

---

## 🌐 Acceder al Sistema

Una vez desplegado, abre:

### Player
```
https://multimedia-distribuido.fly.dev
```

O abre localmente `web/player.html` (ya apunta a la URL de producción).

### Admin Dashboard
Abre `web/admin.html` localmente (configurado para apuntar a Fly.io).

### APIs
- **Health**: https://multimedia-distribuido.fly.dev/health
- **Workers Stats**: https://multimedia-distribuido.fly.dev/workers/stats
- **Docs**: https://multimedia-distribuido.fly.dev/docs

---

## 🔄 Actualizar la Aplicación

Después de hacer cambios en el código:

```powershell
fly deploy
```

Fly.io hace **zero-downtime deployment** automáticamente.

---

## 📊 Monitoreo

### Ver métricas de recursos

```powershell
fly dashboard
```

Abre el dashboard web con:
- CPU/RAM usage
- Request rate
- Logs en vivo

### SSH a la máquina

```powershell
fly ssh console
```

Útil para debugging directo.

### Ver logs de servicios internos

```powershell
fly ssh console -C "tail -f /tmp/worker_a.log"
fly ssh console -C "tail -f /tmp/minio.log"
```

---

## 🛠️ Comandos Útiles

### Escalar la aplicación

```powershell
# Más instancias (mejor performance, mayor costo)
fly scale count 2

# Más CPU/RAM por instancia
fly scale vm shared-cpu-2x --memory 1024
```

### Reiniciar la app

```powershell
fly apps restart multimedia-distribuido
```

### Destruir la app (cuidado!)

```powershell
fly apps destroy multimedia-distribuido
```

---

## 💰 Costos (Free Tier)

Fly.io incluye **gratis**:
- 3 VMs compartidas (256MB RAM cada una)
- 3GB volumen persistente
- 160GB transferencia/mes

**Para este proyecto**: Cabe perfectamente en el free tier si usas 1 VM.

Si necesitas más recursos:
- VM con 512MB RAM: ~$2/mes
- Volumen 10GB: ~$0.15/mes

---

## 🐛 Troubleshooting

### Error: "no space left on device"

El volumen está lleno. Aumenta el tamaño:

```powershell
fly volumes extend media_data --size 15
```

### Error: "health checks failing"

Revisa logs:

```powershell
fly logs
```

Común: Redis/MinIO no arrancan a tiempo. Aumenta el `grace_period` en `fly.toml`.

### Error: "build failed"

Verifica que `Dockerfile.flyio` esté en la raíz:

```powershell
ls Dockerfile.flyio
```

### La app se detiene sola

Por defecto, Fly.io para VMs sin tráfico. Desactívalo en `fly.toml`:

```toml
[http_service]
  auto_stop_machines = false
  auto_start_machines = true
  min_machines_running = 1
```

---

## 🔐 Seguridad

### Cambiar credenciales de MinIO

```powershell
fly secrets set MINIO_ROOT_USER=nuevousuario MINIO_ROOT_PASSWORD=nuevapassword
fly deploy
```

### Habilitar CORS solo para tu dominio

Edita `api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tu-dominio.com"],  # En vez de ["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📈 Próximos Pasos

1. **Configurar dominio custom** (opcional):
   ```powershell
   fly certs add tu-dominio.com
   ```

2. **Añadir PostgreSQL** para usuarios (en vez de Redis):
   ```powershell
   fly postgres create
   ```

3. **Configurar CI/CD con GitHub Actions**:
   - Cada push a `main` despliega automáticamente

---

## 🎓 Ventajas vs Alternativas

| Servicio | Costo Mensual | Docker Support | Límite Free |
|----------|---------------|----------------|-------------|
| **Fly.io** | $0 | ✅ Nativo | 3 VMs, 3GB storage |
| Render | $0 | ✅ | 750hrs/mes, sin storage |
| Railway | $5 mínimo | ✅ | $5 crédito/mes |
| Heroku | $7+ | ❌ | Sin free tier |
| DigitalOcean | $5+ | ✅ | Sin free tier |

**Conclusión**: Fly.io es la mejor opción para este proyecto académico.

---

## ✅ Checklist de Despliegue

- [ ] CLI de Fly instalado
- [ ] Login en Fly.io exitoso
- [ ] App creada con `fly apps create`
- [ ] Volumen persistente creado
- [ ] `fly deploy` ejecutado sin errores
- [ ] `fly status` muestra VM corriendo
- [ ] Health check pasa: https://multimedia-distribuido.fly.dev/health
- [ ] Frontend actualizado con URL de producción
- [ ] Probado login + subida de archivo
- [ ] Probado conversión de archivos
- [ ] Probado compartir enlace público

---

**Documentación oficial**: https://fly.io/docs  
**Comunidad**: https://community.fly.io

---

*Última actualización: 18 de noviembre de 2025*
