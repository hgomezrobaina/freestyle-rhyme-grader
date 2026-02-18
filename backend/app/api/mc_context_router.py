"""
API routes for MC profiles and context management (Fase 4)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.mc_context import MCProfile, MCContextContribution
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# === Pydantic Schemas ===


class MCProfileCreate(BaseModel):
    stage_name: str
    real_name: Optional[str] = None
    signature_style: str  # "Agresivo", "Técnico", "Narrativo", etc
    main_themes: List[str] = []
    strengths: dict = {}
    weaknesses: dict = {}
    character_descriptions: Optional[str] = None
    notable_references: List[str] = []
    famous_punchlines: List[str] = []
    signature_moves: List[str] = []
    career_start_year: Optional[int] = None
    country: Optional[str] = None
    federation: Optional[str] = None


class MCProfileResponse(BaseModel):
    id: int
    stage_name: str
    real_name: Optional[str]
    signature_style: str
    main_themes: List[str]
    strengths: dict
    weaknesses: dict
    battle_count: int
    famous_punchlines: List[str]
    signature_moves: List[str]

    class Config:
        from_attributes = True


class MCContextContributionCreate(BaseModel):
    contribution_type: str  # "strength", "weakness", "character", "reference", "signature_move"
    content: str
    evidence_url: Optional[str] = None
    evidence_battle_id: Optional[int] = None


class MCContextContributionResponse(BaseModel):
    id: int
    contribution_type: str
    content: str
    upvotes: int
    downvotes: int
    status: str

    class Config:
        from_attributes = True


# === Endpoints ===


@router.post("/mc", response_model=MCProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_mc_profile(
    profile: MCProfileCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new MC profile.
    Only admins should be able to do this in production.
    """
    # Check if MC already exists
    existing = db.query(MCProfile).filter(
        MCProfile.stage_name.ilike(profile.stage_name)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"MC '{profile.stage_name}' already exists"
        )

    mc = MCProfile(
        stage_name=profile.stage_name,
        real_name=profile.real_name,
        signature_style=profile.signature_style,
        main_themes=profile.main_themes,
        strengths=profile.strengths,
        weaknesses=profile.weaknesses,
        character_descriptions=profile.character_descriptions,
        notable_references=profile.notable_references,
        famous_punchlines=profile.famous_punchlines,
        signature_moves=profile.signature_moves,
        career_start_year=profile.career_start_year,
        country=profile.country,
        federation=profile.federation,
    )

    db.add(mc)
    db.commit()
    db.refresh(mc)

    logger.info(f"MC profile created: {profile.stage_name}")

    return mc


@router.get("/mc/{mc_name}", response_model=MCProfileResponse)
async def get_mc_profile(
    mc_name: str,
    db: Session = Depends(get_db)
):
    """Get MC profile by stage name"""
    mc = db.query(MCProfile).filter(
        MCProfile.stage_name.ilike(mc_name)
    ).first()

    if not mc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MC '{mc_name}' not found"
        )

    return mc


