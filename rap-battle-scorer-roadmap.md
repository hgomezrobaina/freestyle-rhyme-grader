# Sistema Calificador de Batallas de Rap Freestyle en Español

## Roadmap de Investigación y Desarrollo

---

## 1. Visión General del Sistema

### Pipeline completo

```
VIDEO (YouTube) → AUDIO → TEXTO (STT) → ANÁLISIS MULTIDIMENSIONAL → SCORE (1-5)
```

### Dimensiones de calificación

| Dimensión | Peso sugerido | Dificultad técnica | Automatizable? |
|-----------|---------------|-------------------|----------------|
| Rima técnica | 25% | Media | ✅ Sí |
| Flow / Métrica | 20% | Alta | ⚠️ Parcialmente |
| Punchlines / Ingenio | 25% | Muy alta | ⚠️ Con LLM |
| Respuesta al rival | 20% | Alta | ⚠️ Con LLM + contexto |
| Presencia escénica | 10% | Extrema | ❌ Muy limitado |

> **Nota honesta:** Las dimensiones marcadas con ⚠️ dependerán en gran medida de un LLM (como Claude o GPT) actuando como "juez asistido", no de un modelo entrenado desde cero. Esto tiene limitaciones que se detallan más adelante.

---

## 2. Arquitectura por Fases

### Fase 0 — Recolección de Datos (Semanas 1-3)

**Objetivo:** Construir un dataset de batallas transcritas con puntuaciones humanas.

**Pipeline de recolección:**

```
YouTube (yt-dlp) → Separación de audio → Transcripción (Whisper) → Anotación manual
```

#### Herramientas

| Paso | Herramienta | Notas |
|------|-------------|-------|
| Descarga de video | `yt-dlp` | Extraer solo audio con `-x --audio-format wav` |
| Separación de voces | `demucs` (Meta) | Separar voz de ruido ambiente/beat/público |
| Transcripción | Whisper Large-v3 | WER ~3-8% en español. Hay versión fine-tuned para español con WER ~5.34% |
| Diarización | `pyannote-audio` | Identificar quién habla (MC1 vs MC2) |
| Anotación | Label Studio o spreadsheet | Puntuación humana por ronda |

#### Fuentes de videos sugeridas

- **FMS (Freestyle Master Series)** — Formato profesional con jueces y puntuaciones oficiales
- **Red Bull Batalla** — Competencias internacionales con scores públicos
- **BDM (Batallas de Maestros)** — Chile/Latinoamérica
- **God Level** — Competencias con sistema de votación público

> **Ventaja clave:** FMS y Red Bull Batalla tienen puntuaciones de jueces reales publicadas. Esto te da un "ground truth" para entrenar/validar tu sistema.

#### Estructura del dataset

```
dataset/
├── raw_audio/          # Audio completo de batallas
├── separated_audio/    # Voz aislada por MC
├── transcriptions/     # Texto transcrito por turno/ronda
├── annotations/        # Scores humanos por dimensión
└── metadata/           # Info de la batalla (evento, MCs, ronda, jueces)
```

#### Esquema de anotación sugerido por ronda

```json
{
  "battle_id": "fms2024_arg_j1_r1",
  "event": "FMS Argentina 2024 - Jornada 1",
  "mc1": "MC Nombre 1",
  "mc2": "MC Nombre 2",
  "round": 1,
  "round_type": "easy_mode",
  "mc1_text": "Yo vengo de la calle donde...",
  "mc2_text": "Vos hablas de la calle pero...",
  "mc1_scores": {
    "rima_tecnica": 3,
    "flow_metrica": 4,
    "punchline_ingenio": 5,
    "respuesta_rival": 4,
    "presencia": 3,
    "total": 3.8
  },
  "mc2_scores": { "..." : "..." },
  "judge_scores_official": [4, 3, 4],
  "winner": "mc1"
}
```

**Meta mínima:** 100-200 rondas anotadas para tener una base funcional. Ideal: 500+.

---

### Fase 1 — Análisis Técnico de Rimas (Semanas 3-6)

**Objetivo:** Construir un analizador fonético de rimas en español.

Este es el componente más "clásico" del sistema y el más automatizable. La investigación académica (Hirjee & Brown, 2010) demostró que la densidad de rima es una métrica robusta para evaluar complejidad lírica.

#### Stack técnico

```python
# Dependencias principales
pip install phonemizer epitran gruut-ipa

# Para transcripción fonética del español
sudo apt install espeak-ng
```

#### Módulos a construir

**1. Transcriptor fonético español**

