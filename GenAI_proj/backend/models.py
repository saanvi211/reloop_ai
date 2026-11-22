from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    city: Mapped[str] = mapped_column(String(120), default="Bengaluru", nullable=False)
    tier: Mapped[str] = mapped_column(String(80), default="Circular Starter", nullable=False)
    points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    streak_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    member_since: Mapped[str] = mapped_column(String(40), default="2026", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    profile: Mapped["UserProfile"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    settings: Mapped["UserSettings"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    identifications: Mapped[list["Identification"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    assessments: Mapped[list["Assessment"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    history_entries: Mapped[list["RecyclingHistory"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class UserProfile(Base, TimestampMixin):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    city: Mapped[str] = mapped_column(String(120), default="Bengaluru", nullable=False)
    home_area: Mapped[str] = mapped_column(String(120), default="Indiranagar", nullable=False)

    user: Mapped[User] = relationship(back_populates="profile")


class UserSettings(Base, TimestampMixin):
    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    pickup_reminders: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    impact_digest: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    partner_offers: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    default_mode: Mapped[str] = mapped_column(String(40), default="Home pickup", nullable=False)
    preferred_window: Mapped[str] = mapped_column(
        String(60), default="Weekend afternoons", nullable=False
    )
    city: Mapped[str] = mapped_column(String(120), default="Bengaluru", nullable=False)
    home_area: Mapped[str] = mapped_column(String(120), default="Indiranagar", nullable=False)
    max_distance_km: Mapped[int] = mapped_column(Integer, default=12, nullable=False)
    default_sort: Mapped[str] = mapped_column(String(60), default="Nearest first", nullable=False)
    location_sharing: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    anonymous_analytics: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    photo_retention: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    share_impact: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    accent: Mapped[str] = mapped_column(String(40), default="Emerald", nullable=False)

    user: Mapped[User] = relationship(back_populates="settings")


class Identification(Base, TimestampMixin):
    __tablename__ = "identifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    device_category: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    mapped_device: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    predictions: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)
    method: Mapped[str] = mapped_column(String(40), default="mock-classifier", nullable=False)
    needs_review: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    hint: Mapped[str | None] = mapped_column(String(500), nullable=True)
    hint_matched: Mapped[str | None] = mapped_column(String(80), nullable=True)
    source: Mapped[str] = mapped_column(String(255), default="upload", nullable=False)

    user: Mapped[User] = relationship(back_populates="identifications")


class Assessment(Base, TimestampMixin):
    __tablename__ = "assessments"
    __table_args__ = (
        UniqueConstraint("user_id", "identification_id", name="uq_assessment_user_identification"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    identification_id: Mapped[int | None] = mapped_column(
        ForeignKey("identifications.id", ondelete="SET NULL"), nullable=True, index=True
    )
    assessment_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False, index=True
    )
    device: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    category_group: Mapped[str] = mapped_column(String(80), nullable=False)
    condition: Mapped[str] = mapped_column(String(40), nullable=False)
    age_years: Mapped[int] = mapped_column(Integer, nullable=False)
    working: Mapped[bool] = mapped_column(Boolean, nullable=False)
    brand: Mapped[str] = mapped_column(String(120), default="Not specified", nullable=False)
    model: Mapped[str] = mapped_column(String(120), default="Not specified", nullable=False)
    physical_damage: Mapped[str] = mapped_column(String(40), nullable=False)
    battery_condition: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    band: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    estimated_value: Mapped[int] = mapped_column(Integer, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    recyclable_kg: Mapped[float] = mapped_column(Float, nullable=False)
    recyclable_pct: Mapped[int] = mapped_column(Integer, nullable=False)
    co2_kg: Mapped[float] = mapped_column(Float, nullable=False)
    materials: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    guidance: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    pathway: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(40), default="Assessed", nullable=False)

    user: Mapped[User] = relationship(back_populates="assessments")
    identification: Mapped[Identification | None] = relationship()
    recommendation: Mapped["Recommendation | None"] = relationship(
        back_populates="assessment", uselist=False, cascade="all, delete-orphan"
    )
    history_entries: Mapped[list["RecyclingHistory"]] = relationship(back_populates="assessment")


class Recommendation(Base, TimestampMixin):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    assessment_id: Mapped[int] = mapped_column(
        ForeignKey("assessments.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    pathway: Mapped[str] = mapped_column(String(60), nullable=False)
    pathway_meta: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    ranked: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)
    repair_feasibility: Mapped[str] = mapped_column(String(120), nullable=False)
    residual_value: Mapped[int] = mapped_column(Integer, nullable=False)
    e_waste_kg: Mapped[float] = mapped_column(Float, nullable=False)
    co2_kg: Mapped[float] = mapped_column(Float, nullable=False)
    warnings: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    safety_override: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    centre_types: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    accepted_type: Mapped[str] = mapped_column(String(80), nullable=False)
    estimated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped[User] = relationship(back_populates="recommendations")
    assessment: Mapped[Assessment] = relationship(back_populates="recommendation")


class RecyclingHistory(Base, TimestampMixin):
    __tablename__ = "recycling_history"
    __table_args__ = (
        UniqueConstraint("user_id", "assessment_id", name="uq_history_user_assessment"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    assessment_id: Mapped[int | None] = mapped_column(
        ForeignKey("assessments.id", ondelete="SET NULL"), nullable=True, index=True
    )
    partner_id: Mapped[int | None] = mapped_column(
        ForeignKey("partners.id", ondelete="SET NULL"), nullable=True, index=True
    )
    device: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    detail: Mapped[str] = mapped_column(String(255), nullable=False)
    partner: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    pathway: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    co2_kg: Mapped[float] = mapped_column(Float, nullable=False)
    points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    battery_condition: Mapped[str] = mapped_column(String(40), default="Normal", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    user: Mapped[User] = relationship(back_populates="history_entries")
    assessment: Mapped[Assessment | None] = relationship(back_populates="history_entries")
    partner_record: Mapped["Partner | None"] = relationship()


class Partner(Base, TimestampMixin):
    __tablename__ = "partners"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_id: Mapped[str] = mapped_column(String(60), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    area: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    hours: Mapped[str] = mapped_column(String(80), nullable=False)
    open_now: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    accepted: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    partner: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    fictional: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(60), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    speciality: Mapped[str | None] = mapped_column(String(255), nullable=True)