@router.get("/mc", response_model=List[MCProfileResponse])
async def list_mc_profiles(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List all MC profiles with pagination"""
    profiles = db.query(MCProfile).offset(skip).limit(limit).all()
    return profiles


@router.put("/mc/{mc_name}", response_model=MCProfileResponse)
async def update_mc_profile(
    mc_name: str,
    update: MCProfileCreate,
    db: Session = Depends(get_db)
):
    """Update MC profile (admin only in production)"""
    mc = db.query(MCProfile).filter(
        MCProfile.stage_name.ilike(mc_name)
    ).first()

    if not mc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MC '{mc_name}' not found"
        )

    # Update fields
    mc.real_name = update.real_name or mc.real_name
    mc.signature_style = update.signature_style or mc.signature_style
    mc.main_themes = update.main_themes or mc.main_themes
    mc.strengths = update.strengths or mc.strengths
    mc.weaknesses = update.weaknesses or mc.weaknesses
    mc.character_descriptions = update.character_descriptions or mc.character_descriptions
    mc.notable_references = update.notable_references or mc.notable_references
    mc.famous_punchlines = update.famous_punchlines or mc.famous_punchlines
    mc.signature_moves = update.signature_moves or mc.signature_moves
    mc.career_start_year = update.career_start_year or mc.career_start_year
    mc.country = update.country or mc.country
    mc.federation = update.federation or mc.federation

    db.commit()
    db.refresh(mc)

    logger.info(f"MC profile updated: {mc_name}")

    return mc


@router.post("/mc/{mc_name}/contribute", status_code=status.HTTP_202_ACCEPTED)
async def contribute_to_mc_profile(
    mc_name: str,
    contribution: MCContextContributionCreate,
    user_id: str = Query(..., description="User ID for tracking contributor"),
    db: Session = Depends(get_db)
):
    """
    Contribute context information about an MC.
    Contributions are moderated before appearing in evaluations.

    Types:
    - "strength": What the MC does very well
    - "weakness": Area where they struggle
    - "character": Description of their persona
    - "reference": Type of references they use
    - "signature_move": Their signature technique
    """
    mc = db.query(MCProfile).filter(
        MCProfile.stage_name.ilike(mc_name)
    ).first()

    if not mc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MC '{mc_name}' not found"
        )

    contrib = MCContextContribution(
        mc_id=mc.id,
        contribution_type=contribution.contribution_type,
        content=contribution.content,
        evidence_url=contribution.evidence_url,
        evidence_battle_id=contribution.evidence_battle_id,
        contributor_id=user_id,
        status="pending"  # Must be approved by moderators
    )

    db.add(contrib)
    db.commit()

    logger.info(
        f"MC context contribution from {user_id} for {mc_name} "
        f"(type: {contribution.contribution_type})"
    )

    return {
        "id": contrib.id,
        "status": "pending_approval",
        "message": "Thank you for contributing! Moderators will review your contribution."
    }


@router.get("/mc/{mc_name}/contributions", response_model=List[MCContextContributionResponse])
async def get_mc_contributions(
    mc_name: str,
    db: Session = Depends(get_db)
):
    """
    Get all approved community contributions for an MC.
    Sorted by upvotes.
    """
    mc = db.query(MCProfile).filter(
        MCProfile.stage_name.ilike(mc_name)
    ).first()

    if not mc:
        raise HTTPException(status_code=404, detail="MC not found")

    contribs = db.query(MCContextContribution).filter(
        (MCContextContribution.mc_id == mc.id),
        (MCContextContribution.status == "approved")
    ).order_by(
        MCContextContribution.upvotes.desc()
    ).all()

    return contribs


@router.post("/contributions/{contrib_id}/vote/{vote_type}")
async def vote_contribution(
    contrib_id: int,
    vote_type: str,
    db: Session = Depends(get_db)
):
    """
    Vote on a contribution (up or down).

    vote_type: "up" or "down"
    """
    if vote_type not in ["up", "down"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="vote_type must be 'up' or 'down'"
        )

    contrib = db.query(MCContextContribution).filter(
        MCContextContribution.id == contrib_id
    ).first()

    if not contrib:
        raise HTTPException(status_code=404, detail="Contribution not found")

    if vote_type == "up":
        contrib.upvotes += 1
    else:
        contrib.downvotes += 1

    db.commit()

    return {
        "upvotes": contrib.upvotes,
        "downvotes": contrib.downvotes,
        "net_votes": contrib.upvotes - contrib.downvotes
    }


@router.post("/contributions/{contrib_id}/approve")
async def approve_contribution(
    contrib_id: int,
    moderator_id: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Approve a pending contribution (moderator only).
    """
    contrib = db.query(MCContextContribution).filter(
        MCContextContribution.id == contrib_id
    ).first()

    if not contrib:
        raise HTTPException(status_code=404, detail="Contribution not found")

    if contrib.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Contribution is already {contrib.status}"
        )

    contrib.status = "approved"
    contrib.approved_by = moderator_id

    db.commit()

    logger.info(f"Contribution {contrib_id} approved by moderator {moderator_id}")

    return {"status": "approved"}


@router.post("/contributions/{contrib_id}/reject")
async def reject_contribution(
    contrib_id: int,
    moderator_id: str = Query(...),
    reason: str = Query("No reason provided"),
    db: Session = Depends(get_db)
):
    """
    Reject a pending contribution (moderator only).
    """
    contrib = db.query(MCContextContribution).filter(
        MCContextContribution.id == contrib_id
    ).first()

    if not contrib:
        raise HTTPException(status_code=404, detail="Contribution not found")

    if contrib.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Contribution is already {contrib.status}"
        )

    contrib.status = "rejected"
    contrib.approved_by = moderator_id

    db.commit()

    logger.info(f"Contribution {contrib_id} rejected by {moderator_id}: {reason}")

    return {"status": "rejected", "reason": reason}


@router.delete("/mc/{mc_name}")
async def delete_mc_profile(
    mc_name: str,
    db: Session = Depends(get_db)
):
    """
    Delete an MC profile (admin only).
    WARNING: This will cascade delete all verses from this MC.
    """
    mc = db.query(MCProfile).filter(
        MCProfile.stage_name.ilike(mc_name)
    ).first()

    if not mc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MC '{mc_name}' not found"
        )

    db.delete(mc)
    db.commit()

    logger.warning(f"MC profile deleted: {mc_name}")

    return {
        "deleted": True,
        "mc_name": mc_name,
        "warning": "This action deleted all associated data"
    }
