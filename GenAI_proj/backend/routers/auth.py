from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import get_current_user
from backend.models import User, UserProfile, UserSettings
from backend.schemas import AuthResponse, UserLogin, UserRead, UserRegister
from backend.security import create_access_token, hash_password, verify_password
from backend.serializers import user_to_dict
from data.mock_data import USER_PREFERENCES

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)) -> AuthResponse:
    email = payload.email.strip().lower()
    existing = db.scalar(select(User).where(func.lower(User.email) == email))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = User(
        email=email,
        password_hash=hash_password(payload.password),
        name=payload.name.strip(),
        city=payload.city.strip() or "Bengaluru",
        tier="Circular Starter",
        points=0,
        streak_days=0,
        member_since=datetime_now_label(),
    )
    user.profile = UserProfile(
        city=user.city,
        home_area=USER_PREFERENCES.get("home_area", "Indiranagar"),
    )
    user.settings = UserSettings(
        city=user.city,
        home_area=USER_PREFERENCES.get("home_area", "Indiranagar"),
        default_mode=USER_PREFERENCES.get("default_mode", "Home pickup"),
        preferred_window=USER_PREFERENCES.get("preferred_window", "Weekend afternoons"),
        max_distance_km=USER_PREFERENCES.get("max_distance_km", 12),
        default_sort=USER_PREFERENCES.get("default_sort", "Nearest first"),
        location_sharing=USER_PREFERENCES.get("location_sharing", True),
        anonymous_analytics=USER_PREFERENCES.get("anonymous_analytics", True),
        photo_retention=USER_PREFERENCES.get("photo_retention", False),
        share_impact=USER_PREFERENCES.get("share_impact", True),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        ) from exc
    db.refresh(user)
    return AuthResponse(access_token=create_access_token(user.id), user=user_to_dict(user))


@router.post("/login", response_model=AuthResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> AuthResponse:
    email = payload.email.strip().lower()
    user = db.scalar(select(User).where(func.lower(User.email) == email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This account is inactive.")
    return AuthResponse(access_token=create_access_token(user.id), user=user_to_dict(user))


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> dict:
    return user_to_dict(current_user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user: User = Depends(get_current_user)) -> None:
    # Tokens are stateless; clients discard the token to log out.
    return None


def datetime_now_label() -> str:
    from datetime import datetime

    return datetime.now().strftime("%b %Y")
