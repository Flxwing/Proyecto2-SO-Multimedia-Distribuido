# 🧪 GUÍA DE PRUEBAS PASO A PASO

## ✅ ESTADO ACTUAL
Tu sistema está corriendo y la interfaz web está abierta. ¡Vamos a probarlo!

---

## 🎯 PRUEBA 1: SUBIR Y CONVERTIR UN ARCHIVO (5 minutos)

### **PASO 1: Subir el Archivo de Prueba** 📤

1. **En la interfaz web**, ve a la sección **"📤 Subir Archivo"**

2. **Click en "Seleccionar archivo"**

3. **Navega a la carpeta**:
   ```
   D:\TEC\Sistemas Operativos\Proyecto2-SO-Multimedia-Distribuido\test-files\
   ```

4. **Selecciona el archivo**: `test-audio.mp3`

5. **Click en el botón "Subir"**

6. **DEBERÍAS VER**:
   - ✅ Mensaje "Subido ✅" aparece
   - ✅ El botón cambia de "Subiendo..." a "Subir" de nuevo

---

### **PASO 2: Verificar que el Archivo Está en la Lista** 📋

1. **En la sección "🎵 Archivos Multimedia"**

2. **Click en "Actualizar lista"**

3. **DEBERÍAS VER**:
   - ✅ El archivo `test-audio.mp3` aparece en la lista
   - ✅ Tiene dos botones: "▶️ Reproducir" y "🔄 Convertir"

4. **PRUEBA REPRODUCIR** (opcional):
   - Click en "▶️ Reproducir"
   - Deberías escuchar un tono de 440Hz por 5 segundos

---

### **PASO 3: Solicitar Conversión** 🔄

1. **Click en el botón "🔄 Convertir"** del archivo `test-audio.mp3`

2. **DEBERÍAS VER**:
   - ✅ Se expande un formulario mostrando:
     - "Archivo: test-audio.mp3"
     - Selector de formato de salida
     - Botones "Convertir" y "Cancelar"

3. **En el selector "Formato de salida"**, selecciona: **FLAC**
   - (FLAC es audio sin pérdida, el archivo será más grande pero mejor calidad)

4. **Click en el botón "Convertir"**

5. **DEBERÍAS VER**:
   - ✅ Alerta: "✅ Conversión solicitada! Job ID: [un-id-largo]"
   - ✅ El formulario se cierra
   - ✅ La sección "Trabajos de Conversión" se actualiza automáticamente

---

### **PASO 4: Monitorear el Progreso** 📊

**Observa la sección "📊 Estadísticas de Cola"**:

1. **Primero verás**:
   - "En Cola: 1" (el trabajo está esperando)
   - Los demás en 0

2. **Luego (1-2 segundos)**:
   - "Procesando: 1" (un worker lo tomó)
   - "En Cola: 0"

3. **Finalmente (5-15 segundos)**:
   - "Completados: 1"
   - "Procesando: 0"

**Observa la sección "📋 Trabajos de Conversión"**:

1. **Estado inicial**: 
   ```
   test-audio.mp3 → FLAC
   Status: PENDING (amarillo)
   Job ID: xxx-xxx-xxx
   ```

2. **Cuando empiece a procesar**:
   ```
   test-audio.mp3 → FLAC
   Status: PROCESSING (azul)
   Worker: worker_a (o worker_b)
   [Barra de progreso: 10% → 30% → 50% → 80% → 100%]
   ```

3. **Cuando termine**:
   ```
   test-audio.mp3 → FLAC
   Status: COMPLETED (verde)
   Worker: worker_a
   Duración: ~8.5s
   Reducción: -150% (FLAC es más grande que MP3)
   [Botón: ⬇️ Descargar]
   ```

---

### **PASO 5: Descargar y Verificar el Resultado** ✅

1. **Click en el botón "⬇️ Descargar"**

2. **DEBERÍAS VER**:
   - ✅ Se abre el reproductor en la sección "▶️ Reproductor"
   - ✅ Muestra un reproductor de audio
   - ✅ Puedes reproducir el archivo convertido

3. **Verifica en la lista de archivos**:
   - Click "Actualizar lista" en "🎵 Archivos Multimedia"
   - Deberías ver DOS archivos ahora:
     - `test-audio.mp3` (original)
     - `test-audio_converted.flac` (resultado)

---

## 🎯 PRUEBA 2: SISTEMA DISTRIBUIDO (Múltiples Conversiones)

### **Objetivo**: Verificar que los 2 workers trabajan en paralelo

1. **Sube el mismo archivo 3 veces más** (renómbralo: test1.mp3, test2.mp3, test3.mp3)
   - O usa archivos diferentes si los tienes

2. **Solicita conversión de TODOS simultáneamente**:
   - test-audio.mp3 → WAV
   - test1.mp3 → AAC
   - test2.mp3 → OGG

3. **OBSERVA**: 
   - ✅ "Procesando: 2" (ambos workers trabajando)
   - ✅ En los trabajos verás:
     - Uno dice "Worker: worker_a"
     - Otro dice "Worker: worker_b"
   - ✅ Se procesan 2 a la vez, el tercero espera

---

## 🎯 PRUEBA 3: VER LOGS EN TIEMPO REAL

