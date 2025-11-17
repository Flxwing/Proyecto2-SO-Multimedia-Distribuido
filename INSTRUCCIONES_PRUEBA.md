# 🚀 Instrucciones para Probar el Sistema de Conversión

## 📋 Requisitos Previos
- Docker y Docker Compose instalados
- Puertos disponibles: 8000, 9000, 9001, 9090, 3000, 6379

## 🔧 Paso 1: Reconstruir los Contenedores

Abre una terminal en el directorio del proyecto y ejecuta:

```bash
# Detener contenedores existentes (si los hay)
docker compose down

# Reconstruir las imágenes con los nuevos cambios
docker compose build

# Iniciar todos los servicios
docker compose up -d

# Ver los logs en tiempo real
docker compose logs -f
```

## 📊 Paso 2: Verificar que los Servicios Están Activos

```bash
# Ver estado de los contenedores
docker compose ps

# Deberías ver:
# - api (puerto 8000)
# - worker_a (puerto 9101)
# - worker_b (puerto 9102)
# - redis (puerto 6379)
# - minio (puertos 9000, 9001)
# - prometheus (puerto 9090)
# - grafana (puerto 3000)
# - node_exporter (puerto 9100)
```

## 🎬 Paso 3: Probar el Sistema

### 3.1 Abrir la Interfaz Web
Abre tu navegador en: http://localhost:8000/../../web/player.html

O simplemente abre el archivo `web/player.html` en tu navegador.

### 3.2 Subir un Archivo Multimedia

1. Click en "Seleccionar archivo"
2. Elige un archivo de audio (MP3, FLAC, WAV) o video (MP4, AVI, MKV)
3. Click en "Subir"
4. Espera confirmación "Subido ✅"

### 3.3 Convertir el Archivo

1. En la lista de archivos, haz click en el botón "🔄 Convertir" del archivo que subiste
2. Selecciona el formato de salida deseado:
   - **Audio**: MP3, FLAC, WAV, AAC, OGG
   - **Video**: MP4, AVI, MKV, WEBM, MOV
3. Click en "Convertir"
4. Verás el trabajo aparecer en la sección "Trabajos de Conversión"

### 3.4 Monitorear el Progreso

- **Estadísticas de Cola**: Muestra trabajos en cola, procesando, completados y fallidos
- **Trabajos de Conversión**: Lista todos los trabajos con su estado
  - **Pending** (amarillo): En cola esperando
  - **Processing** (azul): Siendo procesado por un worker
  - **Completed** (verde): Completado exitosamente
  - **Failed** (rojo): Falló por algún error

### 3.5 Descargar/Reproducir el Archivo Convertido

Cuando el estado sea "Completed":
1. Aparecerá un botón "⬇️ Descargar"
2. Click para reproducir el archivo convertido
3. También puedes verlo en la lista de archivos

## 🧪 Casos de Prueba Recomendados

### Prueba 1: Conversión de Audio
```
1. Subir archivo: cancion.mp3
2. Convertir a: FLAC (audio sin pérdida)
3. Verificar: Mayor tamaño pero mejor calidad
4. Convertir de nuevo a: MP3
5. Verificar: Reducción de tamaño
```

### Prueba 2: Conversión de Video
```
1. Subir archivo: video.mp4
2. Convertir a: AVI
3. Verificar: Compatibilidad con diferentes formatos
4. Convertir a: WEBM (optimizado para web)
5. Verificar: Reducción de tamaño
```

### Prueba 3: Carga Distribuida
```
1. Subir múltiples archivos (3-5)
2. Solicitar conversión de todos simultáneamente
3. Observar en los logs cómo worker_a y worker_b se distribuyen el trabajo
4. Comando: docker compose logs -f worker_a worker_b
```

### Prueba 4: Monitoreo
```
1. Mientras se procesan conversiones, abrir:
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000 (admin/admin)
2. Buscar métricas:
   - worker_cpu_load
   - worker_conversions_done_total
   - worker_conversion_duration_seconds
   - api_requests_total
```

