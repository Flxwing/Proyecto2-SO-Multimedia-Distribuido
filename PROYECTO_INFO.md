# Plataforma Multimedia Distribuida - Información del Proyecto

## 📋 Información General

**Curso:** Sistemas Operativos  
**Proyecto:** Sistema Multimedia Distribuido  
**Fecha de inicio:** 10 de noviembre de 2025  
**Repositorio:** Proyecto2-SO-Multimedia-Distribuido

---

## 🎯 Motivación General

La creciente demanda por plataformas que permiten consumir y compartir contenido multimedia (audio, vídeo) en diversos entornos de red ha impulsado el desarrollo de sistemas distribuidos que gestionan múltiples usuarios, recursos limitados y datos intensivos. 

Servicios como **Spotify**, **YouTube** y **SoundCloud** han demostrado que la eficiencia operativa, la escalabilidad y la experiencia de usuario dependen en gran medida de cómo se gestionan los procesos, los archivos y los dispositivos en un sistema distribuido.

Este proyecto busca construir un sistema práctico que simule, en escala académica, las funcionalidades esenciales de estas plataformas, a partir de una arquitectura distribuida y una correcta gestión de procesos y recursos, integrando los principios fundamentales vistos en el Curso.

---

## 📝 Descripción General

Desarrollar un sistema multimedia distribuido que permita:

- ✅ **Reproducir** archivos de audio y vídeo en múltiples formatos (ej. MP3, FLAC, MP4)
- ✅ **Convertir** archivos multimedia entre distintos formatos (ej. de FLAC a MP3)
- ✅ **Reproducir** archivos de manera local o remota (desde servidores o nodos en la nube)
- ✅ **Compartir** archivos multimedia con otros usuarios conectados al sistema
- ✅ **Soportar** múltiples usuarios y sesiones concurrentes, controlando permisos y autenticación
- ✅ **Implementar** mecanismos de monitoreo y optimización dinámica de recursos entre nodos del sistema

---

## 🔧 Componentes Mínimos del Sistema

### 1. Gestión de Usuarios y Sesiones
- Inicio de sesión, autenticación y control de acceso
- Manejo de múltiples usuarios simultáneos

### 2. Reproducción de Contenido
- Reproducción local y remota de audio y vídeo
- Soporte para al menos **tres formatos** de archivos (tanto para audio como vídeo)

### 3. Conversión de Archivos
- Conversión entre formatos
- Énfasis en reducción de tamaño

### 4. Facilidad para Compartir Archivos
- Subida y descarga de archivos desde nodos en la nube o repos compartidos

### 5. Procesamiento Distribuido
- Al menos **dos nodos** ejecutando tareas específicas (conversión, reproducción, gestión de usuarios…)
- Monitoreo de CPU, RAM y uso de red en tiempo real
- Redistribución dinámica de tareas si un nodo se encuentra saturado

### 6. Dashboard de Monitoreo
- Interfaz visual que permita ver el estado de los nodos y las sesiones activas

### 7. Documentación
- Manual de usuario
- Documentación técnica (arquitectura, instrucciones de despliegue, API si aplica)

---

## 📚 Perspectiva desde los Temas del Curso

| Tema | Aplicación en el Proyecto |
|------|---------------------------|
| **Administración de procesos** | Concurrencia de tareas, control y planificación de procesos |
| **Comunicación entre procesos** | Transferencia de archivos, sockets o colas |
| **Administración de dispositivos** | Uso del sistema de archivos, lectura/escritura en disco y manejo de E/S |
| **Sistemas distribuidos** | Múltiples nodos, sincronización y coordinación |
| **Protección y seguridad** | Autenticación y control de accesos |
| **Administración de información** | Acceso a archivos distribuidos, formatos, recuperación y compartición |

---

## 📊 Rúbrica de Evaluación (Escala 0-5)

| # | Aspecto Evaluado | Peso | Descripción |
|---|------------------|------|-------------|
| 1 | **Implementación distribuida del sistema** | 25% | Evalúa el uso real de múltiples nodos, la cooperación entre ellos y el uso eficiente de recursos compartidos. **NOTA:** Este rubro parte de la concepción distribuida del Sistema. No se brindará valoración/calificación a implementaciones locales. |
| 2 | **Gestión de procesos y concurrencia** | 20% | Evalúa cómo se implementa la atención simultánea a múltiples solicitudes, conversiones, transmisiones y manejo de colas. |
| 3 | **Monitoreo y optimización dinámica de recursos** | 15% | Considera el uso de dashboards y mecanismos automáticos de redistribución de carga entre nodos (ej. balanceo basado en uso de CPU o memoria). |
| 4 | **Conversión y reproducción multimedia** | 10% | Evalúa la capacidad para reproducir archivos multimedia correctamente y convertir entre formatos con éxito. |
| 5 | **Compartición y descarga de archivos desde repos distribuidos** | 10% | Mide la funcionalidad del sistema para subir, acceder y compartir archivos entre nodos. |
| 6 | **Interfaz de usuario y experiencia (incluye el dashboard visual)** | 10% | Evalúa la usabilidad de las interfaces para el usuario, claridad del dashboard, facilidad para acceder al contenido. |
| 7 | **Documentación técnica y manual de usuario** | 10% | Considera la completitud de los diagramas, instrucciones de despliegue, descripciones de arquitectura, APIs y guía de uso clara. |

