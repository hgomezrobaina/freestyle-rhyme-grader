"""
API routes for user ratings.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schema import UserRatingCreate, UserRatingResponse, UserRatingStats
from app.services.rating_service import RatingService

router = APIRouter()
rating_service = RatingService()


@router.post("/verse/{verse_id}", response_model=UserRatingResponse, status_code=status.HTTP_201_CREATED)
async def rate_verse(
    verse_id: int, rating_input: UserRatingCreate, db: Session = Depends(get_db)
):
    """
    Create a rating for a verse.

    Users provide their ratings for rima, ingenio, punchline, and respuesta.
    """
    # Verify verse exists
    from app.models.battle import Verse

    verse = db.query(Verse).filter(Verse.id == verse_id).first()
    if not verse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Verse not found"
        )

    try:
        rating = rating_service.create_rating(db, verse_id, rating_input)
        return rating
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating rating: {str(e)}",
        )


@router.get("/verse/{verse_id}/stats", response_model=UserRatingStats)
async def get_verse_rating_stats(verse_id: int, db: Session = Depends(get_db)):
    """
    Get average ratings for a verse from all users.

    Returns statistics like average rima score, average ingenio, etc.
    """
    stats = rating_service.get_verse_rating_stats(db, verse_id)
    return stats


@router.get("/verse/{verse_id}", response_model=list[UserRatingResponse])
async def get_verse_ratings(verse_id: int, db: Session = Depends(get_db)):
    """Get all user ratings for a specific verse."""
    ratings = rating_service.get_verse_ratings(db, verse_id)
    return ratings


@router.get("/user/{user_id}", response_model=list[UserRatingResponse])
async def get_user_ratings(user_id: str, db: Session = Depends(get_db)):
    """Get all ratings from a specific user."""
    ratings = rating_service.get_user_ratings(db, user_id)
    return ratings


@router.delete("/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rating(rating_id: int, db: Session = Depends(get_db)):
    """Delete a specific rating."""
    success = rating_service.delete_rating(db, rating_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found"
        )
    return None
