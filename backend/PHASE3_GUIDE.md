# FASE 3 - Análisis Semántico con LLM

## 🎯 Objetivo

Implementar evaluación automática de:

- **Punchlines** (remates, impacto)
- **Ingenio** (creatividad, originalidad)
- **Respuesta** (qué tan bien responde al rival)

Usando Claude API como "juez asistido" para complementar el análisis técnico de rimas.

---

## 📦 Lo Que Se Implementó

### 1. **LLM Judge Module**

```python
# analysis/semantic/llm_judge.py
✅ evaluate_punchline()     → Evalúa remates e impacto (1-5)
✅ evaluate_cleverness()    → Evalúa ingenio general (1-5)
✅ evaluate_response()      → Evalúa respuesta al rival (1-5)
✅ Multi-evaluation         → Múltiples evaluaciones para calibración
```

### 2. **Semantic Metrics Model**

```python
# app/models/semantic.py
✅ SemanticMetric           → Almacena scores LLM
✅ HumanJudgeAnnotation     → Almacena anotaciones humanas para calibración
```

### 3. **Celery Tasks**

```python
# app/tasks/semantic_evaluation.py
✅ evaluate_verse_semantic()  → Task async para evaluación LLM
✅ calibrate_llm_scores()     → Calibración vs jueces humanos
✅ calculate_integrated_score() → Score final (técnico + semántico)
```

### 4. **REST Endpoints**

```
✅ POST /api/semantic/verses/{id}/evaluate-semantic
   → Queue una evaluación semántica

✅ GET /api/semantic/verses/{id}/semantic-metrics
   → Obtener scores semánticos

✅ POST /api/semantic/verses/{id}/human-annotation
   → Guardar anotaciones humanas para calibración

✅ GET /api/semantic/verses/{id}/comparison
   → Comparar scores LLM vs humanos
```

---

## 🚀 Cómo Usar Fase 3

### 1. **Setup**

Asegúrate de tener la clave API de Anthropic:

```bash
# Opción A: Variable de entorno
export ANTHROPIC_API_KEY="sk-ant-..."

# Opción B: En archivo .env
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

### 2. **Obtener Keys API**

Ve a https://console.anthropic.com/ y crea una clave API.

Precio: ~$0.003 por 1K output tokens (muy barato para evaluaciones).

### 3. **Evaluar un Verso**

```bash
# 1. Queue la evaluación
curl -X POST "http://localhost:8000/api/semantic/verses/1/evaluate-semantic" \
  -H "Content-Type: application/json" \
  -d '{
    "verse_id": 1,
    "context": "Batalla de FMS Argentina 2024. Opponent verse: Vos hablas pero no eres real",
    "num_evaluations": 3
  }'

# Response:
{
  "task_id": "abc123...",
  "verse_id": 1,
  "status": "queued"
}

# 2. Obtener resultados (cuando esté listo)
curl "http://localhost:8000/api/semantic/verses/1/semantic-metrics"

# Response:
{
  "verse_id": 1,
  "punchline_score": 4.2,
  "cleverness_score": 4.5,
  "response_score": 3.8,
  "punchline_confidence": 0.92,
  "cleverness_confidence": 0.88,
  "response_confidence": 0.85,
  "integrated_score": 4.18
}
```

---

## 📊 Evaluación Completa

### Punchline & Remates (1-5)

```
1: Sin remates, líneas genéricas
2: Algunos intentos pero predecibles
3: Algunos remates decentes
4: Remates ingeniosos con doble sentido
5: Remates devastadores y muy creativos
```

Ejemplo: _"Yo soy tan real que te convierto en ficción"_ = 4.5

### Ingenio & Creatividad (1-5)

```
1: Poco creativo, muy predecible
2: Algo creativo pero con clichés
3: Dobles sentidos y referencias decentes
4: Referencias originales y cleverness
5: Muy ingenioso, metáforas brillantes
```

### Respuesta al Rival (1-5)

```
1: Ignora completamente al rival
2: Referencia vaga
3: Responde a algunos puntos
4: Contraataque directo y efectivo
5: Desmonta completamente al rival
```

---

## 🔄 Workflow Completo

```
Batalla se procesa (Fase 2)
    ↓
