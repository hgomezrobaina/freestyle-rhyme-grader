from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON, Enum as SQLEnum, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum
from app.database import Base

class BattleStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class PipelineStep(str, enum.Enum):
    DOWNLOAD = "download"
    TRANSCRIBE = "transcribe"
    SEPARATE = "separate"
    DIARIZE = "diarize"
    ANALYZE = "analyze"

class BattleSourceType(str, enum.Enum):
    YOUTUBE = "youtube"
    UPLOAD = "upload"
    TEXT = "text"

class BattleFormat(str, enum.Enum):
    """Battle format for context"""
    ONE_VS_ONE = "1v1"
    TWO_VS_TWO = "2v2"
    THREE_VS_THREE = "3v3"
    THREE_VS_ONE = "3v1"
    ONE_VS_TWO = "1v2"
    MULTI = "multi"  # Any other format

class Battle(Base):
    __tablename__ = "battles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    source_type = Column(SQLEnum(BattleSourceType))
    status = Column(SQLEnum(BattleStatus), default=BattleStatus.PENDING, index=True)
    progress_step = Column(SQLEnum(PipelineStep), nullable=True, default=None)
    source_url = Column(String, nullable=True)  # YouTube URL, file path, etc.

    # Fase 4: Battle Context and Metadata
    battle_format = Column(SQLEnum(BattleFormat), default=BattleFormat.ONE_VS_ONE)  # 1v1, 2v2, etc
    battle_date = Column(Date, nullable=True)  # When the battle took place
    battle_year = Column(Integer, nullable=True)  # Year for quick filtering
    federation = Column(String, nullable=True)  # "FMS", "BDM", "Aczino's Circuit", etc
    city = Column(String, nullable=True)  # "Buenos Aires", "Madrid", etc
    country = Column(String, nullable=True)  # "Argentina", "España", etc

    # Battle structure
    total_rounds = Column(Integer, nullable=True)  # Number of rounds in battle
    round_duration_seconds = Column(Float, nullable=True)  # Typical length per round

    # Results and notes
    winner_team = Column(Integer, nullable=True)  # 0 for team1, 1 for team2, None if undecided
    battle_type = Column(String, nullable=True)  # "Octavos", "Cuartos", "Semifinal", "Final", "Clasificatoria"

    # Additional metadata as JSON for flexibility
    battle_metadata = Column("metadata", JSON, default={})  # {"judges": [...], "audience_votes": 0, "notable_moments": [...]}

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    verses = relationship("Verse", back_populates="battle", cascade="all, delete-orphan")
    participants = relationship("BattleParticipant", back_populates="battle", cascade="all, delete-orphan")

class Verse(Base):
    __tablename__ = "verses"

    id = Column(Integer, primary_key=True, index=True)
    battle_id = Column(Integer, ForeignKey("battles.id"), index=True)
    verse_number = Column(Integer)  # Order in the battle
    speaker = Column(String, nullable=True)  # MC1, MC2, or name

    # Fase 4: Link to MC profile for context
    mc_id = Column(Integer, ForeignKey("mc_profiles.id"), nullable=True)

    text = Column(String)  # The actual rap text
    duration_seconds = Column(Float, nullable=True)  # Duration of this verse
    round_number = Column(Integer, nullable=True)  # Which round of battle
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    battle = relationship("Battle", back_populates="verses")
    mc_profile = relationship("MCProfile", foreign_keys=[mc_id], back_populates="verses")
    rhyme_metric = relationship("RhymeMetric", back_populates="verse", uselist=False, cascade="all, delete-orphan")
    semantic_metric = relationship("SemanticMetric", back_populates="verse", uselist=False, cascade="all, delete-orphan")  # Fase 3
    ratings = relationship("UserRating", back_populates="verse", cascade="all, delete-orphan")

class RhymeMetric(Base):
    __tablename__ = "rhyme_metrics"

    id = Column(Integer, primary_key=True, index=True)
    verse_id = Column(Integer, ForeignKey("verses.id"), index=True, unique=True)

    # Metrics
    rhyme_density = Column(Float)  # sílabas_rimadas / total_sílabas
    multisyllabic_ratio = Column(Float)  # rimas_multi / total_rimas
    internal_rhymes_count = Column(Integer)  # Number of internal rhymes
    rhyme_diversity = Column(Float, nullable=True)  # Variety of rhyme schemes
    total_syllables = Column(Integer)  # Total syllables in verse
    rhymed_syllables = Column(Integer)  # Number of syllables that rhyme

    # Detailed breakdown
    rhyme_types = Column(JSON, nullable=True)  # {"consonant": 5, "assonant": 2, "mosaic": 1}

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    verse = relationship("Verse", back_populates="rhyme_metric")
