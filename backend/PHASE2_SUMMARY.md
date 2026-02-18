# ✅ FASE 2 - COMPLETADA

## 🎉 Estado: Implementación 100% Lista

El backend ahora incluye **procesamiento automático completo** de batallas de rap.

---

## 📊 Lo Que Se Ha Implementado

### 1. **Celery + Redis Task Queue** ✅

```python
# app/workers/celery_app.py
- Configuración de Celery
- Task serialization (JSON)
- Result backend (Redis)
- Prefetch settings optimizados
```

### 2. **5 Celery Tasks** ✅

| Task                     | Función                    | Input                 | Output                |
| ------------------------ | -------------------------- | --------------------- | --------------------- |
| `download_youtube_video` | Descarga de YouTube        | URL                   | Ruta audio            |
| `transcribe_audio`       | Transcripción con Whisper  | Ruta audio            | Texto + segmentos     |
| `separate_voices`        | Separación voces/beat      | Ruta audio            | Rutas voces separadas |
| `diarize_speakers`       | Identificación de speakers | Ruta audio            | Segmentos + speakers  |
| `process_pipeline`       | Orquestación               | battle_id, tipo, ruta | Batalla completa      |

### 3. **2 Nuevos Endpoints REST** ✅

```
POST /api/battles/youtube
  → Crear batalla desde YouTube URL
  → Async processing
  → Retorna inmediatamente con battle_id

POST /api/battles/upload
  → Crear batalla desde archivo local (MP3, WAV, MP4, etc)
  → Async processing
  → Retorna inmediatamente con battle_id

GET /api/battles/{id}/status
  → Monitorear progreso
  → Retorna status: pending|processing|completed|failed
```

### 4. **Pipeline Automático Completo** ✅

```
YouTube URL / Archivo Local
        ↓
FastAPI (instantáneo)
        ↓
Celery Worker (async)
  1️⃣  Download (yt-dlp)
  2️⃣  Transcribe (Whisper)
  3️⃣  Separate Voices (Demucs)
  4️⃣  Diarize (Pyannote)
  5️⃣  Analyze Verses (análisis de rimas)
        ↓
BD (versos + métricas)
        ↓
Frontend obtiene versos analizados
```

### 5. **Archivos Creados (Fase 2)**

```
app/workers/
  ├── celery_app.py               # Configuración Celery
  └── __init__.py

app/tasks/
  ├── download.py                 # yt-dlp + file save
  ├── transcription.py            # Whisper
  ├── voice_separation.py         # Demucs
  ├── diarization.py              # Pyannote
  ├── pipeline.py                 # Orquestador
  └── __init__.py

app/api/
  ├── youtube_router.py           # POST /battles/youtube
  ├── upload_router.py            # POST /battles/upload
  └── [updated __init__.py]

backend/
  ├── start_worker.py             # Script para Celery worker
  ├── PHASE2_GUIDE.md             # Documentación completa
  └── [updated requirements.txt]
```

---

## 🚀 Cómo Usar Fase 2

### Setup Inicial (Una sola vez)

```bash
cd backend

# 1. Instalar todas las dependencias
pip install -r requirements.txt

# 2. Instalar system dependencies
# macOS: brew install espeak-ng ffmpeg
# Linux: sudo apt install espeak-ng ffmpeg

# 3. Iniciar servicios
docker-compose up -d
```

### Ejecutar (Cada vez que quieras usar)

**Terminal 1 - Servidor FastAPI:**

```bash
python -m uvicorn app.main:app --reload
```

**Terminal 2 - Celery Worker:**

```bash
python start_worker.py
```

### Ejemplo: Procesar Batalla de YouTube

```bash
# 1. Enviar petición
curl -X POST "http://localhost:8000/api/battles/youtube?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ&title=Mi%20Batalla"

# Respuesta (instantánea):
# {"id": 1, "status": "processing", ...}

# 2. Monitorear progreso
curl "http://localhost:8000/api/battles/1/status"
# En Celery worker verás logs de transcripción, separación, etc.

# 3. Una vez completado, obtener versos
curl "http://localhost:8000/api/verses/battle/1"

# Respuesta: Versos con métricas de rimas calculadas automáticamente
```

