from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import get_current_user
from backend.models import Assessment, RecyclingHistory, User
from backend.schemas import (
    AssessmentCreate,
    AssessmentList,
    AssessmentRead,
    AssessmentUpdate,
    RecommendationRead,
)
from backend.serializers import assessment_to_dict, recommendation_to_dict
from backend.services.assessments import create_assessment, regenerate_recommendation, update_assessment

router = APIRouter(prefix="/assessments", tags=["Assessments"])


def _get_owned_assessment(db: Session, user: User, assessment_id: int) -> Assessment:
    record = db.get(Assessment, assessment_id)
    if record is None or record.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")
    return record


@router.get("", response_model=AssessmentList)
def list_assessments(
    q: str | None = Query(default=None, max_length=120),
    status_filter: str | None = Query(default=None, alias="status", max_length=40),
    pathway: str | None = Query(default=None, max_length=60),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    sort: str = Query(default="desc", pattern="^(asc|desc)$"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    filters = [Assessment.user_id == current_user.id]
    if q:
        term = f"%{q.strip()}%"
        filters.append(
            or_(
                Assessment.device.ilike(term),
                Assessment.brand.ilike(term),
                Assessment.model.ilike(term),
                Assessment.category.ilike(term),
            )
        )
    if status_filter:
        filters.append(Assessment.status == status_filter)
    if pathway:
        filters.append(Assessment.pathway == pathway)
    if date_from:
        filters.append(Assessment.assessment_date >= date_from)
    if date_to:
        filters.append(Assessment.assessment_date <= date_to)

    base = select(Assessment).where(*filters)
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    order = Assessment.assessment_date.asc() if sort == "asc" else Assessment.assessment_date.desc()
    records = db.scalars(base.order_by(order).limit(limit).offset(offset)).all()
    return {
        "items": [assessment_to_dict(record, include_recommendation=False) for record in records],
        "total": total,
    }


@router.post("", response_model=AssessmentRead, status_code=status.HTTP_201_CREATED)
def create_new_assessment(
    payload: AssessmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    record = create_assessment(db, current_user, payload)
    return assessment_to_dict(record)


@router.get("/{assessment_id}", response_model=AssessmentRead)
def get_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    record = _get_owned_assessment(db, current_user, assessment_id)
    return assessment_to_dict(record)


@router.patch("/{assessment_id}", response_model=AssessmentRead)
@router.put("/{assessment_id}", response_model=AssessmentRead)
def edit_assessment(
    assessment_id: int,
    payload: AssessmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    record = _get_owned_assessment(db, current_user, assessment_id)
    if not payload.model_dump(exclude_unset=True):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No assessment fields were provided.",
        )
    updated = update_assessment(db, current_user, record, payload)
    return assessment_to_dict(updated)


@router.delete("/{assessment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    record = _get_owned_assessment(db, current_user, assessment_id)
    db.execute(
        update(RecyclingHistory)
        .where(RecyclingHistory.assessment_id == record.id)
        .values(assessment_id=None)
    )
    db.delete(record)
    db.commit()
    return None


@router.get("/{assessment_id}/recommendation", response_model=RecommendationRead)
def get_recommendation(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    record = _get_owned_assessment(db, current_user, assessment_id)
    recommendation = record.recommendation
    if recommendation is None:
        recommendation = regenerate_recommendation(db, record)
    return recommendation_to_dict(recommendation)


@router.post("/{assessment_id}/recommendation", response_model=RecommendationRead)
def generate_recommendation(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    record = _get_owned_assessment(db, current_user, assessment_id)
    recommendation = regenerate_recommendation(db, record)
    return recommendation_to_dict(recommendation)