Versos se generan con RhymeMetric
    ↓
Usuario solicita evaluación semántica
    ↓
POST /api/semantic/verses/{id}/evaluate-semantic
    ↓
Celery task queue → Claude API
    ↓
Claude evalúa 3x (para calibración)
    ↓
Promedios se guardan en SemanticMetric
    ↓
GET /api/semantic/verses/{id}/semantic-metrics
    ↓
User ve: punchline_score, cleverness_score, response_score
    ↓
(Optional) User añade human annotation para calibración
    ↓
Integrated score = weighted average de técnico + semántico
```

---

## 💡 Calibración vs Jueces Humanos

### ¿Por qué calibrar?

El LLM puede ser inconsistente. Necesitamos validar que sus scores:

1. Correlacionan con jueces humanos reales
2. Tienen error bajo (MAE < 0.8 sería bueno)

### Cómo calibrar

```bash
# 1. Human judges califican versos manualmente
curl -X POST "http://localhost:8000/api/semantic/verses/1/human-annotation" \
  -H "Content-Type: application/json" \
  -d '{
    "human_punchline_score": 4.0,
    "human_cleverness_score": 4.5,
    "human_response_score": 3.5,
    "judge_id": "judge_alice",
    "notes": "Very creative pero respuesta podría ser mejor"
  }'

# 2. Comparar LLM vs Human
curl "http://localhost:8000/api/semantic/verses/1/comparison"

# Response:
{
  "verse_id": 1,
  "llm_scores": {
    "punchline": 4.2,
    "cleverness": 4.5,
    "response": 3.8
  },
  "human_avg_scores": {
    "punchline": 4.0,
    "cleverness": 4.5,
    "response": 3.5
  },
  "differences": {
    "punchline_diff": 0.2,
    "cleverness_diff": 0.0,
    "response_diff": 0.3
  },
  "num_human_judges": 1
}
```

### Métricas de Calibración

Con muchas anotaciones humanas, calcular:

```python
MAE = mean(|llm_score - human_score|)
Spearman = correlation(llm_scores, human_scores)

Bueno: MAE < 0.8, Spearman > 0.6
Excelente: MAE < 0.5, Spearman > 0.75
```

---

## ⚙️ Score Final Integrado

Combina técnico + semántico:

```python
integrated_score = (
    rhyme_score * 0.25 +           # Técnico: rimas
    punchline_score * 0.25 +        # Semántico: remates
    cleverness_score * 0.25 +       # Semántico: ingenio
    response_score * 0.25           # Semántico: respuesta
)

# Rango: 1-5
```

Este es el score final que verá el frontend.

---

## 💰 Costos

Claude API es barata:

```
Input: $0.003 / 1M tokens
Output: $0.015 / 1M tokens

Por verso (típicamente 50-150 palabras = 80-250 tokens):
- 1 evaluación: ~$0.0005
- 3 evaluaciones: ~$0.0015

Para 1000 versos: ~$1.50
```

---

## 🎓 Decisiones de Diseño

### ¿Por qué multi-evaluación?

El LLM puede variar (temperature > 0). Haciendo 3 evaluaciones:

1. Promediamos para consistencia
2. Calculamos confidence basado en varianza
3. Detectamos inconsistencias

### ¿Por qué calibración contra humanos?

El LLM puede ser bueno pero no perfecto. Con anotaciones humanas podemos:

1. Validar que tiene sentido
2. Ajustar pesos si es necesario
3. Ser honest sobre limitaciones

### ¿Por qué estos 3 criterios?

- **Punchline**: El impacto inmediato
- **Cleverness**: La creatividad general
- **Response**: Cómo lidia con el rival

Juntos cubren "qué tan bien rapeó este verso"

---

## 🚨 Limitaciones Honesta

El LLM NO entiende:

- Referencias locales/culturales específicas
- Contexto político o social profundo
- Pronunciación perfec (solo ve texto)
- Intención vs resultado

Por eso la calibración humana es **crítica**.

---

## 📝 Variables de Entorno

```bash
# Obligatoria
ANTHROPIC_API_KEY=sk-ant-...

