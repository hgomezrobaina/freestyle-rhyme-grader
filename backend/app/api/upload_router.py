"""
API routes for uploading battle audio/video files.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schema import BattleResponse
from app.models.battle import Battle, BattleSourceType, BattleStatus
from app.services.battle_service import BattleService
from app.tasks.pipeline import process_pipeline
from app.config import get_settings
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
battle_service = BattleService()
settings = get_settings()

# Create upload directory if it doesn't exist
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.TEMP_DIR).mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac", ".mp4", ".mov", ".avi", ".mkv"}
MAX_FILE_SIZE = settings.MAX_FILE_SIZE


@router.post("/upload", response_model=BattleResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_battle_from_upload(
    file: UploadFile = File(...),
    title: str = None,
    description: str = None,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """
    Upload an audio or video file for battle processing.

    Supports: MP3, WAV, M4A, FLAC (audio) or MP4, MOV, AVI, MKV (video)

    This endpoint:
    1. Validates and saves the uploaded file
    2. Creates a battle record with status "processing"
    3. Queues processing (transcription, separation, diarization)
    4. Returns immediately with battle_id

    Args:
        file: Audio or video file
        title: Title for the battle
        description: Optional description
        db: Database session
        background_tasks: Background task runner

    Returns:
        Battle object with status "processing"
    """
    try:
        # Extract filename and validate extension
        if not title:
            title = file.filename.rsplit('.', 1)[0] or "Battle"

        filename = file.filename
        file_ext = Path(filename).suffix.lower()

        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Validate file size (check content-length before saving)
        if file.size and file.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_PAYLOAD_TOO_LARGE,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024**3):.1f}GB"
            )

        # Create battle record FIRST
        battle = Battle(
            title=title,
            description=description,
            source_type=BattleSourceType.UPLOAD,
            source_url=filename,  # Store original filename
            status=BattleStatus.PROCESSING,
        )
        db.add(battle)
        db.commit()
        db.refresh(battle)

        logger.info(f"Created battle {battle.id} from upload: {filename}")

        # Create temp directory for this battle
        battle_temp_dir = Path(settings.TEMP_DIR) / f"battle_{battle.id}"
        battle_temp_dir.mkdir(parents=True, exist_ok=True)

        # Save uploaded file
        file_path = battle_temp_dir / filename
        contents = await file.read()

        with open(file_path, "wb") as f:
            f.write(contents)

        logger.info(f"Saved uploaded file: {file_path}")

        # Queue processing task
        if background_tasks:
            background_tasks.add_task(
                process_pipeline,
                battle.id,
                "upload",
                str(file_path)
            )
        else:
            # Fallback: use Celery directly
            process_pipeline.delay(battle.id, "upload", str(file_path))

        logger.info(f"Queued processing for battle {battle.id}")

        return battle

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )


@router.get("/{battle_id}/status")
async def get_upload_battle_status(battle_id: int, db: Session = Depends(get_db)):
    """
    Get processing status of an uploaded battle.

    Returns:
        {
            "id": ...,
            "status": "pending|processing|completed|failed",
            "progress_message": "...",
            "verses_count": 0
        }
    """
    battle = battle_service.get_battle(db, battle_id)

    if not battle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Battle not found"
        )

    verses = battle_service.get_battle_verses(db, battle_id)

    # Map status to user-friendly message
    status_messages = {
        BattleStatus.PENDING: "Waiting to process...",
        BattleStatus.PROCESSING: "Processing audio...",
        BattleStatus.COMPLETED: "Completed!",
        BattleStatus.FAILED: "Processing failed",
    }

    return {
        "id": battle.id,
        "title": battle.title,
        "status": battle.status.value,
        "progress_message": status_messages.get(battle.status, "Unknown status"),
        "verses_count": len(verses),
        "created_at": battle.created_at,
        "updated_at": battle.updated_at,
    }