```python
# Concepto usando phonemizer + espeak-ng
from phonemizer import phonemize

texto = "yo vengo de la calle representando"
ipa = phonemize(texto, language='es', backend='espeak')
# Resultado: "ʝo benɡo de la kaʎe represeñtando"
```

**2. Detector de rimas**

Tipos de rima a detectar (de menor a mayor complejidad):

| Tipo | Ejemplo | Puntos |
|------|---------|--------|
| Consonante final | calle / valle | 1 |
| Asonante | gato / banco | 0.5 |
| Interna | "Vengo **rimando** mientras voy **caminando**" | 1.5 |
| Multisilábica | "representante" / "delirante" | 2 |
| Mosaic/Compuesta | "para ti" / "compartí" | 2.5 |

**Algoritmo base:**

1. Convertir texto a representación fonética (IPA)
2. Extraer las últimas N sílabas de cada verso
3. Comparar similitud fonética entre pares de versos
4. Calcular un "rhyme score" basado en coincidencias de vocales y consonantes
5. Identificar rimas internas buscando coincidencias dentro del mismo verso

**3. Calculador de Rhyme Density**

```
Rhyme Density = sílabas_rimadas / total_sílabas
```

Referencia de la investigación académica:
- Rappers promedio: ~0.10-0.15
- Rappers técnicos: ~0.20-0.30
- Freestylers élite: variable, pero los mejores superan 0.20

**Métricas derivadas:**

| Métrica | Descripción |
|---------|-------------|
| `rhyme_density` | Proporción de sílabas que riman |
| `rhyme_diversity` | Variedad de esquemas de rima usados |
| `multisyllabic_ratio` | Proporción de rimas multisilábicas vs simples |
| `internal_rhyme_count` | Rimas dentro del mismo verso |
| `rhyme_scheme_complexity` | AABB=1, ABAB=2, ABCABC=3, etc. |

---

### Fase 2 — Análisis de Flow y Métrica (Semanas 6-9)

**Objetivo:** Evaluar el encaje rítmico del MC con el beat (si hay) o su cadencia natural.

> **Advertencia:** Esta es la fase más experimental. El análisis de flow desde audio es un problema abierto en la investigación. El approach aquí es una aproximación, no una solución definitiva.

#### Approach sugerido

**2A. Análisis de prosodia (desde audio)**

```python
# Usar librosa para extraer características rítmicas
import librosa

y, sr = librosa.load("mc1_voice.wav")

# Tempo y beats
tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

# Onset detection (cuando el MC empieza a articular sílabas)
onsets = librosa.onset.onset_detect(y=y, sr=sr)

# Ritmo del habla
speech_rate = len(onsets) / duracion_segundos
```

**2B. Análisis silábico (desde texto)**

```python
# Contar sílabas por verso usando hyphenation rules del español
# El español es bastante regular en su silabificación
import pyphen

dic = pyphen.Pyphen(lang='es')
silabas = dic.inserted("representando")  # "re-pre-sen-tan-do"
```

**Métricas de flow:**

| Métrica | Descripción | Cómo se mide |
|---------|-------------|--------------|
| `speech_rate` | Sílabas por segundo | Audio: onset detection |
| `rhythmic_consistency` | Regularidad del ritmo | Varianza de intervalos entre onsets |
| `pause_patterns` | Uso estratégico de pausas | Detección de silencios |
| `syllable_alignment` | Encaje de sílabas con beats | Correlación onsets vs beats (si hay beat) |

**Scoring de flow (heurístico):**

- Speech rate muy bajo (<3 síl/s): Penalizar (titubeo)
- Speech rate medio (4-7 síl/s): Normal
- Speech rate alto con consistencia (>7 síl/s): Bonificar (doble tempo)
- Alta varianza rítmica: Puede ser bueno (variación intencional) o malo (descontrol)

> Este módulo va a necesitar mucha calibración manual. Recomiendo empezar con las métricas textuales y agregar las de audio iterativamente.

---

### Fase 3 — Análisis Semántico con LLM (Semanas 9-14)

**Objetivo:** Evaluar punchlines, ingenio, y respuesta al rival usando un LLM como "juez asistido".

Este es el corazón del sistema y donde un LLM grande aporta más valor. No vas a entrenar un modelo desde cero para esto — vas a usar prompt engineering sofisticado con un modelo existente.

#### Arquitectura

```
Transcripción MC1 + MC2  →  LLM (Claude API)  →  Scores estructurados (JSON)
       ↑                          ↑
  Contexto de la batalla    Rubric/Criterios detallados
```

#### Prompt de evaluación (concepto)

