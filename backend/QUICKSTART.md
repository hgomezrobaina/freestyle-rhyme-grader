# INICIO RÁPIDO - Freestyle Callificator Backend

El backend está **100% listo para desarrollo**. Aquí está todo lo que necesitas para empezar en 5 minutos.

## Instalación Rápida (5 minutos)

### 1. Requisitos

- Python 3.10+
- Docker Desktop (para PostgreSQL + Redis)
- Git

### 2. Iniciar Servicios

```bash
cd backend
docker-compose up -d
```

✅ PostgreSQL estará en `localhost:5432`
✅ Redis estará en `localhost:6379`

### 3. Instalar y Ejecutar

```bash
# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Instalar dependencies
pip install -r requirements.txt

# Ejecutar servidor
python -m uvicorn app.main:app --reload
```

🚀 API disponible en: **http://localhost:8000**
📚 Documentación: **http://localhost:8000/docs**

### 4. Ejecutar Demostración

```bash
pip install requests
python example_usage.py
```

---

## ¿Qué se ha Completado?

### ✅ Backend MVP Funcional

```
✓ Estructura profesional (FastAPI + SQLAlchemy + PostgreSQL)
✓ 3 modelos de BD (Battle, Verse, RhymeMetric, UserRating)
✓ Análisis de rimas 100% funcional
✓ API REST con 10+ endpoints
✓ Sistema de crowdsourcing de calificaciones
✓ Docker Compose para setup fácil
✓ Documentación completa (README + NEXT_PHASES)
✓ Script de ejemplo funcional
```

### 📊 Análisis Técnico de Rimas

El sistema **automáticamente** calcula:

- **Rhyme Density** (0-1): Proporción de sílabas que riman
- **Rhyme Diversity**: Variedad de tipos de rimas usadas
- **Multisyllabic Ratio**: % de rimas multisilábicas
- **Internal Rhymes**: Rimas dentro del mismo verso
- **Rhyme Types Breakdown**: Consonante, asonante, multisilábica, etc.

Ejemplo de output:

```json
{
  "rhyme_density": 0.35,
  "multisyllabic_ratio": 0.25,
  "internal_rhymes_count": 2,
  "rhyme_diversity": 0.8,
  "rhyme_types": {
    "consonant": 5,
    "assonant": 2,
    "multisyllabic": 1
  }
}
```

### 👥 Sistema de Crowdsourcing

Los usuarios pueden calificar cada verso en **4 dimensiones**:

- ⭐ Rima (automática + manual)
- 🎯 Ingenio (crowdsourcing)
- 💣 Punchline (crowdsourcing)
- 🎤 Respuesta (crowdsourcing)

---

## Flujo Actual (MVP)

```
1. Usuario sube batalla con versos en JSON
   POST /api/battles/text

2. Backend:
   - Crea batalla en BD
   - Analiza CADA verso automáticamente
   - Calcula todas las métricas de rimas
   - Devuelve battle_id inmediatamente

3. Frontend obtiene versos con métricas
   GET /api/verses/battle/{battle_id}

4. Usuarios califican versos
   POST /api/ratings/verse/{verse_id}

5. Frontend obtiene estadísticas por verso
   GET /api/ratings/verse/{verse_id}/stats
```

---

## Arquivos Principales

```
freestyle-callificator/backend/
├── app/
│   ├── main.py                 # 🚀 Aplicación FastAPI
│   ├── config.py               # ⚙️ Configuración
│   ├── database.py             # 🗄️ Conexión PostgreSQL
│   ├── models/                 # 📊 Modelos de BD
│   ├── services/               # 💼 Lógica de negocio
│   └── api/                    # 📡 Endpoints REST
│       ├── battles_router.py   # Crear batallas
│       ├── verses_router.py    # Obtener versos
│       └── ratings_router.py   # Calificaciones
│
├── analysis/                   # 🧠 Análisis de rimas
│   ├── phonetic/               # 📞 IPA + sílabas
│   └── rhyme/                  # 🎵 Detector metricado
│
├── README.md                   # 📖 Documentación completa
├── NEXT_PHASES.md              # 🔄 Roadmap Fase 2-3
├── example_usage.py            # 💡 Script de ejemplo
├── docker-compose.yml          # 🐳 Setup Docker
└── requirements.txt            # 📦 Dependencias
```

---

## Ejemplos de Uso

### Crear Batalla desde Texto

```bash
curl -X POST http://localhost:8000/api/battles/text \
  -H "Content-Type: application/json" \
  -d '{
    "title": "FMS 2024",
    "verses": [
      {
        "verse_number": 1,
        "speaker": "MC1",
        "text": "Yo vengo de la calle donde todo es distinto..."
      },
      {
        "verse_number": 2,
        "speaker": "MC2",
        "text": "Vos hablas de la calle pero aquí no te conocen..."
      }
    ]
  }'
```

Response:

```json
{
  "id": 1,
  "title": "FMS 2024",
  "status": "completed",
  "created_at": "2024-01-15T10:30:00"
}
```

### Obtener Versos con Métricas

```bash
curl http://localhost:8000/api/verses/battle/1
```

Response:

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
      "internal_rhymes_count": 2,
      "rhyme_diversity": 0.8
    }
  }
]
```

### Calificar un Verso

```bash
curl -X POST http://localhost:8000/api/ratings/verse/1 \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "rating_rhyme": 4.5,
    "rating_ingenio": 5,
    "rating_punchline": 4,
    "rating_respuesta": 3,
    "comment": "Excelentes rimas"
  }'
