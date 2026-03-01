"""
API routes for battles.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schema import TextBattleInput, BattleResponse, BattleDetailResponse, BattleParticipantRename, BattleParticipantResponse
from app.models.mc_context import BattleParticipant
from app.services.battle_service import BattleService

router = APIRouter()
battle_service = BattleService()


@router.post("/text", response_model=BattleResponse, status_code=status.HTTP_201_CREATED)
async def create_battle_from_text(
    battle_input: TextBattleInput, db: Session = Depends(get_db)
):
    """
    Create a battle from already-transcribed text.

    This is the simplest endpoint - directly takes verses as input.
    Useful for initial testing and bootstrap with manually transcribed content.
    """
    try:
        battle = battle_service.create_battle_from_text(db, battle_input)
        return battle
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating battle: {str(e)}",
        )


@router.get("/{battle_id}", response_model=BattleDetailResponse)
async def get_battle(battle_id: int, db: Session = Depends(get_db)):
    """Get a battle with all its verses and metrics."""
    battle = battle_service.get_battle(db, battle_id)
    if not battle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Battle not found"
        )
    return battle


@router.get("/", response_model=list[BattleResponse])
async def list_battles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all battles with pagination."""
    battles = battle_service.get_all_battles(db, skip=skip, limit=limit)
    return battles


@router.patch(
    "/{battle_id}/participants/{participant_id}",
    response_model=BattleParticipantResponse,
)
async def rename_participant(
    battle_id: int,
    participant_id: int,
    rename: BattleParticipantRename,
    db: Session = Depends(get_db),
):
    """Rename a battle participant (e.g., from 'MC 1' to 'Aczino')."""
    participant = db.query(BattleParticipant).filter(
        BattleParticipant.id == participant_id,
        BattleParticipant.battle_id == battle_id,
    ).first()

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found in this battle",
        )

    participant.mc_name = rename.mc_name.strip()
    db.commit()
    db.refresh(participant)
    return participant
