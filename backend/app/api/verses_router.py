"""
API routes for verses.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schema import VerseResponse, RhymeMetricResponse
from app.services.battle_service import BattleService

router = APIRouter()
battle_service = BattleService()


@router.get("/battle/{battle_id}", response_model=list[VerseResponse])
async def get_battle_verses(battle_id: int, db: Session = Depends(get_db)):
    """
    Get all verses of a battle with their rhyme metrics.

    This is the main endpoint for the frontend to retrieve analyzed verses.
    """
    verses = battle_service.get_battle_verses(db, battle_id)

    if not verses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No verses found for this battle",
        )

    return verses


@router.get("/{verse_id}", response_model=VerseResponse)
async def get_verse(verse_id: int, db: Session = Depends(get_db)):
    """Get a specific verse with its metrics."""
    from app.models.battle import Verse

    verse = db.query(Verse).filter(Verse.id == verse_id).first()

    if not verse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Verse not found"
        )

    return verse


@router.get("/{verse_id}/rhyme-metrics", response_model=RhymeMetricResponse)
async def get_verse_rhyme_metrics(verse_id: int, db: Session = Depends(get_db)):
    """Get rhyme metrics for a specific verse."""
    from app.models.battle import RhymeMetric

    metrics = db.query(RhymeMetric).filter(RhymeMetric.verse_id == verse_id).first()

    if not metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rhyme metrics not found for this verse",
        )

    return metrics
