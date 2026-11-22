from __future__ import annotations

from datetime import datetime
from typing import Any

from backend.models import (
    Assessment,
    Identification,
    Partner,
    Recommendation,
    RecyclingHistory,
    User,
)
from utils.helpers import device_icon


def _fmt_date(value: datetime | None) -> str:
    return (value or datetime.now()).strftime("%d %b %Y")


def _tone_for_status(status: str) -> str:
    return {
        "Completed": "green",
        "Scheduled": "blue",
        "Processing": "amber",
        "In transit": "teal",
    }.get(status, "green")


def user_to_dict(user: User) -> dict[str, Any]:
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "city": user.city,
        "tier": user.tier,
        "points": user.points,
        "streak_days": user.streak_days,
        "member_since": user.member_since,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "profile": profile_to_dict(user.profile) if user.profile else None,
    }


def profile_to_dict(profile: Any) -> dict[str, Any] | None:
    if profile is None:
        return None
    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "phone": profile.phone,
        "bio": profile.bio,
        "avatar_url": profile.avatar_url,
        "city": profile.city,
        "home_area": profile.home_area,
        "created_at": profile.created_at,
        "updated_at": profile.updated_at,
    }


def identification_to_dict(record: Identification) -> dict[str, Any]:
    return {
        "id": record.id,
        "device": record.device_category,
        "confidence": record.confidence,
        "predictions": record.predictions,
        "needs_review": record.needs_review,
        "method": record.method,
        "hint_matched": record.hint_matched,
        "source": record.source,
        "mapped_device": record.mapped_device,
        "image_url": f"/api/identifications/{record.id}/image" if record.image_path else None,
        "filename": record.original_filename,
        "content_type": record.content_type,
        "file_size": record.file_size,
        "created_at": record.created_at,
    }


def recommendation_to_dict(record: Recommendation) -> dict[str, Any]:
    return {
        "id": record.id,
        "assessment_id": record.assessment_id,
        "pathway": record.pathway,
        "pathway_meta": record.pathway_meta,
        "explanation": record.explanation,
        "ranked": record.ranked,
        "repair_feasibility": record.repair_feasibility,
        "residual_value": record.residual_value,
        "e_waste_kg": record.e_waste_kg,
        "co2_kg": record.co2_kg,
        "warnings": record.warnings,
        "safety_override": record.safety_override,
        "centre_types": record.centre_types,
        "accepted_type": record.accepted_type,
        "estimated": record.estimated,
        "created_at": record.created_at,
    }


def assessment_to_dict(record: Assessment, include_recommendation: bool = True) -> dict[str, Any]:
    identification = record.identification
    image_url = None
    photo_name = None
    identified_category = None
    identification_confidence = None
    if identification is not None:
        if identification.image_path:
            image_url = f"/api/identifications/{identification.id}/image"
        photo_name = identification.original_filename
        identified_category = identification.device_category
        identification_confidence = identification.confidence

    return {
        "id": record.id,
        "assessment_id": record.id,
        "identification_id": record.identification_id,
        "assessment_date": record.assessment_date,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
        "device": record.device,
        "category": record.category,
        "category_group": record.category_group,
        "condition": record.condition,
        "age_years": record.age_years,
        "working": record.working,
        "brand": record.brand,
        "model": record.model,
        "physical_damage": record.physical_damage,
        "battery_condition": record.battery_condition,
        "description": record.description,
        "score": record.score,
        "band": record.band,
        "estimated_value": record.estimated_value,
        "weight_kg": record.weight_kg,
        "recyclable_kg": record.recyclable_kg,
        "recyclable_pct": record.recyclable_pct,
        "co2_kg": record.co2_kg,
        "materials": record.materials,
        "guidance": record.guidance,
        "pathway": record.pathway,
        "status": record.status,
        "identified_category": identified_category,
        "identification_confidence": identification_confidence,
        "photo_name": photo_name,
        "image_url": image_url,
        "recommendation": (
            recommendation_to_dict(record.recommendation)
            if include_recommendation and record.recommendation is not None
            else None
        ),
    }


def history_to_dict(record: RecyclingHistory) -> dict[str, Any]:
    return {
        "id": record.id,
        "assessment_id": record.assessment_id,
        "partner_id": record.partner_id,
        "date": _fmt_date(record.created_at),
        "created_at": record.created_at,
        "device": record.device,
        "detail": record.detail,
        "partner": record.partner,
        "status": record.status,
        "pathway": record.pathway,
        "weight_kg": record.weight_kg,
        "co2_kg": record.co2_kg,
        "points": record.points,
        "score": record.score,
        "category": record.category,
        "battery_condition": record.battery_condition,
        "notes": record.notes,
        "image_url": f"/api/history/{record.id}/image" if record.image_path else None,
        "icon": device_icon(record.device),
        "tone": _tone_for_status(record.status),
    }


def partner_to_dict(record: Partner) -> dict[str, Any]:
    return {
        "id": record.id,
        "external_id": record.external_id,
        "name": record.name,
        "type": record.type,
        "area": record.area,
        "address": record.address,
        "lat": record.lat,
        "lon": record.lon,
        "hours": record.hours,
        "open_now": record.open_now,
        "accepted": record.accepted,
        "capacity": record.capacity,
        "rating": record.rating,
        "distance_km": record.distance_km,
        "partner": record.partner,
        "fictional": record.fictional,
        "phone": record.phone,
        "email": record.email,
        "speciality": record.speciality,
    }


def settings_to_dict(record: Any) -> dict[str, Any]:
    return {
        "id": record.id,
        "user_id": record.user_id,
        "pickup_reminders": record.pickup_reminders,
        "impact_digest": record.impact_digest,
        "partner_offers": record.partner_offers,
        "default_mode": record.default_mode,
        "preferred_window": record.preferred_window,
        "city": record.city,
        "home_area": record.home_area,
        "max_distance_km": record.max_distance_km,
        "default_sort": record.default_sort,
        "location_sharing": record.location_sharing,
        "anonymous_analytics": record.anonymous_analytics,
        "photo_retention": record.photo_retention,
        "share_impact": record.share_impact,
        "accent": record.accent,
        "updated_at": record.updated_at,
    }
