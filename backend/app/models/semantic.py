"""
Semantic metrics model for LLM evaluation results.
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class SemanticMetric(Base):
    """
    Stores LLM evaluation results for a verse.
    """

    __tablename__ = "semantic_metrics"

    id = Column(Integer, primary_key=True, index=True)
    verse_id = Column(Integer, ForeignKey("verses.id"), index=True, unique=True)

    # Semantic scores (1-5)
    punchline_score = Column(Float, nullable=True)  # Remates e impacto
    cleverness_score = Column(Float, nullable=True)  # Ingenio general
    response_score = Column(Float, nullable=True)  # Respuesta al rival

    # Confidence scores (0-1) based on variance of evaluations
    punchline_confidence = Column(Float, nullable=True)
    cleverness_confidence = Column(Float, nullable=True)
    response_confidence = Column(Float, nullable=True)

    # Aggregated analysis
    punchline_analysis = Column(String, nullable=True)  # Best lines, etc
    cleverness_analysis = Column(String, nullable=True)  # Techniques detected
    response_analysis = Column(String, nullable=True)  # Connections to opponent

    # JSON storage for detailed data
    punchline_details = Column(JSON, nullable=True)  # {analyses, best_lines}
    cleverness_details = Column(JSON, nullable=True)  # {techniques, originality}
    response_details = Column(JSON, nullable=True)  # {connections_detected}

    # Final integrated score
    integrated_score = Column(Float, nullable=True)  # Weighted combination of all metrics

    # Metadata
    model_used = Column(String, default="claude-3-5-sonnet-20241022")
    num_evaluations = Column(Integer, default=1)  # How many times evaluated
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    verse = relationship("Verse", back_populates="semantic_metric", uselist=False)


class HumanJudgeAnnotation(Base):
    """
    Store human judge annotations for calibration.

    Used to validate LLM scores against human judges.
    """

    __tablename__ = "human_judge_annotations"

    id = Column(Integer, primary_key=True, index=True)
    verse_id = Column(Integer, ForeignKey("verses.id"), index=True)

    # Human judge scores (1-5)
    human_punchline_score = Column(Float)
    human_cleverness_score = Column(Float)
    human_response_score = Column(Float)

    # Metadata
    judge_id = Column(String)  # Anonymous judge identifier
    round_number = Column(Integer, nullable=True)
    battle_context = Column(String, nullable=True)
    notes = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    verse = relationship("Verse", uselist=False)
