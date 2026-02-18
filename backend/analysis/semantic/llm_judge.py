"""
LLM Judge - Semantic evaluation of rap verses using Claude API.

This module handles:
- Punchline evaluation (remates, creatividad)
- Wit/Cleverness evaluation (ingenio)
- Response to opponent (respuesta al rival)
- Multi-pass evaluation for calibration
"""

import logging
import json
import os
from typing import Optional, Dict, List
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class LLMJudge:
    """
    Judge verses using Claude API for semantic analysis.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM Judge.

        Args:
            api_key: Anthropic API key. If None, reads from ANTHROPIC_API_KEY env var.
        """
        if not api_key:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError(
                    "ANTHROPIC_API_KEY not provided and not found in environment"
                )

        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"

    def evaluate_punchline(
        self,
        verse_text: str,
        context: str = "",
        num_evaluations: int = 1,
    ) -> Dict:
        """
        Evaluate punchlines and wit in a verse.

        Args:
            verse_text: The verse to evaluate
            context: Additional context (battle info, opponent's verse, etc)
            num_evaluations: Number of evaluations to average (for calibration)

        Returns:
            Dictionary with punchline score and analysis
        """
        scores = []
        analyses = []

        for i in range(num_evaluations):
            try:
                prompt = self._build_punchline_prompt(verse_text, context)
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=500,
                    temperature=0.7 if num_evaluations > 1 else 0.3,
                    messages=[{"role": "user", "content": prompt}],
                )

                result_text = response.content[0].text
                result = self._parse_evaluation_response(result_text)

                scores.append(result.get("score", 0))
                analyses.append(result.get("analysis", ""))

                logger.info(f"Punchline evaluation {i+1}/{num_evaluations}: {result}")

            except Exception as e:
                logger.error(f"Punchline evaluation failed: {str(e)}")
                raise

        return {
            "punchline_score": sum(scores) / len(scores) if scores else 0,
            "score_range": (min(scores), max(scores)) if scores else (0, 0),
            "analyses": analyses,
            "confidence": self._calculate_confidence(scores),
        }

    def evaluate_response(
        self,
        verse_text: str,
        opponent_verse: str,
        context: str = "",
        num_evaluations: int = 1,
    ) -> Dict:
        """
        Evaluate how well a verse responds to the opponent.

        Args:
            verse_text: The verse being evaluated
            opponent_verse: What the opponent said
            context: Additional context
            num_evaluations: Number of evaluations for calibration

        Returns:
            Dictionary with response score and analysis
        """
        scores = []
        analyses = []
        connections = []

        for i in range(num_evaluations):
            try:
                prompt = self._build_response_prompt(
                    verse_text, opponent_verse, context
                )
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=600,
                    temperature=0.7 if num_evaluations > 1 else 0.3,
                    messages=[{"role": "user", "content": prompt}],
                )

                result_text = response.content[0].text
                result = self._parse_evaluation_response(result_text)

                scores.append(result.get("score", 0))
                analyses.append(result.get("analysis", ""))
                connections.extend(result.get("connections", []))

                logger.info(f"Response evaluation {i+1}/{num_evaluations}: {result}")

            except Exception as e:
                logger.error(f"Response evaluation failed: {str(e)}")
                raise

        return {
            "response_score": sum(scores) / len(scores) if scores else 0,
            "score_range": (min(scores), max(scores)) if scores else (0, 0),
            "analyses": analyses,
            "connections_detected": list(set(connections)),
            "confidence": self._calculate_confidence(scores),
        }

    def evaluate_cleverness(
        self,
        verse_text: str,
        context: str = "",
        num_evaluations: int = 1,
    ) -> Dict:
        """
        Evaluate overall cleverness and wit.

        Args:
            verse_text: The verse to evaluate
            context: Additional context
            num_evaluations: Number of evaluations for calibration

        Returns:
            Dictionary with cleverness score and analysis
        """
        scores = []
        analyses = []
        techniques = []

        for i in range(num_evaluations):
            try:
                prompt = self._build_cleverness_prompt(verse_text, context)
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=550,
                    temperature=0.7 if num_evaluations > 1 else 0.3,
                    messages=[{"role": "user", "content": prompt}],
                )

                result_text = response.content[0].text
                result = self._parse_evaluation_response(result_text)

                scores.append(result.get("score", 0))
                analyses.append(result.get("analysis", ""))
                techniques.extend(result.get("techniques", []))

                logger.info(f"Cleverness evaluation {i+1}/{num_evaluations}: {result}")

            except Exception as e:
                logger.error(f"Cleverness evaluation failed: {str(e)}")
                raise

        return {
            "cleverness_score": sum(scores) / len(scores) if scores else 0,
            "score_range": (min(scores), max(scores)) if scores else (0, 0),
            "analyses": analyses,
            "techniques_detected": list(set(techniques)),
            "confidence": self._calculate_confidence(scores),
        }

    def _build_punchline_prompt(self, verse: str, context: str) -> str:
        """Build prompt for punchline evaluation."""
        return f"""
Eres un juez experto de batallas de freestyle rap en español.
Evalúa esta verso en términos de PUNCHLINE (remates) e INGENIO.

Criterios:
- Punchline (1-5): ¿Tiene remates memorables y impactantes?
  * 1: Sin remates, líneas genéricas
  * 3: Algunos remates decentes
  * 5: Remates devastadores y muy creativos

- Ingenio (1-5): ¿Qué tan creativo y original es?
  * 1: Poco creativo, muy predecible
  * 3: Algunos dobles sentidos y referencias
  * 5: Muy ingenioso, referencias originales

VERSO A EVALUAR:
"{verse}"

{f"CONTEXTO: {context}" if context else ""}

Responde EN JSON VÁLIDO con:
{{
  "punchline_score": <número 1-5>,
  "cleverness_score": <número 1-5>,
  "score": <promedio>,
  "analysis": "<explicación breve en español>",
  "best_lines": ["línea 1", "línea 2"]
}}
"""

    def _build_response_prompt(
        self, verse: str, opponent_verse: str, context: str
    ) -> str:
        """Build prompt for response evaluation."""
        return f"""
Eres un juez experto de batallas de freestyle rap.
Evalúa qué tan bien este verso RESPONDE al del rival.

Criterios RESPUESTA AL RIVAL (1-5):
- 1: Ignora completamente al rival
- 2: Referencia vaga
- 3: Responde a algunos puntos
- 4: Contraataque directo y efectivo
- 5: Desmonta completamente al rival

LO QUE DIJO EL RIVAL:
"{opponent_verse}"

VERSO QUE RESPONDE:
"{verse}"

{f"CONTEXTO: {context}" if context else ""}

Responde EN JSON VÁLIDO:
{{
  "score": <número 1-5>,
  "analysis": "<explicación>",
  "connections": [
    {{"rival_said": "...", "mc_responded_with": "..."}},
  ],
  "effectiveness": "<destruyó|respondió bien|respondió parcialmente|no respondió>"
}}
"""

    def _build_cleverness_prompt(self, verse: str, context: str) -> str:
        """Build prompt for cleverness evaluation."""
        return f"""
Eres un juez experto de batallas de freestyle.
Evalúa la CREATIVIDAD E INGENIO general del verso.

Técnicas a buscar:
- Dobles sentidos (palabras con múltiples significados)
- Metáforas y analogías
- Referencias culturales
- Wordplay y juegos de palabras
- Paradojas e ironía
- Estructura narrativa

VERSO:
"{verse}"

{f"CONTEXTO: {context}" if context else ""}

Responde EN JSON VÁLIDO:
{{
  "score": <número 1-5>,
  "analysis": "<explicación>",
  "techniques": ["técnica1", "técnica2", ...],
  "originality": "<muy original|original|estándar|predecible>"
}}
"""

    def _parse_evaluation_response(self, response_text: str) -> Dict:
        """Parse JSON response from Claude."""
        try:
            # Try to extract JSON from response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                logger.warning(f"No JSON found in response: {response_text}")
                return {"score": 0, "analysis": response_text}

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {str(e)}")
            return {"score": 0, "analysis": response_text}

    def _calculate_confidence(self, scores: List[float]) -> float:
        """
        Calculate confidence based on variance of multiple evaluations.

        Args:
            scores: List of scores from multiple evaluations

        Returns:
            Confidence score (0-1)
        """
        if len(scores) <= 1:
            return 0.5

        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        std_dev = variance ** 0.5

        # Low variance = high confidence
        # max_std = 2 (range [1-5]) → confidence = 0
        # min_std = 0 → confidence = 1
        confidence = max(0, 1 - (std_dev / 2))
        return round(confidence, 2)

    # === FASE 4: Context-Aware Evaluations ===

    def evaluate_with_mc_context(
        self,
        verse_text: str,
        mc_context: Dict,
        opponent_context: Dict = None,
        num_evaluations: int = 3,
    ) -> Dict:
        """
        Evaluate all three dimensions (punchline, cleverness, response)
        considering the MC's style and history.

        Args:
            verse_text: The verse to evaluate
            mc_context: MC profile context from MCContextRetriever
            opponent_context: Optional opponent context
            num_evaluations: Number of evaluations to average

        Returns:
            Dictionary with all three scores and confidence
        """
        return {
            "punchline": self.evaluate_punchline_with_context(
                verse_text, mc_context, opponent_context, num_evaluations
            ),
            "cleverness": self.evaluate_cleverness_with_context(
                verse_text, mc_context, num_evaluations
            ),
            "response_opponent": opponent_context is not None,
        }

    def evaluate_punchline_with_context(
        self,
        verse_text: str,
        mc_context: Dict,
        opponent_context: Dict = None,
        num_evaluations: int = 3,
    ) -> Dict:
        """
        Evaluate punchline considering MC's signature style and strengths.
        """
        scores = []
        analyses = []

        for i in range(num_evaluations):
            try:
                prompt = self._build_contextual_punchline_prompt(
                    verse_text, mc_context, opponent_context
                )
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=600,
                    temperature=0.7 if num_evaluations > 1 else 0.3,
                    messages=[{"role": "user", "content": prompt}],
                )

                result_text = response.content[0].text
                result = self._parse_evaluation_response(result_text)

                scores.append(result.get("score", 0))
                analyses.append(result.get("analysis", ""))

                logger.info(
                    f"Contextual punchline evaluation {i+1}/{num_evaluations}: {result}"
                )

            except Exception as e:
                logger.error(f"Contextual punchline evaluation failed: {str(e)}")
                raise

        return {
            "punchline_score": sum(scores) / len(scores) if scores else 0,
            "score_range": (min(scores), max(scores)) if scores else (0, 0),
            "analyses": analyses,
            "confidence": self._calculate_confidence(scores),
        }

    def evaluate_cleverness_with_context(
        self,
        verse_text: str,
        mc_context: Dict,
        num_evaluations: int = 3,
    ) -> Dict:
        """
        Evaluate cleverness/creativity considering MC's known style.
        E.g., Aczino = cinematographic references, Zasko = direct wordplay.
        """
        scores = []
        analyses = []
        techniques = []

        for i in range(num_evaluations):
            try:
                prompt = self._build_contextual_cleverness_prompt(
                    verse_text, mc_context
                )
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=650,
                    temperature=0.7 if num_evaluations > 1 else 0.3,
                    messages=[{"role": "user", "content": prompt}],
                )

                result_text = response.content[0].text
                result = self._parse_evaluation_response(result_text)

                scores.append(result.get("score", 0))
                analyses.append(result.get("analysis", ""))
                techniques.extend(result.get("techniques", []))

                logger.info(
                    f"Contextual cleverness evaluation {i+1}/{num_evaluations}: {result}"
                )

            except Exception as e:
                logger.error(f"Contextual cleverness evaluation failed: {str(e)}")
                raise

        return {
            "cleverness_score": sum(scores) / len(scores) if scores else 0,
            "score_range": (min(scores), max(scores)) if scores else (0, 0),
            "analyses": analyses,
            "techniques_detected": list(set(techniques)),
            "fits_style": self._assess_style_consistency(scores),
            "confidence": self._calculate_confidence(scores),
        }

    def _build_contextual_punchline_prompt(
        self, verse: str, mc_context: Dict, opponent_context: Dict = None
    ) -> str:
        """Build prompt considering MC's profile and style."""
        prompt = f"""Eres juez experto de freestyle rap español. Evalúa el PUNCHLINE/REMATE de este verso considerando el estilo y trayectoria del MC.

### MC RAPPEANDO:
**Nombre:** {mc_context['speaker']['name']}
**Estilo:** {mc_context['signature_style']}
**Temas:** {', '.join(mc_context['main_themes'][:5])}
**Fortalezas conocidas:** {', '.join(mc_context['strengths_summary'].keys())}
**Líneas famosas:** {'; '.join(mc_context['famous_punchlines'][:2])}

"""
        if opponent_context:
            prompt += f"""### OPONENTE:
**Nombre:** {opponent_context['speaker']['name']}
**Estilo:** {opponent_context['signature_style']}
**Debilidades:** {', '.join(opponent_context['weaknesses_summary'].keys())}

"""

        prompt += f"""### VERSO A EVALUAR:
"{verse}"

### EVALUACIÓN:
Considerando que {mc_context['speaker']['name']} es {mc_context['signature_style']}, evalúa:

1. **Impacto del remate:** ¿Qué tan efectivo es el cierre?
2. **Consistencia con estilo:** ¿El tipo de remate es típico y efectivo para {mc_context['speaker']['name']}?
3. **Originalidad:** ¿Evita clichés conocidos?
4. **Efectividad contextual:** En el contexto de {mc_context['signature_style']}, ¿es un buen remate?

IMPORTANTE: Un remate que funciona para {mc_context['speaker']['name']} ({mc_context['signature_style']}) puede funcionar diferente para otro MC.

Responde EN JSON VÁLIDO:
{{
  "score": <número 1-5>,
  "analysis": "<explicación considerando su estilo>",
  "leverages_style": <true/false>,
  "originality_level": "<muy original|original|estándar|cliché>",
  "best_moment": "<descripción del mejor momento>"
}}
"""
        return prompt

    def _build_contextual_cleverness_prompt(
        self, verse: str, mc_context: Dict
    ) -> str:
        """Build prompt for cleverness considering MC's known techniques."""
        prompt = f"""Eres juez experto de freestyle. Evalúa INGENIO considerando el estilo específico de este MC.

### MC: {mc_context['speaker']['name']}
**Estilo:** {mc_context['signature_style']}
**Técnicas conocidas:** {'; '.join(mc_context['signature_moves'][:3]) if mc_context['signature_moves'] else 'General'}
**Temas frecuentes:** {', '.join(mc_context['main_themes'][:5])}
**Referencias características:** {', '.join(mc_context['notable_references'][:3])}

### VERSO:
"{verse}"

NOTA: Los MCPs tienen estilos distintos:
- Técnico: foco en silabeo, rimas complejas
- Narrativo: foco en historias, personajes
- Agresivo: foco en insultos directos
- Abstracto: foco en metáforas y capas

### EVALÚA:
1. **Dobles sentidos:** ¿Hay capas de significado?
2. **Referencias:** ¿Qué tipo? (películas, pop, cultural, autobiográfico)
3. **Técnica:** ¿Usa técnicas que conoce {mc_context['speaker']['name']}?
4. **Autenticidad:** ¿Encaja con su personaje?

Responde EN JSON:
{{
  "score": <1-5>,
  "analysis": "<análisis de ingenio>",
  "techniques": ["técnica1", "técnica2"],
  "reference_type": "<cine|literatura|pop|cultural|autobiográfico|otros>",
  "fits_character": <true/false>,
  "authenticity": "<muy auténtico|auténtico|fuera de carácter>"
}}
"""
        return prompt

    def _assess_style_consistency(self, scores: List[float]) -> str:
        """
        Assess if the cleverness/punchline is consistent with MC's known style.
        High variance might indicate they're doing something new (good or bad).
        """
        if len(scores) <= 1:
            return "unknown"

        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        std_dev = variance ** 0.5

        if std_dev < 0.5:
            return "consistent_with_style"
        elif std_dev < 1.0:
            return "mostly_consistent"
        else:
            return "experimenting_or_inconsistent"
