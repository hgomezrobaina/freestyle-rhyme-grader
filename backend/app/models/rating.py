from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class UserRating(Base):
    __tablename__ = "user_ratings"

    id = Column(Integer, primary_key=True, index=True)
    verse_id = Column(Integer, ForeignKey("verses.id"), index=True)
    user_id = Column(String)  # Could be anonymous ID or user UUID

    # Ratings for different dimensions (1-5 scale)
    rating_rhyme = Column(Float, nullable=True)  # How good are the rhymes?
    rating_ingenio = Column(Float, nullable=True)  # How clever/witty?
    rating_punchline = Column(Float, nullable=True)  # How strong are the punchlines?
    rating_respuesta = Column(Float, nullable=True)  # How well does it respond to opponent?

    # Metadata
    comment = Column(String, nullable=True)  # Optional comment from rater
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    verse = relationship("Verse", back_populates="ratings")