```python
SYSTEM_PROMPT = """
Eres un juez experto de batallas de freestyle rap en español.
Evalúas cada turno de un MC en una escala de 1 a 5 en las siguientes dimensiones:

## Criterios de evaluación

### Punchline / Ingenio (1-5)
- 1: Sin remates memorables, líneas genéricas
- 2: Algún intento de remate pero predecible
- 3: Punchlines decentes con algún doble sentido
- 4: Remates ingeniosos con referencias culturales, doble sentido efectivo
- 5: Punchlines devastadores, referencias brillantes, metáforas originales

### Respuesta al rival (1-5)
- 1: Ignora completamente lo que dijo el rival
- 2: Referencia vaga a lo que dijo el rival
- 3: Responde a algunos puntos del rival
- 4: Contraataque directo y efectivo a los argumentos del rival
- 5: Desmonta completamente al rival usando sus propias palabras/argumentos

### Coherencia y estructura (1-5)
- 1: Ideas inconexas, no se entiende el mensaje
- 2: Algunas ideas conectadas pero con mucho relleno
- 3: Hilo conductor claro con algunos desvíos
- 4: Narrativa bien construida de principio a fin
- 5: Estructura impecable con setup, desarrollo y cierre

Responde SOLO en formato JSON válido.
"""

USER_PROMPT = """
## Contexto de la batalla
- Evento: {evento}
- Ronda: {ronda} ({tipo_ronda})
- MC evaluado: {mc_nombre}

## Lo que dijo el rival previamente:
{texto_rival}

## Turno del MC a evaluar:
{texto_mc}

Evalúa este turno.
"""
```

#### Output esperado del LLM

```json
{
  "punchline_ingenio": {
    "score": 4,
    "justificacion": "Buen uso de doble sentido con 'calle' como lugar y como verbo 'callarse'",
    "mejores_lineas": ["línea específica que destacó"]
  },
  "respuesta_rival": {
    "score": 3,
    "justificacion": "Respondió al ataque sobre su estilo pero ignoró la referencia personal",
    "conexiones_detectadas": ["rival dijo X, MC respondió con Y"]
  },
  "coherencia": {
    "score": 4,
    "justificacion": "Buena estructura narrativa con cierre contundente"
  }
}
```

#### Calibración del LLM

**Problema:** El LLM puede ser inconsistente en sus puntuaciones.

**Solución — Multi-evaluación:**

1. Hacer 3-5 evaluaciones del mismo turno (con temperature > 0)
2. Promediar los scores
3. Si la varianza es alta (>1 punto), marcar como "evaluación incierta"
4. Comparar con scores humanos del dataset para calibrar

**Validation loop:**

```python
# Pseudocódigo
for ronda in dataset_anotado:
    scores_llm = [evaluar_con_llm(ronda) for _ in range(5)]
    score_promedio = mean(scores_llm)
    score_humano = ronda.human_score
    
    error = abs(score_promedio - score_humano)
    
    # Métricas de calibración
    mae = mean_absolute_error(todas_predicciones, todos_humanos)
    correlacion = spearman_correlation(predicciones, humanos)
```

**Meta realista:**
- MAE < 0.8 puntos sería un buen resultado
- Correlación de Spearman > 0.6 sería prometedor
- Si no llegas a estos números, el LLM necesita mejor prompting o el problema es demasiado subjetivo

---

### Fase 4 — Score Final Integrado (Semanas 14-16)

**Objetivo:** Combinar todas las dimensiones en un score final de 1 a 5.

#### Modelo de fusión

**Opción A — Promedio ponderado (simple, recomendado para empezar):**

```python
def score_final(rima, flow, punchline, respuesta, presencia):
    return (
        rima * 0.25 +
        flow * 0.20 +
        punchline * 0.25 +
        respuesta * 0.20 +
        presencia * 0.10
    )
```

**Opción B — Modelo aprendido (cuando tengas suficientes datos):**

```python
# Regresión sobre scores humanos
from sklearn.ensemble import GradientBoostingRegressor

X = [rima, flow, punchline, respuesta, presencia]  # features por ronda
y = score_humano  # target

modelo = GradientBoostingRegressor()
modelo.fit(X_train, y_train)
```

> La Opción B solo tiene sentido cuando tengas 200+ rondas anotadas. Antes de eso, usa la Opción A.

---

## 3. Stack Tecnológico Completo

### Infraestructura recomendada

