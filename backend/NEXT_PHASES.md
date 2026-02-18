# Próximas Fases - Roadmap de Implementación

Este documento describe cómo completar las fases 2 y 3 después del MVP actual.

## Estado Actual (MVP Fase 1 - COMPLETADO)

✅ **Lo que ya funciona:**

- API REST completa con 3 rutas principales
- Almacenamiento en PostgreSQL
- Análisis de rimas (detector + métricas)
- Sistema de calificaciones de usuarios (crowdsourcing)
- Documentación completa (Swagger en /docs)

✅ **Cómo usarlo:**

```bash
# 1. Iniciar servicios
docker-compose up -d

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar servidor
python -m uvicorn app.main:app --reload

# 4. Ejecutar ejemplo
python example_usage.py
```

---

## Fase 2: Pipeline de Procesamiento Automático (Próximo)

**Objetivo:** Permitir descarga de YouTube e ingesta automática de audio/video.

### 2.1 Configurar Celery + Redis

**Archivos a crear:**

`app/workers/celery_app.py`:

```python
from celery import Celery
from app.config import get_settings

settings = get_settings()
app = Celery(
    'freestyle_callificator',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)
```

`app/tasks/pipeline.py`:

```
# Orchestrate: download → separate → transcribe → analyze → save
```

### 2.2 Implementar Tareas Celery

**Descargar de YouTube:**

```python
# app/tasks/download.py
from yt_dlp import YoutubeDL

@celery_app.task
def download_youtube_video(url: str, output_path: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': output_path,
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
```

### 2.3 Crear Rutas para YouTube y Upload

**Archivos a crear:**

`app/api/youtube_router.py`:

```python
@router.post("/youtube")
async def create_battle_from_youtube(
    url: str,
    title: str,
    db: Session = Depends(get_db)
):
    # 1. Create battle record with status "processing"
    # 2. Queue download_youtube_video task
    # 3. Return battle_id immediately
    # (Frontend polls GET /battles/{id} para ver progreso)
```

`app/api/upload_router.py`:

```python
@router.post("/upload")
async def create_battle_from_upload(
    file: UploadFile,
    title: str,
    db: Session = Depends(get_db)
):
    # Similar a YouTube pero con archivo local
```

### 2.4 Integración con Whisper

```python
# app/tasks/transcription.py
@celery_app.task
def transcribe_audio(audio_path: str, battle_id: int):
    import whisper
    model = whisper.load_model("large-v3")
    result = model.transcribe(audio_path, language="es")

    # Guardar transcripción en BD
    # Iniciar siguiente task (diarization)
```

### 2.5 Diarización y Separación de Voces

```python
# app/tasks/diarization.py
from demucs import separate
from pyannote.audio import Pipeline

@celery_app.task
def separate_voices(audio_path: str):
    # 1. Usar demucs para separar voces del beat
    # 2. Usar pyannote para identificar MC1 vs MC2
    # 3. Segmentar en versos individuales

@celery_app.task
def diarize_speakers(audio_path: str, transcript: str):
    # Identificar timestamps de cada speaker
    # Splitar transcript por speaker
```

## Fase 3: Análisis Semántico con LLM (Después de Fase 2)

**Objetivo:** Evaluar ingenio, punchline, respuesta con Claude API.

### 3.1 Crear Evaluador LLM

```python
# analysis/semantic/llm_judge.py
from anthropic import Anthropic

class LLMJudge:
    def __init__(self):
        self.client = Anthropic()

    def evaluate_verses(self, verse1, verse2, context):
        """Evaluate punchline, wit, response using Claude."""
        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": f"Evalúa esta ronda...\n{context}"}
            ]
        )
        return self._parse_eval(response)
```

### 3.2 Modelo de BD Ampliado

```python
# Agregar a RhymeMetric o crear nueva tabla SemanticMetric:
class SemanticMetric(Base):
    __tablename__ = "semantic_metrics"

    verse_id = Column(Integer, ForeignKey("verses.id"))
    punchline_score = Column(Float)  # 1-5
    wit_score = Column(Float)        # 1-5
    response_to_opponent = Column(Float)  # 1-5
    llm_explanation = Column(String)
    confidence = Column(Float)  # 0-1
```

### 3.3 Validación contra Ground Truth

```python
# evaluation/calibration.py
def calibrate_llm(dataset_with_human_scores):
    """
    Compare LLM predictions vs human judges
    Calculate MAE, Spearman correlation
    """
    mae = mean_absolute_error(llm_preds, human_scores)
    correlation = spearman(llm_preds, human_scores)

    # Si mae < 0.8 y correlation > 0.6, considerar modelo calibrado
```

## Implementación Step-by-Step

### Semana 1: Celery + Basic Tasks

- [ ] Instalar celery, redis
- [ ] Crear celery_app.py
- [ ] Crear primera task (dummy)
- [ ] Configurar worker para ejecutar tasks

### Semana 2: Download + Transcription

- [ ] Crear download_youtube_video task
- [ ] Crear transcribe_audio task con Whisper
- [ ] Crear POST /battles/youtube endpoint
- [ ] Test completo: YouTube URL → transcripción

### Semana 3: Diarization + Voice Separation

- [ ] Instalar demucs, pyannote
- [ ] Crear separate_voices task
- [ ] Crear diarize_speakers task
- [ ] Segmentar versos automáticamente

### Semana 4: Upload + Pipeline Integration

- [ ] Crear POST /battles/upload endpoint
- [ ] Integrar todo el pipeline (download → transcribe → diarize → analyze)
- [ ] Status tracking (batalla → pending → processing → completed)
- [ ] Error handling

### Semana 5: LLM Semantic Analysis

- [ ] Crear LLMJudge class
- [ ] Implementar evaluación de punchlines
- [ ] Implementar evaluación de respuesta
- [ ] Calibración contra jueces humanos

### Semana 6: Q/A + Optimization

- [ ] Testing completo
- [ ] Mejorar prompts de LLM basado en resultados
- [ ] Optimizar performance
- [ ] Documentación final

## Dependencias a Instalar (Fase 2+)

```bash
# Celery
pip install celery[redis]==5.3.0

# Audio processing
pip install demucs yt-dlp

# Speaker diarization
pip install pyannote.audio

# LLM (Fase 3)
pip install anthropic

# Desarrollo
pip install pytest pytest-asyncio httpx
```

## Testing Strategy

```python
# tests/test_pipeline.py
def test_celery_download_task():
    # Mock YouTube download
    pass

def test_transcription_task():
    # Test Whisper on known audio
    pass

def test_diarization_task():
    # Test speaker identification
    pass

def test_llm_evaluation():
    # Test against known examples
    pass
```

## Consideraciones de Performance

1. **GPU**: Whisper se ejecuta mucho más rápido con GPU
   - Considerar usar Whisper API si no hay GPU local

2. **Caching**: Cachear embeddings de LLM

3. **Async**: Celery permite procesar múltiples batallas en paralelo

4. **Storage**: Batallas grandes (~10GB) requieren storage externo

## Integración Frontend (Futuro)

El frontend necesitará:

```javascript
// 1. WebSocket para ver progreso en tiempo real
ws.on("battle_status", (battle_id, status) => {});

// 2. Long polling como fallback
setInterval(() => GET / battles / { id }, 2000);

// 3. Mostrar versos cuando estén listos (parcialmente completados)
GET / battles / { id } / verses;
```

---

## Contacto / Preguntas

Si tienes dudas sobre estas fases, revisa:

- Roadmap original: `../rap-battle-scorer-roadmap.md`
- Plan detallado: `../plan/enumerated-forging-eagle.md`
