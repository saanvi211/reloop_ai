from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import get_current_user
from backend.models import User, UserSettings
from backend.schemas import SettingsRead, SettingsUpdate
from backend.serializers import settings_to_dict
from data.mock_data import USER_PREFERENCES

router = APIRouter(prefix="/settings", tags=["Settings"])


def _ensure_settings(db: Session, user: User) -> UserSettings:
    if user.settings is None:
        preferences = USER_PREFERENCES
        user.settings = UserSettings(
            city=user.city,
            home_area=preferences.get("home_area", "Indiranagar"),
            pickup_reminders=preferences.get("pickup_reminders", True),
            impact_digest=preferences.get("impact_digest", True),
            partner_offers=preferences.get("partner_offers", False),
            default_mode=preferences.get("default_mode", "Home pickup"),
            preferred_window=preferences.get("preferred_window", "Weekend afternoons"),
            max_distance_km=preferences.get("max_distance_km", 12),
            default_sort=preferences.get("default_sort", "Nearest first"),
            location_sharing=preferences.get("location_sharing", True),
            anonymous_analytics=preferences.get("anonymous_analytics", True),
            photo_retention=preferences.get("photo_retention", False),
            share_impact=preferences.get("share_impact", True),
            accent="Emerald",
        )
        db.commit()
        db.refresh(user.settings)
    return user.settings


@router.get("", response_model=SettingsRead)
@router.get("/preferences", response_model=SettingsRead)
def get_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    return settings_to_dict(_ensure_settings(db, current_user))


@router.put("", response_model=SettingsRead)
@router.patch("", response_model=SettingsRead)
@router.put("/preferences", response_model=SettingsRead)
@router.patch("/preferences", response_model=SettingsRead)
def update_settings(
    payload: SettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    record = _ensure_settings(db, current_user)
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No settings fields were provided.",
        )
    for key, value in changes.items():
        if key in {"city", "home_area"} and value is not None:
            value = value.strip()
        setattr(record, key, value)

    if "city" in changes and changes["city"]:
        current_user.city = changes["city"].strip()
        if current_user.profile is not None:
            current_user.profile.city = current_user.city

    db.commit()
    db.refresh(record)
    return settings_to_dict(record)