---

## 📁 Estructura Actualizada

```
backend/
├── app/
│   ├── workers/                 # 🆕 Celery
│   │   ├── celery_app.py
│   │   └── __init__.py
│   ├── tasks/                   # 🆕 5 tasks
│   │   ├── download.py
│   │   ├── transcription.py
│   │   ├── voice_separation.py
│   │   ├── diarization.py
│   │   ├── pipeline.py
│   │   └── __init__.py
│   ├── api/
│   │   ├── youtube_router.py    # 🆕
│   │   ├── upload_router.py     # 🆕
│   │   └── [otros routers]
│   └── [... todo lo existente sigue igual ...]
│
├── start_worker.py               # 🆕 Script worker
├── PHASE2_GUIDE.md              # 🆕 Guía completa
├── QUICKSTART.md                # Actualizado
├── docker-compose.yml           # Sin cambios
└── [... resto del proyecto ...]
```

---

## 🔍 Tecnologías Nuevas

| Componente       | Librería        | Función                |
| ---------------- | --------------- | ---------------------- |
| Download         | yt-dlp          | Descargar de YouTube   |
| Transcription    | openai/whisper  | Audio a texto          |
| Voice Separation | facebook/demucs | Separar voces del beat |
| Speaker ID       | pyannote-audio  | Identificar speakers   |
| Task Queue       | celery          | Procesamiento async    |
| Message Broker   | redis           | Cola de mensajes       |

Todas ya incluidas en **requirements.txt**

---

## ⏱️ Timing Esperado

Para una batalla de **10 minutos**:

| Paso             | Tiempo       | Con GPU    |
| ---------------- | ------------ | ---------- |
| Descarga YouTube | 1-2 min      | 1-2 min    |
| Transcripción    | 3-5 min      | 30-60 seg  |
| Separación voces | 2-3 min      | 30-45 seg  |
| Diarización      | 1-2 min      | 20-30 seg  |
| Análisis rimas   | < 1 min      | < 1 min    |
| **TOTAL**        | **8-13 min** | **~3 min** |

---

## 📚 Documentación Nueva

1. **PHASE2_GUIDE.md** (LEER ESTO PRIMERO)
   - Setup paso a paso
   - Ejemplos de uso
   - Troubleshooting
   - Monitoreo con Flower

2. **start_worker.py**
   - Script para ejecutar Celery worker
   - Configuración automática
   - Error handling

3. **Updated QUICKSTART.md**
   - Incluye instrucciones de Fase 2

---

## ✅ Checklist Fase 2

- [x] Celery + Redis fully configured
- [x] Download task (yt-dlp wrapper)
- [x] Transcription task (Whisper)
- [x] Voice separation task (Demucs)
- [x] Diarization task (Pyannote)
- [x] Pipeline orchestration
- [x] YouTube endpoint (POST)
- [x] Upload endpoint (POST + file handling)
- [x] Status monitoring endpoint
- [x] Error handling + recovery
- [x] Logging completamente implementado
- [x] Documentation (PHASE2_GUIDE.md)
- [x] Worker startup script
- [x] requirements.txt updated
- [x] Backward compatible con Fase 1 (MVP)

---

## 💡 Características Importantes

### 1. **No Bloqueante (Non-blocking)**

```python
# FastAPI retorna inmediatamente
POST /battles/youtube → {"id": 1, "status": "processing"}

# Mientras tanto...
# Celery procesa en background sin bloquear el servidor
```

### 2. **Escalable**

```python
# start_worker.py usa:
--concurrency=2  # 2 tareas paralelas
--max-tasks-per-child=100  # Restart después de 100 tasks

# Fácil escalar a más workers/procesos
```

### 3. **Recuperación ante Errores**

```python
# Si algo falla en cualquier step:
# 1. Task logs el error
# 2. Battle status → "failed"
# 3. Usuario ve estado en GET /battles/{id}/status
```

### 4. **Retrocompatible**

