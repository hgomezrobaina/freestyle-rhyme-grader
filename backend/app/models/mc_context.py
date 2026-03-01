"""
MC context models for Fase 4 - Contexto de MCs
Stores MC profiles, contributions, and historical data for better LLM evaluations.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class MCProfile(Base):
    """Profile of a rapero/MC with context for improved evaluations"""
    __tablename__ = "mc_profiles"

    id = Column(Integer, primary_key=True, index=True)
    stage_name = Column(String, unique=True, index=True)  # "Aczino", "Zasko", "Dtoke", etc
    real_name = Column(String, nullable=True)

    # Character and style
    signature_style = Column(String)  # "Agresivo", "Técnico", "Narrativo", "Abstracto", etc
    main_themes = Column(JSON)  # ["insultos", "cultural", "autobiográfico", "social", "pop_culture"]
    battle_count = Column(Integer, default=0)

    # Strengths and weaknesses (quality-checked by community)
    strengths = Column(JSON, default={})  # {"wordplay": True, "flow": True, "cultural_refs": True}
    weaknesses = Column(JSON, default={})  # {"punchlines": False, "response": True}

    # Character descriptions
    character_descriptions = Column(Text, nullable=True)  # "Es un villano que ataca el sistema..."

    # Notable references and signatures
    notable_references = Column(JSON, default=[])  # ["Star Wars", "películas", "literatura"]
    notable_battles = Column(JSON, default=[])  # [battle_id, battle_id, ...]
    famous_punchlines = Column(JSON, default=[])  # ["línea 1", "línea 2"]
    signature_moves = Column(JSON, default=[])  # ["doble sentido cinematográfico", "silabeo técnico"]

    # Career timeline
    career_start_year = Column(Integer, nullable=True)
    country = Column(String, nullable=True)  # "Argentina", "España", "México", etc
    federation = Column(String, nullable=True)  # "FMS", "BDM", "Aczino's Battle", etc

    # Profile metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    verses = relationship("Verse", back_populates="mc_profile", foreign_keys="Verse.mc_id")
    contributions = relationship("MCContextContribution", back_populates="mc_profile")
    head_to_head_battles = relationship("MCBattleHistory", back_populates="mc_profile")


class MCContextContribution(Base):
    """Community contributions to improve MC profiles"""
    __tablename__ = "mc_context_contributions"

    id = Column(Integer, primary_key=True, index=True)
    mc_id = Column(Integer, ForeignKey("mc_profiles.id"), index=True)

    # Type of contribution
    contribution_type = Column(String)  # "strength", "weakness", "character", "reference", "signature_move"

    # Content and evidence
    content = Column(Text)  # "Es muy bueno con metáforas de películas"
    evidence_url = Column(String, nullable=True)  # YouTube link
    evidence_battle_id = Column(Integer, nullable=True)  # For specific battle reference

    # Community voting
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)

    # Moderation
    contributor_id = Column(String)  # Username or user_id
    status = Column(String, default="pending")  # "pending", "approved", "rejected"
    approved_by = Column(String, nullable=True)  # Moderator who approved

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    mc_profile = relationship("MCProfile", back_populates="contributions")


class MCBattleHistory(Base):
    """Historical battles for each MC (for context and stats)"""
    __tablename__ = "mc_battle_history"

    id = Column(Integer, primary_key=True, index=True)
    mc_id = Column(Integer, ForeignKey("mc_profiles.id"), index=True)
    battle_id = Column(Integer, ForeignKey("battles.id"), index=True)

    # Opponents (can be multiple in team battles)
    opponent_mc_ids = Column(JSON)  # [id1, id2, ...] for flexibility

    # Battle outcome
    won = Column(Boolean, nullable=True)  # True=won, False=lost, None=no decision
    votes_for = Column(Integer, default=0)
    votes_against = Column(Integer, default=0)

    # Performance notes
    performance_rating = Column(Float, nullable=True)  # 1-5 rating of this battle
    notable_verses = Column(JSON, default=[])  # Verse IDs that were particularly good

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    mc_profile = relationship("MCProfile", back_populates="head_to_head_battles")


class BattleParticipant(Base):
    """Links MCs to battles - supports any number of participants and team configurations"""
    __tablename__ = "battle_participants"

    id = Column(Integer, primary_key=True, index=True)
    battle_id = Column(Integer, ForeignKey("battles.id"), index=True)
    mc_id = Column(Integer, ForeignKey("mc_profiles.id"), nullable=True)

    # Unfamiliar MC (not in database yet)
    mc_name = Column(String)  # "Name of MC" if not created as profile yet

    # Team/side information
    team_number = Column(Integer)  # 0=team1, 1=team2, etc for 2v2, 3v3 battles
    position_in_team = Column(Integer, default=0)  # For identifying order

    # Performance in this battle
    verses_count = Column(Integer, default=0)
    qualified = Column(Boolean, default=True)  # In case of DQ

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    battle = relationship("Battle", back_populates="participants")
    mc = relationship("MCProfile")
    verses = relationship("Verse", foreign_keys="Verse.participant_id", back_populates="participant")