| Componente | Herramienta | Local/Cloud | Costo estimado |
|-----------|-------------|-------------|----------------|
| Descarga videos | `yt-dlp` | Local | Gratis |
| Separación de voz | `demucs` (Meta) | Local (GPU recomendada) | Gratis |
| STT | Whisper Large-v3 | Local con GPU / API | $0.006/min (API) |
| Diarización | `pyannote-audio` | Local | Gratis |
| Análisis fonético | `phonemizer` + `espeak-ng` | Local | Gratis |
| Análisis de audio | `librosa` | Local | Gratis |
| LLM para semántica | Claude API (Sonnet) | Cloud | ~$0.003/1K tokens |
| Orquestación | Python + notebooks | Local | Gratis |
| Base de datos | SQLite → PostgreSQL | Local | Gratis |
| Interfaz | Streamlit / Gradio | Local | Gratis |

### Requisitos de hardware mínimos

**Para desarrollo local con Whisper:**
- GPU: NVIDIA con 10GB+ VRAM (RTX 3060 o superior)
- RAM: 16GB+
- Storage: 100GB+ (para audio/video)

**Alternativa sin GPU local:**
- Usar Whisper API de OpenAI ($0.006/min)
- Usar Google Colab con GPU gratuita para experimentación

---

## 4. Estructura del Proyecto

```
rap-battle-scorer/
├── README.md
├── requirements.txt
├── config.yaml                    # Configuración global
│
├── data/
│   ├── collection/
│   │   ├── downloader.py          # yt-dlp wrapper
│   │   ├── audio_separator.py     # demucs wrapper
│   │   └── sources.yaml           # URLs y metadata de batallas
│   ├── transcription/
│   │   ├── whisper_transcriber.py
│   │   └── diarizer.py            # pyannote speaker diarization
│   └── annotation/
│       ├── schema.py              # Pydantic models para anotaciones
│       └── annotator_tool.py      # Herramienta de anotación
│
├── analysis/
│   ├── phonetic/
│   │   ├── transcriptor.py        # Texto → IPA
│   │   ├── rhyme_detector.py      # Detección de rimas
│   │   ├── rhyme_density.py       # Cálculo de densidad
│   │   └── syllable_counter.py    # Conteo silábico español
│   ├── prosody/
│   │   ├── flow_analyzer.py       # Análisis rítmico desde audio
│   │   └── tempo_detector.py      # Detección de tempo/cadencia
│   ├── semantic/
│   │   ├── llm_judge.py           # Evaluación con Claude/GPT
│   │   ├── prompts.py             # Templates de prompts
│   │   └── calibration.py         # Calibración vs scores humanos
│   └── fusion/
│       ├── weighted_scorer.py     # Score ponderado
│       └── learned_scorer.py      # Modelo aprendido (fase avanzada)
│
├── evaluation/
│   ├── metrics.py                 # MAE, Spearman, etc.
│   ├── human_agreement.py         # Inter-annotator agreement
│   └── reports.py                 # Generación de reportes
│
├── app/
│   ├── streamlit_app.py           # Interfaz web
│   └── api.py                     # FastAPI endpoint (opcional)
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_rhyme_analysis.ipynb
│   ├── 03_flow_analysis.ipynb
│   ├── 04_llm_evaluation.ipynb
│   └── 05_fusion_calibration.ipynb
│
└── tests/
    ├── test_rhyme_detector.py
    ├── test_transcription.py
    └── test_scoring.py
```

---

## 5. Limitaciones Conocidas y Riesgos

Es crucial que tengas estas limitaciones claras desde el inicio:

### Limitaciones técnicas

| Problema | Impacto | Mitigación |
|----------|---------|------------|
| Whisper falla con superposición de voces | Pierde texto cuando hablan encima | Usar demucs para separar + diarización |
| Slang regional no reconocido por Whisper | Transcripciones incorrectas | Fine-tuning de Whisper o corrección manual |
| El español tiene rima más "fácil" que el inglés | Muchas palabras riman naturalmente en español (ej: -ando, -ente) | Ajustar thresholds de rhyme density hacia arriba |
| LLM no entiende contexto cultural local | Pierde referencias a personajes/eventos locales | Incluir contexto en el prompt |
| El "flow" es inherentemente subjetivo | Difícil de cuantificar | Usar múltiples métricas proxy |
| Público/beat contaminan el audio | Difícil aislar la voz | Demucs + preprocessing agresivo |

### Limitaciones del approach con LLM

- **No es un modelo entrenado desde cero:** Estás usando prompt engineering, no machine learning clásico. El LLM no "aprende" de tus datos.
- **Inconsistencia:** El mismo turno evaluado dos veces puede dar scores diferentes.
- **Sesgo cultural:** Los LLMs tienen más datos de rap en inglés que en español freestyle.
- **Costo:** Cada evaluación cuesta dinero (API calls).
- **No es tiempo real:** El pipeline completo toma minutos por batalla.

