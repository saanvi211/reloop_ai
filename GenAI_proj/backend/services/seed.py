from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.models import Partner, RecyclingHistory, User, UserProfile, UserSettings
from backend.security import hash_password
from data.mock_data import COLLECTION_POINTS, DEVICE_CATALOG, RECYCLING_HISTORY, USER_PREFERENCES


def _parse_seed_date(value: str) -> datetime:
    for fmt in ("%d %b %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            continue
    return datetime.now(timezone.utc)


def seed_partners(db: Session) -> None:
    existing = {
        partner.external_id: partner
        for partner in db.scalars(select(Partner)).all()
    }
    for point in COLLECTION_POINTS:
        external_id = point.get("id") or point["name"]
        record = existing.get(external_id)
        if record is None:
            record = Partner(external_id=external_id, name=point["name"])
            db.add(record)
        record.name = point["name"]
        record.type = point["type"]
        record.area = point["area"]
        record.address = point["address"]
        record.lat = float(point["lat"])
        record.lon = float(point["lon"])
        record.hours = point["hours"]
        record.open_now = bool(point["open_now"])
        record.accepted = list(point["accepted"])
        record.capacity = int(point["capacity"])
        record.rating = float(point["rating"])
        record.distance_km = float(point["distance_km"])
        record.partner = bool(point.get("partner", True))
        record.fictional = bool(point.get("fictional", True))
        record.phone = point.get("phone")
        record.email = point.get("email")
        record.speciality = point.get("speciality")
    db.commit()


def _ensure_profile_and_settings(db: Session, user: User) -> None:
    if user.profile is None:
        user.profile = UserProfile(
            city=user.city,
            home_area=USER_PREFERENCES.get("home_area", "Indiranagar"),
        )
    if user.settings is None:
        preferences = USER_PREFERENCES
        user.settings = UserSettings(
            pickup_reminders=preferences.get("pickup_reminders", True),
            impact_digest=preferences.get("impact_digest", True),
            partner_offers=preferences.get("partner_offers", False),
            default_mode=preferences.get("default_mode", "Home pickup"),
            preferred_window=preferences.get("preferred_window", "Weekend afternoons"),
            city=preferences.get("city", user.city),
            home_area=preferences.get("home_area", "Indiranagar"),
            max_distance_km=preferences.get("max_distance_km", 12),
            default_sort=preferences.get("default_sort", "Nearest first"),
            location_sharing=preferences.get("location_sharing", True),
            anonymous_analytics=preferences.get("anonymous_analytics", True),
            photo_retention=preferences.get("photo_retention", False),
            share_impact=preferences.get("share_impact", True),
            accent="Emerald",
        )


def seed_demo_user(db: Session) -> User:
    settings = get_settings()
    email = settings.demo_email.strip().lower()
    user = db.scalar(select(User).where(func.lower(User.email) == email))
    if user is None:
        user = User(
            email=email,
            password_hash=hash_password(settings.demo_password),
            name=settings.demo_name,
            city="Bengaluru",
            tier="Green Guardian",
            points=2480,
            streak_days=12,
            member_since="Mar 2025",
        )
        db.add(user)
        db.flush()
        _ensure_profile_and_settings(db, user)
        db.commit()
        db.refresh(user)
    else:
        _ensure_profile_and_settings(db, user)
        db.commit()
        db.refresh(user)
    return user


def seed_demo_history(db: Session, user: User) -> None:
    count = db.scalar(
        select(func.count(RecyclingHistory.id)).where(RecyclingHistory.user_id == user.id)
    )
    if count:
        return

    partner_lookup = {
        partner.name: partner
        for partner in db.scalars(select(Partner)).all()
    }
    for entry in RECYCLING_HISTORY:
        created_at = _parse_seed_date(entry["date"])
        partner_name = entry["partner"]
        partner = partner_lookup.get(partner_name)
        spec = DEVICE_CATALOG.get(entry["device"], {})
        record = RecyclingHistory(
            user_id=user.id,
            assessment_id=None,
            partner_id=partner.id if partner else None,
            device=entry["device"],
            detail=entry["detail"],
            partner=partner_name,
            status=entry["status"],
            pathway=entry.get("pathway", "Recycle"),
            weight_kg=float(entry["weight_kg"]),
            co2_kg=float(entry["co2_kg"]),
            points=int(entry.get("points", 0)),
            score=int(entry.get("score", 0)),
            category=entry.get("category") or spec.get("category", "Other"),
            battery_condition=entry.get("battery_condition", "Normal"),
            notes=entry.get("notes", "Seeded demo recovery record."),
            created_at=created_at,
            updated_at=created_at,
        )
        db.add(record)
    db.commit()


def seed_database(db: Session) -> None:
    settings = get_settings()
    if not settings.seed_demo_data:
        return
    seed_partners(db)
    user = seed_demo_user(db)
    seed_demo_history(db, user)
