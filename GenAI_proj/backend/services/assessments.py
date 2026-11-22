from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.models import Assessment, Identification, Recommendation, User
from backend.schemas import AssessmentCreate, AssessmentUpdate
from data.mock_data import (
    BATTERY_CONDITIONS,
    DAMAGE_LEVELS,
    DEVICE_CATALOG,
    HAZARDOUS_BATTERY_CONDITIONS,
)
from utils.helpers import derive_condition, estimate_identification
from utils.recommendations_engine import build_recommendation


class SafetyViolation(ValueError):
    """Raised when a pathway would violate the hazardous battery safety rule."""


def is_hazardous(battery_condition: str) -> bool:
    return battery_condition in HAZARDOUS_BATTERY_CONDITIONS


def assert_pathway_allowed(battery_condition: str, pathway: str) -> None:
    if is_hazardous(battery_condition) and pathway != "Hazardous Handling":
        raise SafetyViolation(
            "Swollen, overheating or leaking batteries may only use Hazardous Handling. "
            "Repair, resale and component harvesting are blocked."
        )


def _get_identification(db: Session, user: User, identification_id: int) -> Identification:
    record = db.get(Identification, identification_id)
    if record is None or record.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Identification not found.")
    return record


def _normalise_text(value: str | None, fallback: str = "Not specified") -> str:
    text = (value or "").strip()
    return text or fallback


def _apply_estimate(assessment: Assessment, result: dict, brand: str, model: str, description: str | None) -> None:
    assessment.device = result["device"]
    assessment.category = result["category"]
    assessment.category_group = result["category_group"]
    assessment.condition = result["condition"]
    assessment.age_years = result["age_years"]
    assessment.working = result["working"]
    assessment.brand = brand
    assessment.model = model
    assessment.physical_damage = result["physical_damage"]
    assessment.battery_condition = result["battery_condition"]
    assessment.description = description
    assessment.score = result["score"]
    assessment.band = result["band"]
    assessment.estimated_value = result["estimated_value"]
    assessment.weight_kg = result["weight_kg"]
    assessment.recyclable_kg = result["recyclable_kg"]
    assessment.recyclable_pct = result["recyclable_pct"]
    assessment.co2_kg = result["co2_kg"]
    assessment.materials = result["materials"]
    assessment.guidance = result["guidance"]
    assessment.status = "Assessed"


def _engine_input(assessment: Assessment) -> dict:
    return {
        "device": assessment.device,
        "category": assessment.category,
        "category_group": assessment.category_group,
        "condition": assessment.condition,
        "age_years": assessment.age_years,
        "working": assessment.working,
        "physical_damage": assessment.physical_damage,
        "battery_condition": assessment.battery_condition,
        "description": assessment.description or "",
        "score": assessment.score,
        "estimated_value": assessment.estimated_value,
        "weight_kg": assessment.weight_kg,
        "recyclable_kg": assessment.recyclable_kg,
        "recyclable_pct": assessment.recyclable_pct,
        "co2_kg": assessment.co2_kg,
        "materials": assessment.materials,
    }


def compute_recommendation(assessment: Assessment) -> dict:
    recommendation = build_recommendation(_engine_input(assessment))
    if is_hazardous(assessment.battery_condition):
        if recommendation.get("pathway") != "Hazardous Handling" or not recommendation.get("safety_override"):
            raise RuntimeError("Safety engine failed to enforce Hazardous Handling.")
    return recommendation


def store_recommendation(db: Session, assessment: Assessment, data: dict) -> Recommendation:
    record = assessment.recommendation
    if record is None:
        record = Recommendation(user_id=assessment.user_id, assessment_id=assessment.id)
        db.add(record)
        assessment.recommendation = record
    record.pathway = data["pathway"]
    record.pathway_meta = data["pathway_meta"]
    record.explanation = data["explanation"]
    record.ranked = data["ranked"]
    record.repair_feasibility = data["repair_feasibility"]
    record.residual_value = data["residual_value"]
    record.e_waste_kg = data["e_waste_kg"]
    record.co2_kg = data["co2_kg"]
    record.warnings = data["warnings"]
    record.safety_override = data["safety_override"]
    record.centre_types = data["centre_types"]
    record.accepted_type = data["accepted_type"]
    record.estimated = data.get("estimated", True)
    db.flush()
    return record


