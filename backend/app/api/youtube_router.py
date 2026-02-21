"""
API routes for YouTube battle creation.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schema import BattleResponse
from app.models.battle import Battle, BattleSourceType, BattleStatus
from app.services.battle_service import BattleService
from app.tasks.pipeline import process_pipeline
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
battle_service = BattleService()


class YouTubeBattleInput:
    """Schema for YouTube battle creation"""
    def __init__(self, url: str, title: str, description: str = None):
        self.url = url
        self.title = title
        self.description = description


@router.post("/youtube", response_model=BattleResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_battle_from_youtube(
    url: str,
    title: str,
    description: str = None,
    db: Session = Depends(get_db)
):
    """
    Create a battle from a YouTube URL.

    This endpoint:
    1. Creates a battle record with status "processing"
    2. Queues the video for download and transcription
    3. Returns immediately with battle_id

    The frontend should poll GET /api/battles/{battle_id} to monitor progress.

    Args:
        url: YouTube URL
        title: Title for the battle
        description: Optional description
        db: Database session
        background_tasks: Background task runner

    Returns:
        Battle object with status "processing"
    """
    # Validate URL
    if not url.startswith(("https://youtube.com", "https://www.youtube.com", "https://youtu.be")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid YouTube URL"
        )

    try:
        # Create battle record
        battle = Battle(
            title=title,
            description=description,
            source_type=BattleSourceType.YOUTUBE,
            source_url=url,
            status=BattleStatus.PROCESSING,
        )
        db.add(battle)
        db.commit()
        db.refresh(battle)

        logger.info(f"Created battle {battle.id} from YouTube URL: {url}")

        # Queue processing task via Celery
        process_pipeline.delay(battle.id, "youtube", url)

        logger.info(f"Queued processing for battle {battle.id}")

        return battle

    except Exception as e:
        logger.error(f"Error creating YouTube battle: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating battle: {str(e)}"
        )


@router.get("/{battle_id}/status")
async def get_battle_status(battle_id: int, db: Session = Depends(get_db)):
    """
    Get the current processing status of a battle.

    Useful for polling progress from the frontend.

    Returns:
        {
            "id": ...,
            "status": "pending|processing|completed|failed",
            "progress_message": "...",
            "verses_count": 0  # Once completed
        }
    """
    battle = battle_service.get_battle(db, battle_id)

    if not battle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Battle not found"
        )

    verses = battle_service.get_battle_verses(db, battle_id)

    return {
        "id": battle.id,
        "title": battle.title,
        "status": battle.status.value,
        "progress_step": battle.progress_step.value if battle.progress_step else None,
        "verses_count": len(verses),
        "created_at": battle.created_at,
        "updated_at": battle.updated_at,
    }