# Opcionales (tienen defaults)
CLAUDE_MODEL=claude-3-5-sonnet-20241022  # Usar modelo diferente
NUM_EVALUATIONS=3                        # Cambiar default de evaluaciones
```

---

## 📚 Ejemplo Completo

### Scenario: Evaluar battle completa

```bash
# 1. Batalla ya se procesó en Fase 2
# GET /api/battles/1 → 5 versos con RhymeMetric

# 2. Evaluar semánticamente cada verso
for verse_id in 1 2 3 4 5; do
  curl -X POST "http://localhost:8000/api/semantic/verses/$verse_id/evaluate-semantic" \
    -H "Content-Type: application/json" \
    -d '{
      "verse_id": '$verse_id',
      "context": "Batalla FMS Argentina. MC1 vs MC2",
      "num_evaluations": 3
    }'
done

# 3. Esperar ~2 minutos (3 evaluaciones x 5 versos)

# 4. Obtener scores finales para battle
curl "http://localhost:8000/api/battles/1/verses"

# Cada verso mostrará:
{
  "id": 1,
  "text": "...",
  "rhyme_metric": { ... },
  "semantic_metric": {
    "punchline_score": 4.2,
    "cleverness_score": 4.5,
    "response_score": 3.8,
    "integrated_score": 4.18
  }
}

# 5. Frontend puede mostrar batallacompletamente scores automáticos
```

---

## 🔗 Integración con MVP + Fase 2

| Feature         | MVP    | Fase 2 | Fase 3            |
| --------------- | ------ | ------ | ----------------- |
| Crowdsourcing   | ✅     | ✅     | ✅                |
| Rhyme analysis  | ✅     | ✅     | ✅                |
| Punchline score | Manual | N/A    | ✅ **Automático** |
| Cleverness      | Manual | N/A    | ✅ **Automático** |
| Response        | Manual | N/A    | ✅ **Automático** |
| Final score     | N/A    | N/A    | ✅ **Integrado**  |

---

## 🎉 Próximos Pasos

1. **Instalar:** `pip install -r requirements.txt`
2. **Configurar:** `export ANTHROPIC_API_KEY=...`
3. **Evaluar:** POST `/api/semantic/verses/{id}/evaluate-semantic`
4. **Calibrar:** Recopilar anotaciones humanas
5. **Mejorar:** Ajustar pesos según resultados

---

## 📞 Troubleshooting

### "InvalidAuthenticationError"

```
→ ANTHROPIC_API_KEY no configurada correctamente
→ Verificar: echo $ANTHROPIC_API_KEY (debe mostrar sk-ant-...)
```

### "Task timeout"

```
→ Evaluación tardó más de 30 min
→ Celery timeout de 30 min por defecto
→ Aumentar en app/workers/celery_app.py
```

### "LLM returned invalid JSON"

```
→ Claude no devolvió JSON válido
→ Reintentar o usar modelo diferente
→ Registrado en logs para debug
```

---

## ✅ Checklist Fase 3

- [x] LLM Judge module con Claude API
- [x] Semantic metrics model en BD
- [x] Celery tasks para evaluación
- [x] REST endpoints
- [x] Calibration framework
- [x] Integrated score calculation
- [x] Environment variable support
- [x] Error handling y logging
- [x] Documentación completa

---

**Fase 3 está 100% implementada y lista para usar!**

Antes de producción, recomendamos:

1. Calibrar con ~50-100 anotaciones humanas
2. Validar que MAE < 1.0
3. Verificar que Spearman > 0.5

Luego escalar a evaluaciones en batch.
