from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import get_current_user
from backend.models import Assessment, Partner, RecyclingHistory, User
from backend.schemas import (
    HistoryCreate,
    HistoryList,
    HistoryRead,
    HistorySummary,
    HistoryUpdate,
)
from backend.serializers import history_to_dict
from backend.services.assessments import SafetyViolation, assert_pathway_allowed
from backend.services.images import resolve_image_path

router = APIRouter(prefix="/history", tags=["Recycling history"])


def _owned_history(db: Session, user: User, history_id: int) -> RecyclingHistory:
    record = db.get(RecyclingHistory, history_id)
    if record is None or record.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History entry not found.")
    return record


def _owned_assessment(db: Session, user: User, assessment_id: int) -> Assessment:
    record = db.get(Assessment, assessment_id)
    if record is None or record.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")
    return record


def _partner_for(db: Session, partner_id: int | None) -> Partner | None:
    if partner_id is None:
        return None
    partner = db.get(Partner, partner_id)
    if partner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection partner not found.")
    return partner


def _safe_pathway(battery_condition: str, pathway: str) -> None:
    try:
        assert_pathway_allowed(battery_condition, pathway)
    except SafetyViolation as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.post("", response_model=HistoryRead, status_code=status.HTTP_201_CREATED)
def create_history(
    payload: HistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    assessment = _owned_assessment(db, current_user, payload.assessment_id)
    existing = db.scalar(
        select(RecyclingHistory).where(
            RecyclingHistory.user_id == current_user.id,
            RecyclingHistory.assessment_id == assessment.id,
        )
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This assessment is already recorded in your recycling history.",
        )

    pathway = payload.pathway or assessment.pathway
    _safe_pathway(assessment.battery_condition, pathway)

    partner = _partner_for(db, payload.partner_id)
    partner_name = (payload.partner or "").strip() or (
        partner.name if partner is not None else "ReLoop partner network"
    )
    if assessment.brand != "Not specified" or assessment.model != "Not specified":
        detail = f"{assessment.brand} {assessment.model}".strip()
    else:
        detail = f"{assessment.condition} condition"

    points = payload.points
    if points is None:
        points = max(40, assessment.score * 2) if payload.status == "Completed" else 0

    identification = assessment.identification
    record = RecyclingHistory(
        user_id=current_user.id,
        assessment_id=assessment.id,
        partner_id=partner.id if partner is not None else None,
        device=assessment.device,
        detail=detail[:255],
        partner=partner_name[:255],
        status=payload.status,
        pathway=pathway,
        weight_kg=assessment.weight_kg,
        co2_kg=assessment.co2_kg,
        points=points,
        score=assessment.score,
        category=assessment.category,
        battery_condition=assessment.battery_condition,
        notes=(payload.notes or "").strip() or None,
        image_path=identification.image_path if identification is not None else None,
    )
    db.add(record)
    assessment.status = payload.status
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This assessment is already recorded in your recycling history.",
        ) from exc
    db.refresh(record)
    return history_to_dict(record)


@router.get("", response_model=HistoryList)
def list_history(
    q: str | None = Query(default=None, max_length=120),
    status_filter: str | None = Query(default=None, alias="status", max_length=40),
    pathway: str | None = Query(default=None, max_length=60),
    category: str | None = Query(default=None, max_length=80),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    sort: str = Query(default="desc", pattern="^(asc|desc)$"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    filters = [RecyclingHistory.user_id == current_user.id]
    if q:
        term = f"%{q.strip()}%"
        filters.append(
            or_(
                RecyclingHistory.device.ilike(term),
                RecyclingHistory.detail.ilike(term),
                RecyclingHistory.partner.ilike(term),
                RecyclingHistory.notes.ilike(term),
                RecyclingHistory.pathway.ilike(term),
            )
        )
    if status_filter:
        filters.append(RecyclingHistory.status == status_filter)
    if pathway:
        filters.append(RecyclingHistory.pathway == pathway)
    if category:
        filters.append(RecyclingHistory.category == category)
    if date_from:
        filters.append(RecyclingHistory.created_at >= date_from)
    if date_to:
        filters.append(RecyclingHistory.created_at <= date_to)

    base = select(RecyclingHistory).where(*filters)
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    order = RecyclingHistory.created_at.asc() if sort == "asc" else RecyclingHistory.created_at.desc()
    records = db.scalars(base.order_by(order).limit(limit).offset(offset)).all()
    return {"items": [history_to_dict(record) for record in records], "total": total}


@router.get("/summary", response_model=HistorySummary)
def history_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    completed = RecyclingHistory.status == "Completed"
    records = db.scalars(
        select(RecyclingHistory).where(
            RecyclingHistory.user_id == current_user.id,
            completed,
        )
    ).all()
    return {
        "devices": len(records),
        "weight_kg": round(sum(record.weight_kg for record in records), 2),
        "co2_kg": round(sum(record.co2_kg for record in records), 1),
        "points": sum(record.points for record in records),
    }


@router.get("/{history_id}", response_model=HistoryRead)
def get_history(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    return history_to_dict(_owned_history(db, current_user, history_id))


@router.get("/{history_id}/image")
def get_history_image(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FileResponse:
    record = _owned_history(db, current_user, history_id)
    if not record.image_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")
    path = resolve_image_path(record.image_path)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")
    media_type = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    return FileResponse(path, media_type=media_type, headers={"Cache-Control": "private, max-age=3600"})


@router.patch("/{history_id}", response_model=HistoryRead)
@router.put("/{history_id}", response_model=HistoryRead)
def update_history(
    history_id: int,
    payload: HistoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    record = _owned_history(db, current_user, history_id)
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No history fields were provided.",
        )

    if "pathway" in changes and payload.pathway:
        _safe_pathway(record.battery_condition, payload.pathway)
        record.pathway = payload.pathway
    if "status" in changes and payload.status:
        record.status = payload.status
        if payload.status == "Completed" and record.points == 0 and "points" not in changes:
            record.points = max(40, record.score * 2)
    if "points" in changes and payload.points is not None:
        record.points = payload.points
    if "notes" in changes:
        record.notes = (payload.notes or "").strip() or None
    if "partner_id" in changes:
        partner = _partner_for(db, payload.partner_id)
        record.partner_id = partner.id if partner is not None else None
        if partner is not None and not payload.partner:
            record.partner = partner.name
    if "partner" in changes and payload.partner:
        record.partner = payload.partner.strip()[:255]

    db.commit()
    db.refresh(record)
    return history_to_dict(record)


@router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_history(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    record = _owned_history(db, current_user, history_id)
    db.delete(record)
    db.commit()
    return None
