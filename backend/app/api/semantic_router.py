"""
API routes for semantic evaluation endpoints (Fase 3).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.battle import Verse
from app.models.semantic import SemanticMetric, HumanJudgeAnnotation
from app.tasks.semantic_evaluation import evaluate_verse_semantic
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class SemanticEvaluationRequest(BaseModel):
    """Request to evaluate a verse semantically."""
    verse_id: int
    context: str = ""  # Optional context (opponent verse, battle info, etc)
    num_evaluations: int = 3  # Number of evaluations to average


class SemanticMetricResponse(BaseModel):
    """Response with semantic metrics."""
    verse_id: int
    punchline_score: float = None
    cleverness_score: float = None
    response_score: float = None
    punchline_confidence: float = None
    cleverness_confidence: float = None
    response_confidence: float = None
    integrated_score: float = None

    class Config:
        from_attributes = True


class HumanJudgeAnnotationInput(BaseModel):
    """Input for human judge annotation."""
    verse_id: int
    human_punchline_score: float  # 1-5
    human_cleverness_score: float  # 1-5
    human_response_score: float  # 1-5
    judge_id: str
    notes: str = None


@router.post("/verses/{verse_id}/evaluate-semantic", status_code=status.HTTP_202_ACCEPTED)
async def evaluate_verse_semantically(
    verse_id: int,
    request: SemanticEvaluationRequest,
    db: Session = Depends(get_db)
):
    """
    Queue a semantic evaluation task for a verse.

    This uses Claude LLM to evaluate:
    - Punchlines and remates
    - Cleverness and creativity
    - Response to opponent

    Returns immediately with task_id for polling progress.

    Args:
        verse_id: ID of the verse to evaluate
        request: Evaluation request with context and num_evaluations
        db: Database session

    Returns:
        Dictionary with task_id and status
    """
    try:
        # Verify verse exists
        verse = db.query(Verse).filter(Verse.id == verse_id).first()
        if not verse:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Verse not found"
            )

        # Check if already evaluated (optional - allow re-evaluation)
        existing = db.query(SemanticMetric).filter(
            SemanticMetric.verse_id == verse_id
        ).first()

        logger.info(f"Queuing semantic evaluation for verse {verse_id}")

        #Queue the task
        task = evaluate_verse_semantic.delay(
            verse_id=verse_id,
            context=request.context,
            num_evaluations=request.num_evaluations,
        )

        return {
            "task_id": task.id,
            "verse_id": verse_id,
            "status": "queued",
            "message": f"Semantic evaluation queued for verse {verse_id}. Check status with task_id.",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error queueing semantic evaluation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error queueing evaluation: {str(e)}"
        )


@router.get("/verses/{verse_id}/semantic-metrics", response_model=SemanticMetricResponse)
async def get_semantic_metrics(verse_id: int, db: Session = Depends(get_db)):
    """
    Get semantic evaluation metrics for a verse.

    Returns LLM evaluation scores if available.

    Args:
        verse_id: ID of the verse

    Returns:
        SemanticMetric with all evaluation scores
    """
    semantic_metric = db.query(SemanticMetric).filter(
        SemanticMetric.verse_id == verse_id
    ).first()

    if not semantic_metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Semantic metrics not found for this verse"
        )

    return semantic_metric


@router.post("/verses/{verse_id}/human-annotation")
async def annotate_verse_with_human_scores(
    verse_id: int,
    annotation: HumanJudgeAnnotationInput,
    db: Session = Depends(get_db)
):
    """
    Save human judge annotations for a verse.

    This is used for calibrating LLM scores against human judges.

    Args:
        verse_id: ID of the verse
        annotation: Human judge scores
        db: Database session

    Returns:
        Created annotation record
    """
    try:
        # Verify verse exists
        verse = db.query(Verse).filter(Verse.id == verse_id).first()
        if not verse:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Verse not found"
            )

        # Validate scores are 1-5
        for score in [
            annotation.human_punchline_score,
            annotation.human_cleverness_score,
            annotation.human_response_score,
        ]:
            if not (1 <= score <= 5):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Scores must be between 1 and 5"
                )

        # Save annotation
        human_annotation = HumanJudgeAnnotation(
            verse_id=verse_id,
            human_punchline_score=annotation.human_punchline_score,
            human_cleverness_score=annotation.human_cleverness_score,
            human_response_score=annotation.human_response_score,
            judge_id=annotation.judge_id,
            notes=annotation.notes,
        )

        db.add(human_annotation)
        db.commit()

        logger.info(f"Human annotation saved for verse {verse_id} by judge {annotation.judge_id}")

        return {
            "id": human_annotation.id,
            "verse_id": verse_id,
            "judge_id": annotation.judge_id,
            "status": "saved",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving human annotation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving annotation: {str(e)}"
        )


@router.get("/verses/{verse_id}/comparison")
async def compare_llm_vs_human(verse_id: int, db: Session = Depends(get_db)):
    """
    Compare LLM scores vs human judge annotations for a verse.

    Useful for calibration and validation.

    Args:
        verse_id: ID of the verse

    Returns:
        Comparison of LLM vs human scores
    """
    semantic_metric = db.query(SemanticMetric).filter(
        SemanticMetric.verse_id == verse_id
    ).first()

    human_annotations = db.query(HumanJudgeAnnotation).filter(
        HumanJudgeAnnotation.verse_id == verse_id
    ).all()

    if not semantic_metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM metrics not found"
        )

    if not human_annotations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No human annotations found"
        )

    # Calculate averages from human judges
    human_avg = {
        "punchline": sum(h.human_punchline_score for h in human_annotations) / len(human_annotations),
        "cleverness": sum(h.human_cleverness_score for h in human_annotations) / len(human_annotations),
        "response": sum(h.human_response_score for h in human_annotations) / len(human_annotations),
    }

    # Calculate differences
    differences = {
        "punchline_diff": (semantic_metric.punchline_score - human_avg["punchline"]) if semantic_metric.punchline_score else None,
        "cleverness_diff": (semantic_metric.cleverness_score - human_avg["cleverness"]) if semantic_metric.cleverness_score else None,
        "response_diff": (semantic_metric.response_score - human_avg["response"]) if semantic_metric.response_score else None,
    }

    return {
        "verse_id": verse_id,
        "llm_scores": {
            "punchline": semantic_metric.punchline_score,
            "cleverness": semantic_metric.cleverness_score,
            "response": semantic_metric.response_score,
        },
        "human_avg_scores": human_avg,
        "differences": differences,
        "num_human_judges": len(human_annotations),
    }
