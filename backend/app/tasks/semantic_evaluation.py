"""
Semantic evaluation tasks using Claude LLM.
"""

import logging
from app.workers.celery_app import celery_app
from app.database import SessionLocal
from app.models.battle import Verse
from app.models.semantic import SemanticMetric
from analysis.semantic.llm_judge import LLMJudge
import os

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="tasks.evaluate_verse_semantic")
def evaluate_verse_semantic(
    self,
    verse_id: int,
    context: str = "",
    num_evaluations: int = 3,
) -> dict:
    """
    Evaluate a verse semantically (punchline, cleverness, response potential).

    Args:
        verse_id: ID of the verse to evaluate
        context: Additional context (battle info, opponent verse, etc)
        num_evaluations: Number of evaluations to average

    Returns:
        Dictionary with semantic metrics
    """
    def _update(state, meta):
        if self.request.id:
            self.update_state(state=state, meta=meta)

    db = SessionLocal()
    try:
        logger.info(f"Starting semantic evaluation for verse {verse_id}")
        _update("PROCESSING", {"status": "Loading LLM model..."})

        # Get the verse
        verse = db.query(Verse).filter(Verse.id == verse_id).first()
        if not verse:
            raise ValueError(f"Verse {verse_id} not found")

        logger.info(f"Evaluating verse: {verse.text[:100]}...")

        # Initialize LLM Judge
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        judge = LLMJudge(api_key=api_key)

        # Evaluate punchlines
        logger.info("Evaluating punchlines...")
        _update("PROCESSING", {"status": "Evaluating punchlines..."})
        punchline_result = judge.evaluate_punchline(
            verse.text,
            context=context,
            num_evaluations=num_evaluations,
        )

        # Evaluate cleverness
        logger.info("Evaluating cleverness...")
        _update("PROCESSING", {"status": "Evaluating cleverness..."})
        cleverness_result = judge.evaluate_cleverness(
            verse.text,
            context=context,
            num_evaluations=num_evaluations,
        )

        # Evaluate response potential
        logger.info("Evaluating response potential...")
        _update("PROCESSING", {"status": "Evaluating response..."})

        # For response evaluation, we need opponent verse from context
        opponent_verse = ""
        if context:
            # Try to extract opponent verse from context
            # Format expected: "Opponent verse: [text]"
            if "Opponent verse:" in context:
                opponent_verse = context.split("Opponent verse:")[1].strip()

        response_result = {}
        if opponent_verse:
            response_result = judge.evaluate_response(
                verse.text,
                opponent_verse=opponent_verse,
                context=context,
                num_evaluations=num_evaluations,
            )
        else:
            logger.warning("No opponent verse found in context, skipping response evaluation")
            response_result = {
                "response_score": None,
                "response_confidence": 0,
                "analyses": [],
                "connections_detected": [],
            }

        logger.info("Evaluations completed, saving to database...")

        # Save to database
        semantic_metric = db.query(SemanticMetric).filter(
            SemanticMetric.verse_id == verse_id
        ).first()

        if not semantic_metric:
            semantic_metric = SemanticMetric(verse_id=verse_id)
            db.add(semantic_metric)

        # Update with evaluation results
        semantic_metric.punchline_score = punchline_result.get("punchline_score")
        semantic_metric.punchline_confidence = punchline_result.get("confidence")
        semantic_metric.punchline_details = {
            "analyses": punchline_result.get("analyses", []),
            "score_range": punchline_result.get("score_range"),
        }

        semantic_metric.cleverness_score = cleverness_result.get("cleverness_score")
        semantic_metric.cleverness_confidence = cleverness_result.get("confidence")
        semantic_metric.cleverness_details = {
            "analyses": cleverness_result.get("analyses", []),
            "techniques": cleverness_result.get("techniques_detected", []),
            "score_range": cleverness_result.get("score_range"),
        }

        semantic_metric.response_score = response_result.get("response_score")
        semantic_metric.response_confidence = response_result.get("confidence", 0)
        semantic_metric.response_details = {
            "analyses": response_result.get("analyses", []),
            "connections": response_result.get("connections_detected", []),
            "score_range": response_result.get("score_range", (0, 0)),
        }

        semantic_metric.num_evaluations = num_evaluations

        # Calculate integrated score (weighted average)
        semantic_metric.integrated_score = calculate_integrated_score(
            rhyme_density=0,  # Would come from RhymeMetric
            punchline_score=semantic_metric.punchline_score,
            cleverness_score=semantic_metric.cleverness_score,
            response_score=semantic_metric.response_score,
        )

        db.commit()
        logger.info(f"Semantic evaluation saved for verse {verse_id}")

        return {
            "verse_id": verse_id,
            "punchline_score": semantic_metric.punchline_score,
            "cleverness_score": semantic_metric.cleverness_score,
            "response_score": semantic_metric.response_score,
            "integrated_score": semantic_metric.integrated_score,
            "status": "completed",
        }

    except Exception as e:
        logger.error(f"Semantic evaluation failed for verse {verse_id}: {str(e)}", exc_info=True)
        raise

    finally:
        db.close()