### ¿Qué significaría "éxito" en este proyecto?

| Nivel | Descripción | Métrica |
|-------|-------------|---------|
| Básico | El sistema detecta rimas y da un score técnico razonable | Rhyme detection accuracy > 80% |
| Intermedio | El sistema predice ganadores de rondas mejor que el azar | Accuracy de predicción > 60% |
| Avanzado | Correlación significativa con jueces reales | Spearman > 0.5 con scores de FMS |
| Excelente | Scores del sistema son indistinguibles de un juez humano amateur | Spearman > 0.7 |

> **Mi estimación honesta:** Con las herramientas actuales, puedes llegar al nivel "Intermedio" con esfuerzo moderado. El nivel "Avanzado" requiere un dataset grande y mucha calibración. El nivel "Excelente" es un objetivo de investigación serio.

---

## 6. Primeros Pasos Concretos

### Semana 1: Setup y primeros datos

```bash
# 1. Crear entorno
python -m venv rap-scorer-env
source rap-scorer-env/bin/activate

# 2. Instalar dependencias core
pip install yt-dlp openai-whisper librosa phonemizer pyphen
pip install torch torchaudio  # para Whisper local
pip install anthropic         # para Claude API
sudo apt install espeak-ng ffmpeg

# 3. Descargar tu primera batalla
yt-dlp -x --audio-format wav -o "batalla_test.wav" "URL_VIDEO"

# 4. Transcribir
python -c "
import whisper
model = whisper.load_model('large-v3')
result = model.transcribe('batalla_test.wav', language='es')
print(result['text'])
"
```

### Semana 2: Primer análisis de rimas

```python
# rhyme_detector_v0.py — Versión mínima viable
from phonemizer import phonemize

def get_last_vowels(word, n=3):
    """Extrae las últimas N vocales de una palabra en IPA."""
    ipa = phonemize(word, language='es', backend='espeak', strip=True)
    vowels = [c for c in ipa if c in 'aeiouɛɔ']
    return ''.join(vowels[-n:])

def do_words_rhyme(word1, word2, min_match=2):
    """Determina si dos palabras riman comparando vocales finales."""
    v1 = get_last_vowels(word1)
    v2 = get_last_vowels(word2)
    
    # Comparar desde el final
    matches = 0
    for c1, c2 in zip(reversed(v1), reversed(v2)):
        if c1 == c2:
            matches += 1
        else:
            break
    
    return matches >= min_match

# Test
print(do_words_rhyme("caminando", "rimando"))    # True
print(do_words_rhyme("batalla", "calle"))         # False
print(do_words_rhyme("representante", "delirante"))  # True
```

### Semana 3: Primera evaluación con LLM

Usar la API de Claude para evaluar un turno transcrito y comparar con el score real de los jueces.

---

## 7. Recursos de Investigación Relevantes

### Papers académicos

- **Hirjee & Brown (2010):** "Using Automated Rhyme Detection to Characterize Rhyming Style in Rap Music" — El paper fundacional para detección automática de rimas.
- **Malmi et al. (2016):** "DopeLearning: A Computational Approach to Rap Lyrics Generation" — Modelos de ranking para líneas de rap.
- **DeepRapper:** Sistema Transformer que modela rimas y ritmos simultáneamente.

### Herramientas open source

| Herramienta | Uso | URL |
|-------------|-----|-----|
| Whisper | STT multilingüe | github.com/openai/whisper |
| Demucs | Separación de fuentes de audio | github.com/facebookresearch/demucs |
| pyannote-audio | Diarización de hablantes | github.com/pyannote/pyannote-audio |
| phonemizer | Texto → IPA | github.com/bootphon/phonemizer |
| epitran | Transcripción fonética | github.com/dmort27/epitran |
| librosa | Análisis de audio | librosa.org |
| prosodic | Parser métrico-fonológico | github.com/quadrismegistus/prosodic |
| WhisperX | Whisper + timestamps + diarización | github.com/m-bain/whisperX |

---

## 8. Consideraciones Legales

- **Descarga de videos:** Verifica los términos de uso de cada plataforma. Para investigación/uso personal generalmente hay más flexibilidad, pero no distribuyas el contenido.
- **Transcripciones:** Las letras de freestyle son propiedad intelectual de los MCs. Tu dataset debe ser para investigación, no para publicación de las letras.
- **Puntuaciones oficiales:** Los sistemas de puntuación de FMS/Red Bull son datos públicos (se transmiten en vivo).

---

*Documento generado como guía de investigación. Los tiempos estimados son aproximados y dependen de la dedicación y experiencia del desarrollador.*
