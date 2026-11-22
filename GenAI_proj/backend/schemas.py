from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

BatteryCondition = Literal["Normal", "Swollen", "Overheating", "Leaking", "Unknown"]
DamageLevel = Literal["None", "Minor", "Moderate", "Major"]
HistoryStatus = Literal["Completed", "Scheduled", "Processing", "In transit"]
PathwayName = Literal[
    "Repair",
    "Refurbish & Resell",
    "Harvest Components",
    "Recycle",
    "Hazardous Handling",
]
SortOption = Literal["nearest", "rating", "capacity"]


class UserRegister(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    city: str = Field(default="Bengaluru", max_length=120)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    email: EmailStr | None = None
    city: str | None = Field(default=None, max_length=120)


class ProfileBase(BaseModel):
    phone: str | None = Field(default=None, max_length=40)
    bio: str | None = Field(default=None, max_length=1000)
    avatar_url: str | None = Field(default=None, max_length=500)
    city: str | None = Field(default=None, max_length=120)
    home_area: str | None = Field(default=None, max_length=120)


class ProfileUpdate(ProfileBase):
    pass


class ProfileRead(ProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    name: str
    city: str
    tier: str
    points: int
    streak_days: int
    member_since: str
    is_active: bool
    created_at: datetime
    profile: ProfileRead | None = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class IdentificationCreate(BaseModel):
    category: str = Field(min_length=1, max_length=80)
    hint: str | None = Field(default=None, max_length=500)


class IdentificationRead(BaseModel):
    id: int
    device: str
    confidence: float
    predictions: list[dict[str, Any]]
    needs_review: bool
    method: str
    hint_matched: str | None = None
    source: str
    mapped_device: str
    image_url: str | None = None
    filename: str | None = None
    content_type: str | None = None
    file_size: int | None = None
    created_at: datetime


class IdentificationList(BaseModel):
    items: list[IdentificationRead]
    total: int


class AssessmentCreate(BaseModel):
    identification_id: int | None = Field(default=None, ge=1)
    device: str | None = Field(default=None, max_length=80)
    age_years: int = Field(default=3, ge=0, le=50)
    working: bool
    physical_damage: DamageLevel = "None"
    battery_condition: BatteryCondition = "Normal"
    brand: str | None = Field(default=None, max_length=120)
    model: str | None = Field(default=None, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    selected_pathway: PathwayName | None = None
    identified_category: str | None = Field(default=None, max_length=80)

    @model_validator(mode="after")
    def require_device_source(self) -> "AssessmentCreate":
        if not self.identification_id and not self.device:
            raise ValueError("Either identification_id or device must be provided.")
        return self


class AssessmentUpdate(BaseModel):
    identification_id: int | None = Field(default=None, ge=1)
    device: str | None = Field(default=None, max_length=80)
    age_years: int | None = Field(default=None, ge=0, le=50)
    working: bool | None = None
    physical_damage: DamageLevel | None = None
    battery_condition: BatteryCondition | None = None
    brand: str | None = Field(default=None, max_length=120)
    model: str | None = Field(default=None, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    selected_pathway: PathwayName | None = None
    identified_category: str | None = Field(default=None, max_length=80)


class RecommendationRead(BaseModel):
    id: int
    assessment_id: int
    pathway: str
    pathway_meta: dict[str, Any]
    explanation: str
    ranked: list[dict[str, Any]]
    repair_feasibility: str
    residual_value: int
    e_waste_kg: float
    co2_kg: float
    warnings: list[str]
    safety_override: bool
    centre_types: list[str]
    accepted_type: str
    estimated: bool
    created_at: datetime


class AssessmentRead(BaseModel):
    id: int
    assessment_id: int
    identification_id: int | None = None
    assessment_date: datetime
    created_at: datetime
    updated_at: datetime
    device: str
    category: str
    category_group: str
    condition: str
    age_years: int
    working: bool
    brand: str
    model: str
    physical_damage: str
    battery_condition: str
    description: str | None = None
    score: int
    band: dict[str, Any]
    estimated_value: int
    weight_kg: float
    recyclable_kg: float
    recyclable_pct: int
    co2_kg: float
    materials: dict[str, Any]
    guidance: list[str]
    pathway: str
    status: str
    identified_category: str | None = None
    identification_confidence: float | None = None
    photo_name: str | None = None
    image_url: str | None = None
    recommendation: RecommendationRead | None = None


class AssessmentList(BaseModel):
    items: list[AssessmentRead]
    total: int


class HistoryCreate(BaseModel):
    assessment_id: int = Field(ge=1)
    partner_id: int | None = Field(default=None, ge=1)
    partner: str | None = Field(default=None, max_length=255)
    status: HistoryStatus = "Processing"
    pathway: PathwayName | None = None
    points: int | None = Field(default=None, ge=0, le=100000)
    notes: str | None = Field(default=None, max_length=2000)


class HistoryUpdate(BaseModel):
    partner_id: int | None = Field(default=None, ge=1)
    partner: str | None = Field(default=None, max_length=255)
    status: HistoryStatus | None = None
    pathway: PathwayName | None = None
    points: int | None = Field(default=None, ge=0, le=100000)
    notes: str | None = Field(default=None, max_length=2000)


class HistoryRead(BaseModel):
    id: int
    assessment_id: int | None = None
    partner_id: int | None = None
    date: str
    created_at: datetime
    device: str
    detail: str
    partner: str
    status: str
    pathway: str
    weight_kg: float
    co2_kg: float
    points: int
    score: int
    category: str
    battery_condition: str
    notes: str | None = None
    image_url: str | None = None
    icon: str
    tone: str


class HistoryList(BaseModel):
    items: list[HistoryRead]
    total: int


class HistorySummary(BaseModel):
    devices: int
    weight_kg: float
    co2_kg: float
    points: int


class PartnerRead(BaseModel):
    id: int
    external_id: str
    name: str
    type: str
    area: str
    address: str
    lat: float
    lon: float
    hours: str
    open_now: bool
    accepted: list[str]
    capacity: int
    rating: float
    distance_km: float
    partner: bool
    fictional: bool
    phone: str | None = None
    email: str | None = None
    speciality: str | None = None


class CentreMeta(BaseModel):
    areas: list[str]
    types: list[str]
    accepted: list[str]
    fictional: bool = True


class SettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    pickup_reminders: bool
    impact_digest: bool
    partner_offers: bool
    default_mode: str
    preferred_window: str
    city: str
    home_area: str
    max_distance_km: int
    default_sort: str
    location_sharing: bool
    anonymous_analytics: bool
    photo_retention: bool
    share_impact: bool
    accent: str
    updated_at: datetime


class SettingsUpdate(BaseModel):
    pickup_reminders: bool | None = None
    impact_digest: bool | None = None
    partner_offers: bool | None = None
    default_mode: str | None = Field(default=None, max_length=40)
    preferred_window: str | None = Field(default=None, max_length=60)
    city: str | None = Field(default=None, max_length=120)
    home_area: str | None = Field(default=None, max_length=120)
    max_distance_km: int | None = Field(default=None, ge=1, le=100)
    default_sort: str | None = Field(default=None, max_length=60)
    location_sharing: bool | None = None
    anonymous_analytics: bool | None = None
    photo_retention: bool | None = None
    share_impact: bool | None = None
    accent: str | None = Field(default=None, max_length=40)


class DashboardTotals(BaseModel):
    devices_assessed: int
    devices_recovered: int
    weight_kg: float
    co2_kg: float
    points: int
    repaired: int
    reused: int
    recycled: int
    hazardous: int


class MonthlyPoint(BaseModel):
    month: str
    waste_kg: float
    devices: int
    co2_kg: float


class DashboardStats(BaseModel):
    totals: DashboardTotals
    status_breakdown: dict[str, int]
    pathway_breakdown: dict[str, dict[str, float]]
    category_breakdown: list[dict[str, Any]]
    monthly: list[MonthlyPoint]
    recent_activity: list[HistoryRead]
    range: str
    categories: list[str]


class ImpactStats(BaseModel):
    totals: DashboardTotals
    pathway_breakdown: dict[str, dict[str, float]]
    monthly: list[MonthlyPoint]
    materials: list[dict[str, Any]]
    equivalents: list[dict[str, Any]]
    range: str