def regenerate_recommendation(db: Session, assessment: Assessment) -> Recommendation:
    data = compute_recommendation(assessment)
    record = store_recommendation(db, assessment, data)
    if is_hazardous(assessment.battery_condition):
        assessment.pathway = "Hazardous Handling"
    db.commit()
    db.refresh(record)
    return record


def _validate_choice(value: str, allowed: list[str] | set[str], label: str) -> None:
    if value not in allowed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid {label}. Allowed values: {', '.join(sorted(allowed))}.",
        )


def _apply_assessment(
    db: Session,
    user: User,
    payload: AssessmentCreate | AssessmentUpdate,
    assessment: Assessment | None,
) -> Assessment:
    identification: Identification | None = None
    if payload.identification_id is not None:
        identification = _get_identification(db, user, payload.identification_id)
    elif assessment is not None and assessment.identification_id:
        identification = db.get(Identification, assessment.identification_id)

    if identification is not None:
        device = identification.mapped_device
    elif payload.device:
        device = payload.device
    elif assessment is not None:
        device = assessment.device
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Either identification_id or device must be provided.",
        )

    if device not in DEVICE_CATALOG:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported device '{device}'. Choose a supported device type.",
        )

    age_years = (
        payload.age_years
        if payload.age_years is not None
        else (assessment.age_years if assessment is not None else 0)
    )
    working = (
        payload.working
        if payload.working is not None
        else (assessment.working if assessment is not None else True)
    )
    physical_damage = (
        payload.physical_damage
        if payload.physical_damage is not None
        else (assessment.physical_damage if assessment is not None else "None")
    )
    battery_condition = (
        payload.battery_condition
        if payload.battery_condition is not None
        else (assessment.battery_condition if assessment is not None else "Normal")
    )
    brand = _normalise_text(
        payload.brand if payload.brand is not None else (assessment.brand if assessment else None)
    )
    model = _normalise_text(
        payload.model if payload.model is not None else (assessment.model if assessment else None)
    )
    if payload.description is not None:
        description = payload.description.strip() or None
    else:
        description = assessment.description if assessment is not None else None

    _validate_choice(physical_damage, DAMAGE_LEVELS, "physical damage level")
    _validate_choice(battery_condition, BATTERY_CONDITIONS, "battery condition")

    if assessment is not None and payload.identification_id is not None:
        duplicate = db.scalar(
            select(Assessment).where(
                Assessment.user_id == user.id,
                Assessment.identification_id == payload.identification_id,
                Assessment.id != assessment.id,
            )
        )
        if duplicate is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An assessment already exists for this identification.",
            )

    if assessment is None and identification is not None:
        existing = db.scalar(
            select(Assessment).where(
                Assessment.user_id == user.id,
                Assessment.identification_id == identification.id,
            )
        )
        if existing is not None:
            assessment = existing

    if assessment is None:
        assessment = Assessment(user_id=user.id)

    assessment.identification_id = identification.id if identification is not None else None

    condition = derive_condition(age_years, working, physical_damage)
    photo_name = identification.original_filename if identification else ""
    result = estimate_identification(
        device,
        condition,
        age_years,
        working,
        seed_text=f"{brand}|{model}|{photo_name}",
        battery_condition=battery_condition,
        physical_damage=physical_damage,
        description=description or "",
    )
    _apply_estimate(assessment, result, brand, model, description)

    recommendation_data = compute_recommendation(assessment)
    selected_pathway = payload.selected_pathway or recommendation_data["pathway"]
    try:
        assert_pathway_allowed(battery_condition, selected_pathway)
    except SafetyViolation as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    assessment.pathway = selected_pathway

    if assessment.id is None:
        db.add(assessment)
    db.flush()

    store_recommendation(db, assessment, recommendation_data)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A duplicate assessment record already exists.",
        ) from exc
    db.refresh(assessment)
    return assessment


def create_assessment(db: Session, user: User, payload: AssessmentCreate) -> Assessment:
    return _apply_assessment(db, user, payload, None)


def update_assessment(
    db: Session, user: User, assessment: Assessment, payload: AssessmentUpdate
) -> Assessment:
    return _apply_assessment(db, user, payload, assessment)