**Total: 100%**

---

## 🏗️ Arquitectura Actual del Proyecto

```
Proyecto2-SO-Multimedia-Distribuido/
├── api/                    # Nodo API (Gestión de usuarios, sesiones)
│   ├── Dockerfile
│   └── main.py
├── worker/                 # Nodo Worker (Conversión de archivos)
│   ├── Dockerfile
│   └── worker.py
├── web/                    # Interfaz de usuario
│   └── player.html
├── monitoring/             # Monitoreo del sistema
│   └── prometheus.yml
├── docker-compose.yml      # Orquestación de servicios
└── README.md
```

---

## ✅ Checklist de Requisitos

### Funcionalidades Core
- [ ] Autenticación de usuarios
- [ ] Manejo de sesiones concurrentes
- [ ] Reproducción de audio (MP3, FLAC, WAV)
- [ ] Reproducción de vídeo (MP4, AVI, MKV)
- [ ] Conversión entre formatos de audio
- [ ] Conversión entre formatos de vídeo
- [ ] Subida de archivos
- [ ] Descarga de archivos
- [ ] Compartir archivos entre usuarios

### Arquitectura Distribuida
- [ ] Mínimo 2 nodos operativos
- [ ] Comunicación entre nodos
- [ ] Distribución de tareas
- [ ] Balanceo de carga dinámico

### Monitoreo y Optimización
- [ ] Dashboard visual
- [ ] Monitoreo de CPU por nodo
- [ ] Monitoreo de RAM por nodo
- [ ] Monitoreo de uso de red
- [ ] Redistribución automática de tareas

### Documentación
- [ ] Manual de usuario
- [ ] Documentación técnica
- [ ] Diagramas de arquitectura
- [ ] Instrucciones de despliegue
- [ ] Documentación de API

---

## 🚀 Tecnologías Sugeridas

### Backend
- Python (FastAPI/Flask)
- Node.js (Express)
- Go

### Procesamiento Multimedia
- FFmpeg (conversión)
- GStreamer (streaming)

### Comunicación
- REST API
- WebSockets
- Message Queues (RabbitMQ, Redis)

### Monitoreo
- Prometheus
- Grafana
- Docker Stats

### Contenedores
- Docker
- Docker Compose
- Kubernetes (opcional)

---

## 📌 Notas Importantes

1. **Arquitectura Distribuida Obligatoria**: El proyecto DEBE implementarse de forma distribuida. No se aceptarán soluciones locales.

2. **Formatos Multimedia Mínimos**:
   - Audio: MP3, FLAC, WAV (mínimo 3)
   - Video: MP4, AVI, MKV (mínimo 3)

3. **Nodos Mínimos**: Al menos 2 nodos con funciones específicas y diferenciadas.

4. **Concurrencia**: El sistema debe manejar múltiples usuarios y operaciones simultáneas.

5. **Monitoreo en Tiempo Real**: Dashboard que muestre el estado actual del sistema.

---

## 🎯 Objetivos de Aprendizaje

- Comprender la arquitectura de sistemas distribuidos
- Implementar comunicación entre procesos
- Gestionar recursos compartidos
- Optimizar el rendimiento del sistema
- Implementar mecanismos de seguridad y autenticación
- Desarrollar interfaces de usuario efectivas
- Documentar sistemas complejos

---

## 📅 Plan de Desarrollo (Sugerido)

### Fase 1: Infraestructura Base
- Configuración de contenedores Docker
- Comunicación básica entre nodos
- Estructura de base de datos

### Fase 2: Funcionalidades Core
- Autenticación y gestión de usuarios
- Subida/descarga de archivos
- Reproducción básica

### Fase 3: Procesamiento Multimedia
- Conversión de formatos
- Optimización de archivos
- Streaming

### Fase 4: Monitoreo y Optimización
- Dashboard de monitoreo
- Métricas de recursos
- Balanceo de carga

### Fase 5: Pulido y Documentación
- Testing
- Documentación completa
- Manual de usuario

---

*Documento creado: 10 de noviembre de 2025*  
*Última actualización: 10 de noviembre de 2025*
