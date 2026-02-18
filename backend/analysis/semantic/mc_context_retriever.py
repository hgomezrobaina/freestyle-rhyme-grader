"""
MC Context Retriever - Fetches detailed context about MCs for LLM evaluations
Fase 4: Contexto para mejores evaluaciones semánticas
"""

from sqlalchemy.orm import Session
from app.models.mc_context import MCProfile, MCContextContribution, MCBattleHistory
from app.models.battle import Verse, Battle
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class MCContextRetriever:
    """Retrieves and formats MC context for LLM-based evaluations"""

    def __init__(self, db: Session):
        self.db = db

    def get_mc_context(self, mc_name: str, opponent_mc_name: str = None) -> Optional[Dict]:
        """
        Retrieves complete context about an MC for evaluation.

        Args:
            mc_name: Stage name of the MC (e.g., "Aczino", "Zasko")
            opponent_mc_name: Optional opponent name for head-to-head history

        Returns:
            Dictionary with formatted MC context or None if not found
        """
        mc = self.db.query(MCProfile).filter(
            MCProfile.stage_name.ilike(mc_name)
        ).first()

        if not mc:
            logger.warning(f"MC profile not found: {mc_name}")
            return None

        context = {
            "speaker": self._format_mc_profile(mc),
            "strengths_summary": mc.strengths,
            "weaknesses_summary": mc.weaknesses,
            "signature_style": mc.signature_style,
            "main_themes": mc.main_themes,
            "notable_references": mc.notable_references[:5],  # Top 5
            "famous_punchlines": mc.famous_punchlines[:3],  # Top 3
            "signature_moves": mc.signature_moves,
            "character_description": mc.character_descriptions,
            "total_battles": mc.battle_count,
            "federation": mc.federation,
            "country": mc.country,
        }

        # Get community-verified information
        approved_contributions = self._get_approved_contributions(mc.id)
        if approved_contributions:
            context["community_insights"] = approved_contributions

        # If opponent specified, get head-to-head record
        if opponent_mc_name:
            opponent = self.db.query(MCProfile).filter(
                MCProfile.stage_name.ilike(opponent_mc_name)
            ).first()

            if opponent:
                context["opponent"] = self._format_mc_profile(opponent)
                context["head_to_head"] = self._get_h2h_history(mc.id, opponent.id)

        return context

    def _format_mc_profile(self, mc: MCProfile) -> Dict:
        """Formats MC profile for inclusion in LLM prompts"""
        return {
            "name": mc.stage_name,
            "real_name": mc.real_name,
            "style": mc.signature_style,
            "themes": mc.main_themes,
            "strengths": list(mc.strengths.keys()) if mc.strengths else [],
            "weaknesses": list(mc.weaknesses.keys()) if mc.weaknesses else [],
            "famous_lines": mc.famous_punchlines[:3],
            "signature_moves": mc.signature_moves[:3],
            "career_years": f"{mc.career_start_year}-present" if mc.career_start_year else "Unknown",
            "federation": mc.federation,
            "country": mc.country,
            "total_battles": mc.battle_count,
        }

    def _get_h2h_history(self, mc1_id: int, mc2_id: int) -> Dict:
        """
        Gets direct head-to-head history between two MCs
        """
        battles = self.db.query(MCBattleHistory).filter(
            (MCBattleHistory.mc_id == mc1_id),
            (MCBattleHistory.opponent_mc_ids.contains(f'[{mc2_id}'))
        ).all()

        if not battles:
            return {"battles": 0, "head_to_head_record": "First encounter"}

        wins = sum(1 for b in battles if b.won)
        losses = len(battles) - wins

        recent = []
        for b in battles[-3:]:
            recent.append({
                "battle_id": b.battle_id,
                "result": "win" if b.won else "loss" if b.won is False else "draw",
                "performance_rating": b.performance_rating,
            })

        return {
            "total_battles": len(battles),
            "wins": wins,
            "losses": losses,
            "head_to_head_record": f"{wins}-{losses}",
            "recent_battles": recent,
        }

    def _get_approved_contributions(self, mc_id: int) -> List[Dict]:
        """
        Gets community-approved contributions about an MC.
        Ranked by upvotes.
        """
        contributions = self.db.query(MCContextContribution).filter(
            (MCContextContribution.mc_id == mc_id),
            (MCContextContribution.status == "approved")
        ).order_by(
            MCContextContribution.upvotes.desc()
        ).limit(10).all()

        if not contributions:
            return []

        return [
            {
                "type": c.contribution_type,
                "content": c.content,
                "upvotes": c.upvotes,
                "evidence_battle": c.evidence_battle_id,
            }
            for c in contributions
        ]

    def get_battle_context(self, battle_id: int) -> Optional[Dict]:
        """
        Gets complete battle context with all participants
        """
        battle = self.db.query(Battle).filter(Battle.id == battle_id).first()

        if not battle:
            return None

        # Get participants
        from app.models.mc_context import BattleParticipant
        participants = self.db.query(BattleParticipant).filter(
            BattleParticipant.battle_id == battle_id
        ).all()

        teams = {}
        for p in participants:
            team_key = f"team_{p.team_number}"
            if team_key not in teams:
                teams[team_key] = []

            mc_context = {}
            if p.mc_id:
                mc = self.db.query(MCProfile).filter(MCProfile.id == p.mc_id).first()
                if mc:
                    mc_context = self._format_mc_profile(mc)
            else:
                mc_context = {"name": p.mc_name}

            teams[team_key].append(mc_context)

        return {
            "battle_id": battle_id,
            "title": battle.title,
            "format": battle.battle_format.value if battle.battle_format else "1v1",
            "date": battle.battle_date.isoformat() if battle.battle_date else None,
            "year": battle.battle_year,
            "federation": battle.federation,
            "city": battle.city,
            "country": battle.country,
            "battle_type": battle.battle_type,
            "total_rounds": battle.total_rounds,
            "participants": teams,
            "status": battle.status.value if battle.status else None,
        }

    def get_verse_context(self, verse_id: int) -> Optional[Dict]:
        """
        Gets complete context for a verse including:
        - MC profile
        - Battle information
        - Opponent information
        """
        verse = self.db.query(Verse).filter(Verse.id == verse_id).first()

        if not verse:
            return None

        context = {
            "verse_id": verse_id,
            "verse_number": verse.verse_number,
            "round_number": verse.round_number,
            "text": verse.text,
        }

        # MC context
        if verse.mc_id:
            mc = self.db.query(MCProfile).filter(MCProfile.id == verse.mc_id).first()
            if mc:
                context["speaker"] = self._format_mc_profile(mc)

        # Battle context
        if verse.battle_id:
            battle = self.db.query(Battle).filter(Battle.id == verse.battle_id).first()
            if battle:
                context["battle"] = self.get_battle_context(battle.id)

                # Get opponent verse for response evaluation
                opponent_verses = self.db.query(Verse).filter(
                    (Verse.battle_id == verse.battle_id),
                    (Verse.verse_number > verse.verse_number),
                    (Verse.speaker != verse.speaker)
                ).order_by(Verse.verse_number).first()

                if opponent_verses:
                    context["opponent_verse"] = {
                        "text": opponent_verses.text,
                        "verse_number": opponent_verses.verse_number,
                    }
                    if opponent_verses.mc_id:
                        opponent_mc = self.db.query(MCProfile).filter(
                            MCProfile.id == opponent_verses.mc_id
                        ).first()
                        if opponent_mc:
                            context["opponent_speaker"] = self._format_mc_profile(opponent_mc)

        return context
