from __future__ import annotations

import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import get_current_user
from backend.models import Partner, User
from backend.schemas import CentreMeta, PartnerRead
from backend.serializers import partner_to_dict
from data.mock_data import COLLECTION_POINTS

router = APIRouter(prefix="/centres", tags=["Collection centres"])


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _filtered(
    db: Session,
    *,
    q: str | None,
    centre_type: str | None,
    area: str | None,
    accepted: str | None,
    open_now: bool | None,
    partner_only: bool,
    lat: float | None,
    lon: float | None,
    max_distance: float | None,
    sort: str,
) -> list[dict]:
    records = db.scalars(select(Partner)).all()
    results: list[dict] = []
    for record in records:
        if q:
            term = q.strip().lower()
            haystack = f"{record.name} {record.area} {record.address} {record.speciality or ''}".lower()
            if term not in haystack:
                continue
        if centre_type and record.type != centre_type:
            continue
        if area and record.area != area:
            continue
        if accepted and accepted not in record.accepted:
            continue
        if open_now is not None and record.open_now != open_now:
            continue
        if partner_only and not record.partner:
            continue

        data = partner_to_dict(record)
        if lat is not None and lon is not None:
            data["distance_km"] = round(_haversine(lat, lon, record.lat, record.lon), 1)
        if max_distance is not None and data["distance_km"] > max_distance:
            continue
        results.append(data)

    if sort == "rating":
        results.sort(key=lambda item: item["rating"], reverse=True)
    elif sort == "capacity":
        results.sort(key=lambda item: item["capacity"], reverse=True)
    else:
        results.sort(key=lambda item: item["distance_km"])
    return results


@router.get("/meta", response_model=CentreMeta)
def centre_meta(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    records = db.scalars(select(Partner)).all()
    if not records:
        return {
            "areas": sorted({point["area"] for point in COLLECTION_POINTS}),
            "types": sorted({point["type"] for point in COLLECTION_POINTS}),
            "accepted": sorted({item for point in COLLECTION_POINTS for item in point["accepted"]}),
            "fictional": True,
        }
    return {
        "areas": sorted({record.area for record in records}),
        "types": sorted({record.type for record in records}),
        "accepted": sorted({item for record in records for item in record.accepted}),
        "fictional": True,
    }


@router.get("/nearby", response_model=list[PartnerRead])
def nearby_centres(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    max_distance: float = Query(default=20, ge=0.1, le=500),
    accepted: str | None = Query(default=None, max_length=80),
    centre_type: str | None = Query(default=None, max_length=80),
    sort: str = Query(default="nearest", pattern="^(nearest|rating|capacity)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    return _filtered(
        db,
        q=None,
        centre_type=centre_type,
        area=None,
        accepted=accepted,
        open_now=None,
        partner_only=False,
        lat=lat,
        lon=lon,
        max_distance=max_distance,
        sort=sort,
    )


@router.get("", response_model=list[PartnerRead])
def list_centres(
    q: str | None = Query(default=None, max_length=120),
    centre_type: str | None = Query(default=None, alias="type", max_length=80),
    area: str | None = Query(default=None, max_length=120),
    accepted: str | None = Query(default=None, max_length=80),
    open_now: bool | None = Query(default=None),
    partner_only: bool = Query(default=False),
    lat: float | None = Query(default=None, ge=-90, le=90),
    lon: float | None = Query(default=None, ge=-180, le=180),
    max_distance: float | None = Query(default=None, ge=0.1, le=500),
    sort: str = Query(default="nearest", pattern="^(nearest|rating|capacity)$"),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    return _filtered(
        db,
        q=q,
        centre_type=centre_type,
        area=area,
        accepted=accepted,
        open_now=open_now,
        partner_only=partner_only,
        lat=lat,
        lon=lon,
        max_distance=max_distance,
        sort=sort,
    )[:limit]


@router.get("/{partner_id}", response_model=PartnerRead)
def get_centre(
    partner_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    record = db.get(Partner, partner_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection partner not found.")
    return partner_to_dict(record)
