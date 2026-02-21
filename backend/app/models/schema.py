from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict
from app.models.battle import BattleStatus, BattleSourceType

# Battle Schemas
class BattleCreate(BaseModel):
    title: str
    description: Optional[str] = None
    source_type: BattleSourceType
    source_url: Optional[str] = None

class BattleParticipantResponse(BaseModel):
    id: int
    mc_name: str
    team_number: int
    position_in_team: int

    class Config:
        from_attributes = True

class BattleResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    source_type: BattleSourceType
    source_url: Optional[str] = None
    status: BattleStatus
    progress_step: Optional[str] = None
    battle_date: Optional[str] = None
    federation: Optional[str] = None
    total_rounds: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Verse Schemas
class VerseCreate(BaseModel):
    verse_number: int
    speaker: Optional[str] = None
    text: str
    duration_seconds: Optional[float] = None

class RhymeMetricResponse(BaseModel):
    id: int
    rhyme_density: float
    multisyllabic_ratio: float
    internal_rhymes_count: int
    rhyme_diversity: Optional[float]
    total_syllables: int
    rhymed_syllables: int
    rhyme_types: Optional[Dict]

    class Config:
        from_attributes = True

class VerseResponse(BaseModel):
    id: int
    battle_id: int
    verse_number: int
    speaker: Optional[str]
    text: str
    duration_seconds: Optional[float]
    round_number: Optional[int] = None
    rhyme_metric: Optional[RhymeMetricResponse]
    created_at: datetime

    class Config:
        from_attributes = True

class BattleDetailResponse(BattleResponse):
    verses: List[VerseResponse] = []
    participants: List[BattleParticipantResponse] = []

# User Rating Schemas
class UserRatingCreate(BaseModel):
    user_id: str
    rating_rhyme: Optional[float] = None
    rating_ingenio: Optional[float] = None
    rating_punchline: Optional[float] = None
    rating_respuesta: Optional[float] = None
    comment: Optional[str] = None

class UserRatingResponse(BaseModel):
    id: int
    verse_id: int
    user_id: str
    rating_rhyme: Optional[float]
    rating_ingenio: Optional[float]
    rating_punchline: Optional[float]
    rating_respuesta: Optional[float]
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class UserRatingStats(BaseModel):
    """Average ratings for a verse"""
    verse_id: int
    avg_rating_rhyme: Optional[float]
    avg_rating_ingenio: Optional[float]
    avg_rating_punchline: Optional[float]
    avg_rating_respuesta: Optional[float]
    total_ratings: int

# Text Battle Input Schema
class TextBattleInput(BaseModel):
    title: str
    description: Optional[str] = None
    verses: List[VerseCreate]