```

### Obtener Estadísticas de Calificaciones

```bash
curl http://localhost:8000/api/ratings/verse/1/stats
```

Response:

```json
{
  "verse_id": 1,
  "avg_rating_rhyme": 4.2,
  "avg_rating_ingenio": 4.5,
  "avg_rating_punchline": 4.1,
  "avg_rating_respuesta": 3.8,
  "total_ratings": 5
}
```

---

## Próximas Fases

### Fase 2: Automatización Completa

- ✅ Celery para procesamiento async
- ✅ Descarga de YouTube automatizada
- ✅ Transcripción con Whisper (local o API)
- ✅ Separación de voces (Demucs)
- ✅ Identificación de MC (Pyannote)

Ver: `NEXT_PHASES.md`

### Fase 3: Inteligencia Semántica

- ✅ Evaluación de Ingenio con LLM (Claude)
- ✅ Evaluación de Punchline con LLM
- ✅ Evaluación de Respuesta con LLM
- ✅ Calibración contra jueces humanos

---

## Dependencias Clave

```
✓ FastAPI - Framework web
✓ SQLAlchemy - ORM
✓ PostgreSQL - Base de datos
✓ Redis - Cache/Queue (para Celery)
✓ phonemizer - IPA transcription
✓ pyphen - Syllabification
✓ librosa - Audio analysis (fase 2)
✓ Whisper - STT (fase 2)
✓ Celery - Task queue (fase 2)
```

Todas ya están en `requirements.txt`.

---

## Troubleshooting

### "Connection refused to PostgreSQL"

```bash
docker-compose ps  # Verificar que está corriendo
docker-compose restart  # Reiniciar servicios
```

### "Module phonemizer not found"

macOS:

```bash
brew install espeak-ng ffmpeg
```

Linux:

```bash
sudo apt install espeak-ng ffmpeg
```

Windows: Descargar desde [espeak-ng releases](https://github.com/espeak-ng/espeak-ng/releases)

### "Port 8000 already in use"

```bash
# Usar puerto diferente
python -m uvicorn app.main:app --port 8001 --reload
```

---

## Estructura de Directorios Completa

```
freestyle-callificator/
├── backend/                          # ← YOU ARE HERE
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app
│   │   ├── config.py                # Config/ env vars
│   │   ├── database.py              # SQLAlchemy setup
│   │   │
│   │   ├── models/
│   │   │   ├── battle.py            # Battle, Verse, RhymeMetric
│   │   │   ├── rating.py            # UserRating
│   │   │   ├── schema.py            # Pydantic schemas
│   │   │   └── __init__.py
│   │   │
│   │   ├── api/
│   │   │   ├── battles_router.py    # POST /battles/text
│   │   │   ├── verses_router.py     # GET /verses
│   │   │   ├── ratings_router.py    # POST /ratings
│   │   │   └── __init__.py
│   │   │
│   │   ├── services/
│   │   │   ├── battle_service.py    # CRUD battles
│   │   │   ├── rating_service.py    # CRUD ratings
│   │   │   └── __init__.py
│   │   │
│   │   ├── tasks/                   # (Fase 2: Celery)
│   │   │   └── __init__.py
│   │   │
│   │   └── __init__.py
│   │
│   ├── analysis/
│   │   ├── phonetic/
│   │   │   ├── transcriptor.py      # Texto→IPA
│   │   │   ├── syllable_counter.py  # Contar sílabas
│   │   │   ├── vowel_extractor.py   # Extraer vocales
│   │   │   └── __init__.py
│   │   │
│   │   ├── rhyme/
│   │   │   ├── types.py             # RhymeType enum
│   │   │   ├── detector.py          # Detectar rimas
│   │   │   ├── metrics.py           # Calcular métricas
│   │   │   └── __init__.py
│   │   │
│   │   └── __init__.py
│   │
│   ├── workers/
│   │   └── __init__.py              # (Fase 2: Celery)
│   │
│   ├── requirements.txt             # Dependencies
│   ├── docker-compose.yml           # PostgreSQL + Redis
│   ├── .env                         # Environment variables
│   ├── .env.example                 # Template
│   ├── README.md                    # Documentación principal
│   ├── NEXT_PHASES.md               # Roadmap Fase 2-3
│   ├── QUICKSTART.md                # Este archivo
│   └── example_usage.py             # Script de demostración
│
├── rap-battle-scorer-roadmap.md     # Roadmap original
└── [Frontend React/Vue - PRÓXIMO]
```

---

## Resumen: Lo que Puedes Hacer Ahora

✅ **Crear batallas** con versos transcritos
✅ **Obtener métricas automáticas** de rimas
✅ **Permitir usuarios** calificar versos
✅ **Recopilar datos** de múltiples perspectivas humanas
✅ **Accumular datos de entrenamiento** para modelos futuros

## Próximo Paso

**Opción A: Crear Frontend Web**

- React o Vue
- Conectarse a los endpoints REST
- Interfaz para subir batallas y ver versos
- Componentes de calificación

**Opción B: Implementar Fase 2**

- Celery + Whisper
- Descarga de YouTube
- Pipeline automático completo
- Ver `NEXT_PHASES.md`

---

**¿Preguntas o necesitas ayuda?** Revisa:

- Documentación en `/docs` (Swagger)
- Script de ejemplo: `example_usage.py`
- Código fuente (bien comentado)
- `NEXT_PHASES.md` para fases siguientes
