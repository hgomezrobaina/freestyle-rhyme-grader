# Freestyle Callificator Backend

Backend para el sistema de calificación automática de batallas de rap freestyle en español.

## Características del MVP (Fase 1)

- ✅ Análisis automático de rimas (densidad, diversidad, multisilábicas, internas)
- ✅ API REST para subir batallas y obtener métricas
- ✅ Almacenamiento en PostgreSQL
- ✅ Sistema de calificaciones de usuarios (crowdsourcing)
- 🔄 Pipeline de procesamiento con Celery (en desarrollo)
- 🔄 Descarga de YouTube y transcripción con Whisper (Fase próxima)

## Instalación

### Requisitos Previos

- Python 3.10+
- Docker & Docker Compose (para PostgreSQL y Redis)
- Git

### 1. Clonar el repositorio

```bash
cd backend
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# En Windows
venv\Scripts\activate

# En macOS/Linux
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar PostgreSQL y Redis con Docker

```bash
docker-compose up -d
```

Esto inicia:

- PostgreSQL en `localhost:5432`
- Redis en `localhost:6379`

Credenciales PostgreSQL:

- Usuario: `freestyle_user`
- Contraseña: `freestyle_password`
- Base de datos: `freestyle_callificator`

### 5. Inicializar la base de datos

Las tablas se crean automáticamente cuando ejecutas la aplicación (SQLAlchemy lo hace).

### 6. Ejecutar el servidor

```bash
python -m uvicorn app.main:app --reload
```

El servidor estará disponible en: `http://localhost:8000`

## Documentación de la API

Una vez que el servidor está corriendo, abre:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints Disponibles

### Batallas

**Crear batalla desde texto (simplest)**

```bash
POST /api/battles/text
```

Payload ejemplo:

```json
{
  "title": "FMS Argentina 2024",
  "description": "Batalla de prueba",
  "verses": [
    {
      "verse_number": 1,
      "speaker": "MC1",
      "text": "Yo vengo de la calle donde todo es distinto, representando el barrio con mi estilo bien finto",
      "duration_seconds": 30
    },
    {
      "verse_number": 2,
      "speaker": "MC2",
      "text": "Vos hablas de la calle pero aquí no te conocen, en mi barrio paso cosas que en el tuyo nunca pasan",
      "duration_seconds": 30
    }
  ]
}
```

Response:

```json
{
  "id": 1,
  "title": "FMS Argentina 2024",
  "description": "Batalla de prueba",
  "source_type": "text",
  "status": "completed",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:05"
}
```

**Obtener batalla con todos sus versos**

```bash
GET /api/battles/{battle_id}
```

**Listar todas las batallas**

```bash
GET /api/battles/
```

### Versos

**Obtener versos de una batalla (con métricas de rimas)**

```bash
GET /api/verses/battle/{battle_id}
```

Response incluye métricas como:

```json
{
  "id": 1,
  "verse_number": 1,
  "speaker": "MC1",
  "text": "...",
  "rhyme_metric": {
    "rhyme_density": 0.35,
    "multisyllabic_ratio": 0.25,
    "internal_rhymes_count": 2,
    "rhyme_diversity": 0.8,
    "total_syllables": 28,
    "rhymed_syllables": 10
  }
}
```

**Obtener métricas de rimas de un verso específico**

```bash
GET /api/verses/{verse_id}/rhyme-metrics
```

### Calificaciones de Usuarios

**Calificar un verso**

```bash
POST /api/ratings/verse/{verse_id}
```

Payload:

```json
{
  "user_id": "user_123",
  "rating_rhyme": 4.5,
  "rating_ingenio": 5,
  "rating_punchline": 4,
  "rating_respuesta": 3.5,
  "comment": "Muy buenas rimas"
}
```

**Obtener estadísticas de calificaciones de un verso**

```bash
GET /api/ratings/verse/{verse_id}/stats
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

## Estructura del Análisis de Rimas

### Métrica: Rhyme Density (Densidad de Rimas)

```
rhyme_density = sílabas_rimadas / total_sílabas
```

Escala de referencia académica:

- **0.05** = Muy baja (freestyle promedio)
- **0.15** = Media (rappers técnicos)
- **0.30+** = Alta (élite/freestylers con mucho prep)

### Métrica: Rhyme Diversity (Diversidad)

Número de tipos de rimas diferentes usadas (consonante, asonante, multisilábica, etc.)

### Tipos de Rimas Detectadas

1. **Consonante**: Coincidencia completa (vocales + consonantes finales)
2. **Asonante**: Solo vocales finales
3. **Multisilábica**: Rima de múltiples sílabas
4. **Interna**: Rima dentro del mismo verso
5. **Mosaico**: Rimas compuestas (ej: "para ti" / "compartí")

## Stack Tecnológico

```
Backend:
- FastAPI (framework web)
- SQLAlchemy (ORM)
- PostgreSQL (base de datos)
- Redis (cache/queue)

Análisis de Rimas:
- phonemizer (transcripción fonética)
- espeak-ng (síntesis texto-A palabra)
- pyphen (silabificación español)

Async Processing (próximamente):
- Celery (task queue)
- Whisper (transcripción audio)
- Demucs (separación de voces)
- pyannote-audio (diarización)
```

## Roadmap

### Completado (MVP)

- [x] Estructura de BD + models
- [x] API básica (text input)
- [x] Análisis de rimas (detector + métricas)
- [x] API de calificaciones

### En Progreso

- [ ] Celery task queue
- [ ] Descarga de YouTube
- [ ] Transcripción con Whisper
- [ ] Separación de voces (Demucs)
- [ ] Diarización (speaker identification)

### Futuro (Fase 2-3)

- [ ] Análisis semántico con LLM (ingenio, punchline, respuesta)
- [ ] Score final ponderado
- [ ] Frontend web para visualizar y calificar

## Testing

Ejecutar pruebas:

```bash
# (Tests por implementar)
pytest
```

## Desarrollo

### Agregar nuevos endpoints

1. Crear función en `app/api/{router_name}.py`
2. Documentar con docstrings (FastAPI + Swagger automáticamente)
3. Usar schemas de `app/models/schema.py`
4. Lógica de negocio en `app/services/`

### Extending análisis de rimas

Editar:

- `analysis/rhyme/detector.py` - Algoritmo de detección
- `analysis/rhyme/metrics.py` - Cálculo de métricas
- `analysis/phonetic/*` - Procesamiento fonético

## Problemas Comunes

### "Connection refused" en PostgreSQL

Verificar que Docker está corriendo:

```bash
docker ps
```

Reiniciar servicios:

```bash
docker-compose restart
```

### "Module phonemizer not found"

Instalar sistem dependencies (Linux/Mac):

```bash
sudo apt install espeak-ng ffmpeg  # Linux
brew install espeak-ng ffmpeg      # macOS
```

Windows: descargar desde [espeak-ng releases](https://github.com/espeak-ng/espeak-ng/releases)

## Licencia

[Especificar licencia]

## Contacto

[Tu contacto]
