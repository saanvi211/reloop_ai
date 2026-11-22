from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import get_current_user
from backend.models import Assessment, User
from backend.schemas import RecommendationRead
from backend.serializers import recommendation_to_dict
from backend.services.assessments import regenerate_recommendation

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


def _owned_assessment(db: Session, user: User, assessment_id: int) -> Assessment:
    record = db.get(Assessment, assessment_id)
    if record is None or record.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")
    return record


@router.get("/{assessment_id}", response_model=RecommendationRead)
def read_recommendation(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    record = _owned_assessment(db, current_user, assessment_id)
    recommendation = record.recommendation
    if recommendation is None:
        recommendation = regenerate_recommendation(db, record)
    return recommendation_to_dict(recommendation)


@router.post("/{assessment_id}/generate", response_model=RecommendationRead)
def generate_for_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    record = _owned_assessment(db, current_user, assessment_id)
    recommendation = regenerate_recommendation(db, record)
    return recommendation_to_dict(recommendation)