@celery_app.task(bind=True, name="tasks.calibrate_llm_scores")
def calibrate_llm_scores(self, battles_count: int = 10) -> dict:
    """
    Calibrate LLM scores against human judge annotations.

    Calculates:
    - Mean Absolute Error (MAE)
    - Spearman correlation
    - Per-dimension accuracy

    Args:
        battles_count: Number of battles to compare

    Returns:
        Calibration metrics
    """
    def _update(state, meta):
        if self.request.id:
            self.update_state(state=state, meta=meta)

    db = SessionLocal()
    try:
        logger.info("Starting LLM calibration against human judges")
        _update("PROCESSING", {"status": "Gathering annotations..."})

        from app.models.semantic import HumanJudgeAnnotation
        from scipy.stats import spearmanr
        import numpy as np

        # Get verses with both LLM and human evaluations
        verses_with_both = db.query(Verse).filter(
            Verse.semantic_metric != None,  # Has LLM scores
        ).all()

        logger.info(f"Found {len(verses_with_both)} verses with LLM evaluations")

        # For each dimension, calculate metrics
        calibration_results = {
            "punchline": {},
            "cleverness": {},
            "response": {},
            "overall": {},
        }

        if len(verses_with_both) > 0:
            # This is simplified - in production would compare against human_judge_annotations
            logger.warning("Calibration requires human judge annotations - not yet available")

            calibration_results["status"] = "partial"
            calibration_results["note"] = "Waiting for human judge annotations"
        else:
            calibration_results["status"] = "no_data"

        logger.info(f"Calibration complete: {calibration_results}")
        return calibration_results

    except Exception as e:
        logger.error(f"Calibration failed: {str(e)}", exc_info=True)
        raise

    finally:
        db.close()


def calculate_integrated_score(
    rhyme_density: float = 0,
    punchline_score: float = 0,
    cleverness_score: float = 0,
    response_score: float = 0,
    weights: dict = None,
) -> float:
    """
    Calculate integrated final score combining technical and semantic metrics.

    Default weights:
    - Rhyme technical: 25%
    - Punchline: 25%
    - Cleverness: 25%
    - Response: 25%

    Args:
        rhyme_density: Rhyme density (0-1 scale, needs normalization)
        punchline_score: Punchline score (1-5)
        cleverness_score: Cleverness score (1-5)
        response_score: Response score (1-5)
        weights: Custom weights dictionary

    Returns:
        Integrated score (1-5)
    """
    if weights is None:
        weights = {
            "rhyme": 0.25,
            "punchline": 0.25,
            "cleverness": 0.25,
            "response": 0.25,
        }

    # Normalize rhyme_density to 1-5 scale
    # rhyme_density 0.30 = 5 stars, 0.15 = 3.5 stars, etc
    rhyme_score = min(5, (rhyme_density / 0.30) * 5) if rhyme_density > 0 else 2.5

    # Handle None values
    scores = {
        "rhyme": rhyme_score,
        "punchline": punchline_score or 2.5,
        "cleverness": cleverness_score or 2.5,
        "response": response_score or 2.5,
    }

    # Calculate weighted sum
    integrated = sum(scores[key] * weights[key] for key in scores.keys())

    return round(integrated, 2)