```python
# MVP /api/battles/text sigue funcionando igual
# Fase 2 /api/battles/youtube es nuevo
# Sin conflictos, todo coexiste
```

---

## 🎯 Diferencia MVP vs Fase 2

| Característica    | MVP (Fase 1)                 | Fase 2                         |
| ----------------- | ---------------------------- | ------------------------------ |
| Input             | Texto transcrito manualmente | YouTube + archivos audio/video |
| Transcripción     | Manual                       | Automática (Whisper)           |
| Separación voces  | N/A                          | Automática (Demucs)            |
| Identificación MC | Manual                       | Automática (Pyannote)          |
| Segmentación      | Manual                       | Automática                     |
| Análisis rimas    | ✅                           | ✅ (mismo que MVP)             |
| Crowdsourcing     | ✅                           | ✅ (mismo que MVP)             |
| Processing        | Síncrono                     | **Asincrónico (Celery)**       |

---

## 🔧 Debugging & Monitoreo

### Ver logs de Celery Worker

```bash
# Terminal 2 (donde ejecutaste start_worker.py)
# Ya muestra logs automáticamente
```

### Monitorear tasks con Flower

```bash
pip install flower
celery -A app.workers.celery_app flower --port=5555
# Abre: http://localhost:5555
```

### Redis monitor

```bash
redis-cli
> MONITOR
# Ver todas las operaciones en Redis
```

---

## 🚨 Requisitos del Sistema

### Processor:

- GPU NVIDIA recomendada (1000x+ rápido)
- CPU multi-core mínimo

### Memory:

- RAM: 8GB minimum, 16GB recomendado
- Whisper model: ~2.9GB descarga inicial (se cachea)

### Storage:

- 50GB+ libre para audio temporal + Whisper cache

### Network:

- Descarga YouTube requiere conexión a internet
- Primera descarga de Whisper: ~1-2 Gbps

---

## 📝 Próximos Pasos (Fase 3)

Después de validar que Fase 2 funciona correctamente:

- [ ] Análisis semántico con LLM (Claude API)
  - Evaluación de punchlines
  - Evaluación de ingenio
  - Evaluación de respuesta al rival
- [ ] Calibración contra jueces humanos
- [ ] Score final integrado

Ver **NEXT_PHASES.md** en la raíz del proyecto.

---

## 🎓 Decisiones Arquitectónicas

### ¿Por qué Celery + Redis?

- Escalable horizontalmente
- Confiable (persistencia de tasks)
- Fácil de monitorear
- Estándar de la industria

### ¿Por qué tasks separadas en lugar de función grande?

- Cada task reutilizable
- Fácil debuggear
- Puede fallar una sin romper pipeline
- Fácil agregar retry logic

### ¿Por qué status polling en lugar de WebSocket?

- MVP simple
- WebSocket puede agregarse después en frontend
- Polling funciona para fase actual

---

## 📞 Support

### Si algo no funciona:

1. Leer **PHASE2_GUIDE.md** (sección Troubleshooting)
2. Verificar logs en Terminal 2 (Celery Worker)
3. Ejecutar `docker-compose ps` para verificar servicios
4. Verificar que Redis está corriendo: `redis-cli ping`

### Errores comunes:

```
"Connection refused" Redis
→ docker-compose up -d

"ModuleNotFoundError: demucs"
→ pip install -r requirements.txt

"Celery worker doesn't start"
→ python -c "from app.workers.celery_app import celery_app; print('OK')"
```

---

## 🎉 Resumen

**Fase 2 está completamente implementada y lista para usar.**

El sistema ahora puede procesar:

- ✅ YouTube URLs
- ✅ Archivos de audio local
- ✅ Archivos de video local
- ✅ Transcripción automática
- ✅ Separación de voces
- ✅ Identificación de speakers
- ✅ Análisis de rimas
- ✅ Crowdsourcing de calificaciones

**Todo asincrónico, escalable y con manejo de errores robusto.**

Next: Crear frontend web o implementar Fase 3 (LLM semántico).

---

Generated: 2024-01-15
Version: Fase 2 - Complete
