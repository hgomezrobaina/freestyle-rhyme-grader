"""
Rating service - handles user ratings for verses.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.rating import UserRating
from app.models.schema import UserRatingCreate, UserRatingStats
from typing import List, Optional


class RatingService:
    """Service for managing user ratings."""

    def create_rating(self, db: Session, verse_id: int, rating_input: UserRatingCreate) -> UserRating:
        """
        Create a new rating for a verse.

        Args:
            db: Database session
            verse_id: ID of the verse being rated
            rating_input: Rating data

        Returns:
            Created UserRating object
        """
        rating = UserRating(
            verse_id=verse_id,
            user_id=rating_input.user_id,
            rating_rhyme=rating_input.rating_rhyme,
            rating_ingenio=rating_input.rating_ingenio,
            rating_punchline=rating_input.rating_punchline,
            rating_respuesta=rating_input.rating_respuesta,
            comment=rating_input.comment,
        )
        db.add(rating)
        db.commit()
        return rating

    def get_verse_ratings(self, db: Session, verse_id: int) -> List[UserRating]:
        """Get all ratings for a specific verse."""
        return db.query(UserRating).filter(UserRating.verse_id == verse_id).all()

    def get_verse_rating_stats(self, db: Session, verse_id: int) -> UserRatingStats:
        """
        Get average ratings for a verse.

        Args:
            db: Database session
            verse_id: ID of the verse

        Returns:
            UserRatingStats with average ratings
        """
        ratings = self.get_verse_ratings(db, verse_id)

        if not ratings:
            return UserRatingStats(
                verse_id=verse_id,
                avg_rating_rhyme=None,
                avg_rating_ingenio=None,
                avg_rating_punchline=None,
                avg_rating_respuesta=None,
                total_ratings=0,
            )

        # Calculate averages
        avg_rhyme = sum(r.rating_rhyme for r in ratings if r.rating_rhyme) / len(
            [r for r in ratings if r.rating_rhyme]
        ) if any(r.rating_rhyme for r in ratings) else None

        avg_ingenio = sum(r.rating_ingenio for r in ratings if r.rating_ingenio) / len(
            [r for r in ratings if r.rating_ingenio]
        ) if any(r.rating_ingenio for r in ratings) else None

        avg_punchline = sum(r.rating_punchline for r in ratings if r.rating_punchline) / len(
            [r for r in ratings if r.rating_punchline]
        ) if any(r.rating_punchline for r in ratings) else None

        avg_respuesta = sum(r.rating_respuesta for r in ratings if r.rating_respuesta) / len(
            [r for r in ratings if r.rating_respuesta]
        ) if any(r.rating_respuesta for r in ratings) else None

        return UserRatingStats(
            verse_id=verse_id,
            avg_rating_rhyme=round(avg_rhyme, 2) if avg_rhyme else None,
            avg_rating_ingenio=round(avg_ingenio, 2) if avg_ingenio else None,
            avg_rating_punchline=round(avg_punchline, 2) if avg_punchline else None,
            avg_rating_respuesta=round(avg_respuesta, 2) if avg_respuesta else None,
            total_ratings=len(ratings),
        )

    def delete_rating(self, db: Session, rating_id: int) -> bool:
        """Delete a rating."""
        rating = db.query(UserRating).filter(UserRating.id == rating_id).first()
        if rating:
            db.delete(rating)
            db.commit()
            return True
        return False

    def get_user_ratings(self, db: Session, user_id: str) -> List[UserRating]:
        """Get all ratings from a specific user."""
        return db.query(UserRating).filter(UserRating.user_id == user_id).all()