## 📈 Ver Métricas en Prometheus

1. Abre http://localhost:9090
2. En la barra de búsqueda, escribe estas métricas:
   ```
   worker_conversions_done_total
   worker_cpu_load
   worker_memory_usage_mb
   worker_jobs_in_progress
   worker_conversion_duration_seconds
   api_requests_total
   ```
3. Click en "Graph" para ver gráficos

## 📊 Configurar Dashboard en Grafana

1. Abre http://localhost:3000
2. Login: admin / admin (cambiar password si pide)
3. Add Data Source → Prometheus
   - URL: http://prometheus:9090
   - Click "Save & Test"
4. Create Dashboard → Add Visualization
5. Agregar métricas de workers y API

## 🔍 Verificar Logs de Workers

```bash
# Ver logs del worker A
docker compose logs -f worker_a

# Ver logs del worker B
docker compose logs -f worker_b

# Deberías ver mensajes como:
# [worker_a] Procesando job <job-id>
# [worker_a] Descargando archivo.mp3
# [worker_a] Convirtiendo a flac
# [worker_a] Subiendo archivo_converted.flac
# [worker_a] Job completado en 15.32s
```

## 🔧 Verificar Cola de Redis

```bash
# Conectarse a Redis
docker compose exec redis redis-cli

# Ver longitud de la cola
LLEN conversion:queue

# Ver todos los jobs
KEYS job:status:*

# Ver detalles de un job específico
GET job:status:<job-id>

# Salir
exit
```

## 🐛 Solución de Problemas

### Error: "Archivo no encontrado"
- Verifica que el archivo se haya subido correctamente a MinIO
- Abre http://localhost:9001 (MinIO Console)
- Login: admin / admin12345
- Verifica que el bucket "media" tenga tus archivos

### Error: Workers no procesan trabajos
```bash
# Verificar que los workers estén corriendo
docker compose ps

# Ver logs de errores
docker compose logs worker_a worker_b

# Reiniciar workers
docker compose restart worker_a worker_b
```

### Error: Conversión falla
- Verifica los logs del worker para ver el error de FFmpeg
- Asegúrate de que el formato de entrada sea válido
- Algunos formatos requieren códecs específicos

### Puerto 8000 ocupado
```bash
# Cambiar puerto en docker-compose.yml
# De: "8000:8000"
# A:  "8080:8000"
# Luego usar http://localhost:8080
```

## 📸 Screenshots Esperados

1. **Interfaz Web**: Debe mostrar todos los paneles (subir, archivos, conversión, estadísticas, trabajos, reproductor)
2. **Lista de Archivos**: Cada archivo con botones "Reproducir" y "Convertir"
3. **Trabajos en Proceso**: Barra de progreso azul mostrando 10%, 30%, 50%, 80%, 100%
4. **Trabajos Completados**: Estado verde con botón de descarga y métricas (duración, reducción de tamaño)
5. **Estadísticas**: Cards mostrando números actualizados cada 3 segundos

## ✅ Criterios de Éxito

- [ ] Puedes subir archivos multimedia
- [ ] Puedes reproducir archivos en el navegador
- [ ] Puedes solicitar conversiones de formato
- [ ] Los workers procesan las conversiones correctamente
- [ ] El estado de los trabajos se actualiza en tiempo real
- [ ] Las métricas de Prometheus muestran datos reales
- [ ] Ambos workers (worker_a y worker_b) procesan trabajos
- [ ] Los archivos convertidos se pueden descargar
- [ ] Las estadísticas de cola se actualizan correctamente
- [ ] El sistema maneja múltiples conversiones simultáneas

## 🎯 Próximos Pasos

Una vez que el sistema funcione correctamente:

1. **Fase 2**: Implementar autenticación de usuarios
2. **Fase 3**: Agregar balanceo de carga inteligente
3. **Fase 4**: Crear dashboard personalizado de monitoreo
4. **Fase 5**: Documentación completa y testing

---

**Última actualización**: 10 de noviembre de 2025
