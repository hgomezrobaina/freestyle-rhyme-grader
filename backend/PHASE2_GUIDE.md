# FASE 2 - Guía de Instalación y Uso

## ¿Qué es Fase 2?

Fase 2 añade procesamiento automático de audio:

✅ **Descarga de YouTube** - Descargar directamente desde URLs
✅ **Transcripción** - Convertir audio a texto con Whisper
✅ **Separación de Voces** - Aislar voces del beat/ruido con Demucs
✅ **Diarización** - Identificar quién es MC1 vs MC2
✅ **Pipeline Automático** - Todo ejecutado asincronamente con Celery

## Instalación Rápida

### 1. Instalar Dependencias Adicionales

```bash
cd backend
pip install -r requirements.txt

# Sistema: espeak-ng (necesario para phonemizer)
# macOS:
brew install espeak-ng ffmpeg

# Linux:
sudo apt-get install espeak-ng ffmpeg

# Windows: Descargar desde https://github.com/espeak-ng/espeak-ng/releases
```

### 2. Verificar Redis está Corriendo

```bash
# La instancia de Redis debe estar corriendo (de docker-compose)
docker-compose ps

# Si no está corriendo:
docker-compose up -d
```

### 3. Iniciar el Servidor FastAPI

En **Terminal 1**:

```bash
python -m uvicorn app.main:app --reload
```

Servidor disponible en: **http://localhost:8000**

### 4. Iniciar Celery Worker

En **Terminal 2** (nueva):

```bash
python start_worker.py
```

Deberías ver:

```
Starting Celery Worker...
Make sure Redis is running: docker-compose up -d

 ---------- celery@hostname v5.3.0 (eminent)
 ---------- ... worker@hostname ready.
```

## Cómo Usar - Endpoints Nuevos

### Crear Batalla desde YouTube

```bash
curl -X POST "http://localhost:8000/api/battles/youtube?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ&title=Mi%20Batalla" \
  -H "accept: application/json"
```

Response (inmediato):

```json
{
  "id": 1,
  "title": "Mi Batalla",
  "status": "processing",
  "source_type": "youtube",
  "created_at": "2024-01-15T..."
}
```

### Subir Archivo Local (MP3, WAV, MP4, etc.)

```bash
curl -X POST "http://localhost:8000/api/battles/upload?title=Mi%20Batalla" \
  -F "file=@/path/to/battle.mp3" \
  -H "accept: application/json"
```

Response:

```json
{
  "id": 2,
  "title": "Mi Batalla",
  "status": "processing",
  "source_type": "upload"
}
```

### Monitorear Progreso

Mientras se procesa, puedes consultar el estado:

```bash
curl "http://localhost:8000/api/battles/1/status"
```

Response:

```json
{
  "id": 1,
  "status": "processing",
  "progress_message": "Processing audio...",
  "verses_count": 0
}
```

Una vez completado:

```json
{
  "id": 1,
  "status": "completed",
  "progress_message": "Completed!",
  "verses_count": 5
}
```

### Ver Versos Analizados

Una vez completado:

```bash
curl "http://localhost:8000/api/verses/battle/1"
```

Response (mismo que MVP + búsqueda automática):

```json
[
  {
    "id": 1,
    "verse_number": 1,
    "speaker": "MC1",
    "text": "Yo vengo de la calle...",
    "rhyme_metric": {
      "rhyme_density": 0.35,
      "multisyllabic_ratio": 0.25,
      "internal_rhymes_count": 2
    }
  }
]
```

## Cómo Funciona - Pipeline Interno

```
Usuario sube YouTube/Archivo
        ↓
FastAPI crea Battle (status=processing)
        ↓
Celery Worker recibe task
        ↓
1️⃣  Descargar video (yt-dlp) o verificar archivo
        ↓
2️⃣  Transcribir audio (Whisper) → obtiene el texto completo
        ↓
3️⃣  Separar voces (Demucs) → aísla voces del beat
        ↓
4️⃣  Diarizar (Pyannote) → identifica MC1 vs MC2
        ↓
5️⃣  Segmentar versos → divide por cambios de speaker
        ↓
6️⃣  Analizar rimas → calcula métricas para cada verso
        ↓
Guardar en BD → status=completed
        ↓
Frontend obtiene versos con métricas listas
```

## Estado de las Tasks

