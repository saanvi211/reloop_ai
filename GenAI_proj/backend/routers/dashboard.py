from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import get_current_user
from backend.models import Assessment, RecyclingHistory, User
from backend.schemas import DashboardStats, ImpactStats
from backend.serializers import history_to_dict
from data.mock_data import DEVICE_CATALOG

router = APIRouter(prefix="/dashboard", tags=["Dashboard & impact"])

RangeFilter = Literal["30d", "90d", "year", "all"]

PATHWAY_KEYS = ["Repair", "Refurbish & Resell", "Harvest Components", "Recycle", "Hazardous Handling"]


def _range_start(range_value: str) -> datetime | None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if range_value == "30d":
        return now - timedelta(days=30)
    if range_value == "90d":
        return now - timedelta(days=90)
    if range_value == "year":
        return datetime(now.year, 1, 1)
    return None


def _category_filter(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def _history_records(db: Session, user: User, start: datetime | None) -> list[RecyclingHistory]:
    query = select(RecyclingHistory).where(RecyclingHistory.user_id == user.id)
    if start is not None:
        query = query.where(RecyclingHistory.created_at >= start)
    return list(db.scalars(query.order_by(RecyclingHistory.created_at.desc())).all())


def _filtered_history(
    records: list[RecyclingHistory], categories: list[str]
) -> list[RecyclingHistory]:
    if not categories:
        return records
    wanted = {item.lower() for item in categories}
    return [record for record in records if record.category.lower() in wanted]


def _totals(records: list[RecyclingHistory]) -> dict:
    completed = [record for record in records if record.status == "Completed"]
    return {
        "devices_assessed": len(records),
        "devices_recovered": len(completed),
        "weight_kg": round(sum(record.weight_kg for record in completed), 2),
        "co2_kg": round(sum(record.co2_kg for record in completed), 1),
        "points": sum(record.points for record in completed),
        "repaired": sum(1 for record in completed if record.pathway == "Repair"),
        "reused": sum(1 for record in completed if record.pathway == "Refurbish & Resell"),
        "recycled": sum(
            1 for record in completed if record.pathway in {"Recycle", "Harvest Components"}
        ),
        "hazardous": sum(1 for record in completed if record.pathway == "Hazardous Handling"),
    }


def _status_breakdown(records: list[RecyclingHistory]) -> dict[str, int]:
    counts = {"Completed": 0, "Scheduled": 0, "Processing": 0, "In transit": 0}
    for record in records:
        counts[record.status] = counts.get(record.status, 0) + 1
    return counts


def _pathway_breakdown(records: list[RecyclingHistory]) -> dict[str, dict[str, float]]:
    breakdown = {
        key: {"devices": 0, "weight_kg": 0.0, "co2_kg": 0.0} for key in PATHWAY_KEYS
    }
    for record in records:
        if record.status != "Completed":
            continue
        entry = breakdown.setdefault(
            record.pathway, {"devices": 0, "weight_kg": 0.0, "co2_kg": 0.0}
        )
        entry["devices"] += 1
        entry["weight_kg"] = round(entry["weight_kg"] + record.weight_kg, 2)
        entry["co2_kg"] = round(entry["co2_kg"] + record.co2_kg, 1)
    return breakdown


def _category_breakdown(records: list[RecyclingHistory]) -> list[dict]:
    grouped: dict[str, dict] = {}
    for record in records:
        entry = grouped.setdefault(
            record.category, {"category": record.category, "devices": 0, "weight_kg": 0.0, "co2_kg": 0.0}
        )
        entry["devices"] += 1
        entry["weight_kg"] = round(entry["weight_kg"] + record.weight_kg, 2)
        entry["co2_kg"] = round(entry["co2_kg"] + record.co2_kg, 1)
    return sorted(grouped.values(), key=lambda item: item["devices"], reverse=True)


def _monthly(records: list[RecyclingHistory]) -> list[dict]:
    grouped: dict[tuple[int, int], dict] = {}
    for record in records:
        if record.status != "Completed":
            continue
        stamp = record.created_at
        key = (stamp.year, stamp.month)
        entry = grouped.setdefault(
            key,
            {
                "month": stamp.strftime("%b %Y"),
                "waste_kg": 0.0,
                "devices": 0,
                "co2_kg": 0.0,
            },
        )
        entry["waste_kg"] = round(entry["waste_kg"] + record.weight_kg, 2)
        entry["devices"] += 1
        entry["co2_kg"] = round(entry["co2_kg"] + record.co2_kg, 1)
    return [grouped[key] for key in sorted(grouped)]


def _assessments(db: Session, user: User, start: datetime | None) -> list[Assessment]:
    query = select(Assessment).where(Assessment.user_id == user.id)
    if start is not None:
        query = query.where(Assessment.assessment_date >= start)
    return list(db.scalars(query).all())


def _materials(assessments: list[Assessment], records: list[RecyclingHistory]) -> list[dict]:
    totals: dict[str, float] = {}
    for assessment in assessments:
        for material, pct in (assessment.materials or {}).items():
            totals[material] = totals.get(material, 0.0) + assessment.recyclable_kg * pct / 100

    if not totals:
        for record in records:
            if record.status != "Completed":
                continue
            spec = DEVICE_CATALOG.get(record.device)
            if not spec:
                continue
            recoverable = record.weight_kg * spec["recyclable_pct"] / 100
            for material, pct in spec["materials"].items():
                totals[material] = totals.get(material, 0.0) + recoverable * pct / 100

    return [
        {"material": material, "kg": round(kg, 1)}
        for material, kg in sorted(totals.items(), key=lambda item: item[1], reverse=True)
    ]


def _equivalents(totals: dict) -> list[dict]:
    co2 = totals["co2_kg"]
    weight = totals["weight_kg"]
    return [
        {
            "label": "Trees planted for a year",
            "value": f"{int(co2 / 21.77):,}",
            "icon": "leaf",
            "tone": "green",
            "note": "At 21.77 kg CO₂ absorbed per mature tree per year.",
        },
        {
            "label": "Smartphones charged",
            "value": f"{int(co2 * 9.8):,}",
            "icon": "phone",
            "tone": "blue",
            "note": "Approximate energy saved from avoided manufacturing.",
        },
        {
            "label": "Landfill space avoided",
            "value": f"{round(weight * 0.0015, 2)} m³",
            "icon": "package",
            "tone": "amber",
            "note": "Estimated compacted e-waste volume kept out of landfill.",
        },
    ]


@router.get("/stats", response_model=DashboardStats)
def dashboard_stats(
    range_filter: RangeFilter = Query(default="all", alias="range"),
    categories: str | None = Query(default=None, max_length=300),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    start = _range_start(range_filter)
    wanted = _category_filter(categories)
    records = _filtered_history(_history_records(db, current_user, start), wanted)
    completed = [record for record in records if record.status == "Completed"]
    return {
        "totals": _totals(records),
        "status_breakdown": _status_breakdown(records),
        "pathway_breakdown": _pathway_breakdown(completed),
        "category_breakdown": _category_breakdown(records),
        "monthly": _monthly(completed),
        "recent_activity": [history_to_dict(record) for record in records[:6]],
        "range": range_filter,
        "categories": wanted,
    }


@router.get("/impact", response_model=ImpactStats)
def impact_stats(
    range_filter: RangeFilter = Query(default="all", alias="range"),
    categories: str | None = Query(default=None, max_length=300),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    start = _range_start(range_filter)
    wanted = _category_filter(categories)
    records = _filtered_history(_history_records(db, current_user, start), wanted)
    completed = [record for record in records if record.status == "Completed"]
    assessments = _assessments(db, current_user, start)

    totals = _totals(records)
    return {
        "totals": totals,
        "pathway_breakdown": _pathway_breakdown(completed),
        "monthly": _monthly(completed),
        "materials": _materials(assessments, completed),
        "equivalents": _equivalents(totals),
        "range": range_filter,
    }