Abre PowerShell y ejecuta:

```powershell
docker compose logs -f worker_a worker_b
```

**DEBERÍAS VER** (mientras procesas conversiones):

```
worker_a  | [worker_a] Procesando job abc-123-def
worker_a  | [worker_a] Descargando test-audio.mp3
worker_a  | [worker_a] Convirtiendo a flac
worker_a  | [worker_a] Subiendo test-audio_converted.flac
worker_a  | [worker_a] Job abc-123-def completado en 8.34s

worker_b  | [worker_b] Procesando job xyz-789-ghi
worker_b  | [worker_b] Descargando test1.mp3
...
```

Presiona `Ctrl+C` para salir.

---

## 🎯 PRUEBA 4: VERIFICAR MÉTRICAS EN PROMETHEUS

1. **Abre en tu navegador**: http://localhost:9090

2. **En la barra de búsqueda**, escribe: `worker_conversions_done_total`

3. **Click en "Execute"**

4. **DEBERÍAS VER**:
   ```
   worker_conversions_done_total{status="success"} = 1 (o más)
   ```

5. **Click en la pestaña "Graph"** para ver gráfico

6. **Prueba otras métricas**:
   - `worker_cpu_load` - CPU de los workers
   - `worker_conversion_duration_seconds` - Tiempo de conversión
   - `api_requests_total` - Requests a la API

---

## 🎯 PRUEBA 5: VER ARCHIVOS EN MINIO

1. **Abre**: http://localhost:9001

2. **Login**:
   - Username: `admin`
   - Password: `admin12345`

3. **Click en "Buckets"** → **"media"**

4. **DEBERÍAS VER**:
   - ✅ `test-audio.mp3`
   - ✅ `test-audio_converted.flac`
   - ✅ Todos los archivos que hayas subido/convertido

5. **Puedes**:
   - Descargar archivos directamente
   - Ver tamaño, fecha, etc.

---

## ✅ CHECKLIST DE VERIFICACIÓN

Marca lo que funciona:

### Funcionalidades Básicas
- [ ] ✅ Subir archivos funciona
- [ ] ✅ Archivos aparecen en la lista
- [ ] ✅ Reproducir archivos funciona
- [ ] ✅ Solicitar conversión funciona
- [ ] ✅ Ver jobs en la lista
- [ ] ✅ Estadísticas se actualizan automáticamente

### Conversión
- [ ] ✅ Estado cambia: PENDING → PROCESSING → COMPLETED
- [ ] ✅ Barra de progreso se muestra y avanza
- [ ] ✅ Aparece el worker que procesó (worker_a o worker_b)
- [ ] ✅ Se muestra duración en segundos
- [ ] ✅ Se muestra reducción de tamaño
- [ ] ✅ Botón de descarga aparece
- [ ] ✅ Archivo convertido se puede reproducir
- [ ] ✅ Archivo convertido aparece en lista

### Sistema Distribuido
- [ ] ✅ Múltiples conversiones en paralelo (2 a la vez)
- [ ] ✅ Worker A procesa trabajos
- [ ] ✅ Worker B procesa trabajos
- [ ] ✅ Cola funciona correctamente
- [ ] ✅ Logs muestran actividad real

### Monitoreo
- [ ] ✅ Prometheus muestra métricas
- [ ] ✅ MinIO tiene los archivos
- [ ] ✅ Estadísticas son precisas

---

## 🐛 SI ALGO NO FUNCIONA

### Problema: "Error al subir archivo"
```powershell
# Ver logs de API
docker compose logs api

# Verificar MinIO
docker compose logs minio
```

### Problema: "Conversión se queda en PENDING"
```powershell
# Ver logs de workers
docker compose logs worker_a worker_b

# Verificar Redis
docker exec redis redis-cli LLEN conversion:queue
```

### Problema: "No aparece el archivo convertido"
```powershell
# Listar archivos en MinIO
docker exec api python -c "from minio import Minio; m=Minio('minio:9000', access_key='admin', secret_key='admin12345', secure=False); print([o.object_name for o in m.list_objects('media')])"
```

---

## 🎉 SI TODO FUNCIONA

¡FELICIDADES! Tu sistema está completamente operativo:

- ✅ Arquitectura distribuida real
- ✅ Cola de trabajos funcional
- ✅ Conversión multimedia exitosa
- ✅ Monitoreo en tiempo real
- ✅ 2 workers procesando en paralelo

**Puntuación estimada: ~75/100** 🎯

---

## 📸 CAPTURAS RECOMENDADAS

Para tu documentación/presentación, toma screenshots de:

1. Interfaz web con conversión completada
2. Estadísticas mostrando múltiples trabajos
3. Logs de workers procesando
4. Métricas en Prometheus
5. Archivos en MinIO Console
6. Docker Desktop mostrando los 8 contenedores

---

## 🚀 SIGUIENTE PASO

Una vez que TODAS las pruebas pasen, podemos:

1. **Implementar autenticación de usuarios**
2. **Agregar balanceo de carga inteligente**
3. **Crear dashboard personalizado**
4. **Documentación completa del proyecto**

---

**¡Empieza con la PRUEBA 1 y dime qué tal te va!** 🚀

Si algo falla, dime exactamente qué error ves y te ayudo a solucionarlo.