Mientras se procesa, puedes ver logs en la **Terminal 2** (Celery Worker):

```
[2024-01-15 10:30:00,000: INFO/MainProcess] Task... started
[2024-01-15 10:30:15,500: INFO/Worker] Downloading from YouTube...
[2024-01-15 10:31:00,000: INFO/Worker] Download completed
[2024-01-15 10:31:05,000: INFO/Worker] Loading Whisper model...
[2024-01-15 10:32:30,000: INFO/Worker] Transcription completed
[2024-01-15 10:33:00,000: INFO/Worker] Voice separation completed
[2024-01-15 10:33:30,000: INFO/Worker] Diarization completed
[2024-01-15 10:34:00,000: INFO/Worker] Pipeline completed
```

## Timing Esperado

Ejemplo: Batalla de 10 minutos

- **Descarga YouTube**: 1-2 minutos (depende de velocidad)
- **Transcripción Whisper**: 3-5 minutos (con GPU mucho más rápido)
- **Separación Demucs**: 2-3 minutos
- **Diarización Pyannote**: 1-2 minutos
- **Análisis de Rimas**: < 1 minuto

**Total: 8-13 minutos** (much faster con GPU)

## GPU vs CPU

### Con GPU (NVIDIA, recomendado)

Instalar CUDA:

```bash
# Verificar GPU disponible en Python
python -c "import torch; print(torch.cuda.is_available())"
```

Los tiempos se reducen a la mitad o más.

### Sin GPU (CPU lento)

Usar Whisper API en lugar de local:

```python
# En app/tasks/transcription.py cambiar a:
import requests
response = requests.post("https://api.openai.com/v1/audio/transcriptions", ...)
```

Costo: ~$0.006 por minuto de audio.

## Troubleshooting Fase 2

### "Connection refused" en Redis

```bash
docker-compose ps
docker-compose restart
```

### Celery worker no inicia

```bash
# Verificar que Redis está corriendo
redis-cli ping
# Debería devolver: PONG

# Verificar que celery_app se importa correctamente
python -c "from app.workers.celery_app import celery_app; print('OK')"
```

### "ModuleNotFoundError: No module named 'demucs'"

```bash
pip install -r requirements.txt
pip install demucs --upgrade
```

### YouTube download falla

```bash
# yt-dlp requiere ffmpeg
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg
# Windows: Descargar desde ffmpeg.org
```

### Whisper model lento en primera ejecución

Primera vez que ejecutas Whisper descarga el modelo (~2.9GB):

```
Loading Whisper model (large-v3)...
```

Esto toma 1-2 minutos la primera vez. Posteriormente se cachea localmente.

## Monitoreo en Producción

Para ver status de tasks Celery:

```bash
# Terminal nueva:
celery -A app.workers.celery_app events
```

O usar flower (dashboard web):

```bash
pip install flower
celery -A app.workers.celery_app flower --port=5555
# Abre: http://localhost:5555
```

## Limpieza de Archivos Temporales

Los archivos descargados/procesados se guardan en:

```
backend/temp/
backend/uploads/
```

Para limpiar:

```bash
rm -rf backend/temp/*
rm -rf backend/uploads/*
```

## Próximos Pasos (Fase 3)

Después de validar Fase 2, implementar:

- [ ] Análisis semántico con LLM (Claude API)
  - Evaluación de punchlines
  - Evaluación de ingenio
  - Evaluación de respuesta

Ver `NEXT_PHASES.md` para detalles.

## Resumen de Nuevos Endpoints

| Método | Endpoint                   | Función                           |
| ------ | -------------------------- | --------------------------------- |
| POST   | `/api/battles/youtube`     | Crear batalla desde YouTube       |
| POST   | `/api/battles/upload`      | Crear batalla desde archivo local |
| GET    | `/api/battles/{id}/status` | Monitorear progreso               |
| GET    | `/api/verses/battle/{id}`  | Obtener versos (mismo que MVP)    |

Los endpoints del MVP siguen funcionando igual:

- `POST /api/battles/text` → Batalla con texto ya transcrito
- `GET /api/ratings/verse/{id}/stats` → Estadísticas de crowdsourcing

## ¿Necesitas Ayuda?

- Documentación Swagger: http://localhost:8000/docs
- Logs de Celery: Terminal 2
- Estado del servidor: http://localhost:8000/health
