"""
API routes for battles.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schema import TextBattleInput, BattleResponse, BattleDetailResponse
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
