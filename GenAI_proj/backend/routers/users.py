from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import get_current_user
from backend.models import User, UserProfile
from backend.schemas import ProfileRead, ProfileUpdate, UserRead, UserUpdate
from backend.serializers import profile_to_dict, user_to_dict

router = APIRouter(prefix="/users", tags=["Users & profiles"])


def _ensure_profile(current_user: User) -> UserProfile:
    if current_user.profile is None:
        current_user.profile = UserProfile(city=current_user.city)
    return current_user.profile


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)) -> dict:
    return user_to_dict(current_user)


@router.patch("/me", response_model=UserRead)
def update_me(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No profile fields were provided.",
        )
    if "email" in changes and changes["email"]:
        email = changes["email"].strip().lower()
        existing = db.scalar(
            select(User).where(func.lower(User.email) == email, User.id != current_user.id)
        )
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="That email address is already in use.",
            )
        current_user.email = email
    if "name" in changes and changes["name"]:
        current_user.name = changes["name"].strip()
    if "city" in changes and changes["city"]:
        current_user.city = changes["city"].strip()
        _ensure_profile(current_user).city = current_user.city

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="That email address is already in use.",
        ) from exc
    db.refresh(current_user)
    return user_to_dict(current_user)


@router.get("/me/profile", response_model=ProfileRead)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    profile = _ensure_profile(current_user)
    db.commit()
    db.refresh(profile)
    return profile_to_dict(profile)


@router.put("/me/profile", response_model=ProfileRead)
@router.patch("/me/profile", response_model=ProfileRead)
def update_profile(
    payload: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    profile = _ensure_profile(current_user)
    changes = payload.model_dump(exclude_unset=True)
    for key, value in changes.items():
        if key in {"phone", "bio", "avatar_url"}:
            setattr(profile, key, (value or "").strip() or None)
        elif key in {"city", "home_area"} and value:
            setattr(profile, key, value.strip())
    if payload.city:
        current_user.city = payload.city.strip()
    db.commit()
    db.refresh(profile)
    return profile_to_dict(profile)
