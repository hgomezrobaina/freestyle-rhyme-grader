"""
Battle service - handles CRUD operations for battles.
"""

from sqlalchemy.orm import Session
from app.models.battle import Battle, Verse, RhymeMetric, BattleStatus, BattleSourceType
from app.models.schema import BattleCreate, VerseCreate, TextBattleInput
from analysis.rhyme.metrics import RhymeMetricsCalculator
from typing import Optional, List


class BattleService:
    """Service for managing battles."""

    def __init__(self):
        self.metrics_calculator = RhymeMetricsCalculator()

    def create_battle_from_text(
        self, 
        db: Session, 
        battle_input: TextBattleInput
    ) -> Battle:
        """
        Create a battle from text input (already transcribed).

        Args:
            db: Database session
            battle_input: Battle data with verses

        Returns:
            Created Battle object
        """
        # Create battle
        battle = Battle(
            title=battle_input.title,
            description=battle_input.description,
            source_type=BattleSourceType.TEXT,
            status=BattleStatus.PENDING,
        )
        db.add(battle)
        db.flush()  # Flush to get the battle ID

        # Create verses and analyze rhymes
        for verse_input in battle_input.verses:
            verse = Verse(
                battle_id=battle.id,
                verse_number=verse_input.verse_number,
                speaker=verse_input.speaker,
                text=verse_input.text,
                duration_seconds=verse_input.duration_seconds,
            )
            db.add(verse)
            db.flush()  # Flush to get verse ID

            # Calculate rhyme metrics
            metrics = self.metrics_calculator.calculate_metrics(verse.text)

            rhyme_metric = RhymeMetric(
                verse_id=verse.id,
                rhyme_density=metrics["rhyme_density"],
                multisyllabic_ratio=metrics["multisyllabic_ratio"],
                internal_rhymes_count=metrics["internal_rhymes_count"],
                rhyme_diversity=metrics["rhyme_diversity"],
                total_syllables=metrics["total_syllables"],
                rhymed_syllables=metrics["rhymed_syllables"],
                rhyme_types=metrics["rhyme_types"],
            )
            db.add(rhyme_metric)

        # Mark battle as completed
        battle.status = BattleStatus.COMPLETED

        db.commit()
        return battle

    def get_battle(self, db: Session, battle_id: int) -> Optional[Battle]:
        """Get a battle by ID."""
        return db.query(Battle).filter(Battle.id == battle_id).first()

    def get_all_battles(self, db: Session, skip: int = 0, limit: int = 100) -> List[Battle]:
        """Get all battles with pagination."""
        return db.query(Battle).offset(skip).limit(limit).all()

    def get_battle_verses(self, db: Session, battle_id: int) -> List[Verse]:
        """Get all verses of a battle."""
        return db.query(Verse).filter(Verse.battle_id == battle_id).all()

    def update_battle_status(
        self, db: Session, battle_id: int, status: BattleStatus
    ) -> Battle:
        """Update battle status."""
        battle = self.get_battle(db, battle_id)
        if battle:
            battle.status = status
            db.commit()
        return battle

    def delete_battle(self, db: Session, battle_id: int) -> bool:
        """Delete a battle and all its associated data."""
        battle = self.get_battle(db, battle_id)
        if battle:
            db.delete(battle)
            db.commit()
            return True
        return False
