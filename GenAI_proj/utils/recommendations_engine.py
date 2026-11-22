from __future__ import annotations

from data import mock_data as d
from data.mock_data import HAZARDOUS_BATTERY_CONDITIONS, PATHWAYS
from utils.helpers import accepted_type_for

PATHWAY_ORDER = ["Repair", "Refurbish & Resell", "Harvest Components", "Recycle", "Hazardous Handling"]

CENTRE_TYPES = {
    "Repair": ["Repair Shop", "Refurbisher"],
    "Refurbish & Resell": ["Refurbisher", "Repair Shop"],
    "Harvest Components": ["Recycling Centre", "Drop-off"],
    "Recycle": ["Recycling Centre", "Drop-off", "Kiosk"],
    "Hazardous Handling": ["Recycling Centre", "Drop-off", "Kiosk"],
}

PATHWAY_NOTES = {
    "Repair": "Targeted repair is the lowest-carbon route when the device still works.",
    "Refurbish & Resell": "Refurbishment keeps the whole device in use and recovers resale value.",
    "Harvest Components": "Useful modules and materials can be recovered from a non-working unit.",
    "Recycle": "Verified material recovery is the safest option for a low-value device.",
    "Hazardous Handling": "Specialist handling is required because the battery may be unsafe.",
}


def _battery_is_hazardous(result: dict) -> bool:
    return result.get("battery_condition", "Unknown") in HAZARDOUS_BATTERY_CONDITIONS


def _repair_feasibility(result: dict) -> str:
    if _battery_is_hazardous(result):
        return "Not recommended — hazardous battery"
    if not result.get("working"):
        return "Low — device does not power on"
    damage = result.get("physical_damage", "None")
    age = int(result.get("age_years", 0))
    if damage in {"None", "Minor"} and age <= 3:
        return "High"
    if damage == "Moderate" or age <= 6:
        return "Medium"
    return "Low"


def _scores(result: dict) -> dict[str, int]:
    score = int(result.get("score", 50))
    age = int(result.get("age_years", 0))
    working = bool(result.get("working"))
    damage = result.get("physical_damage", "None")
    battery = result.get("battery_condition", "Normal")
    value = int(result.get("estimated_value", 0))
    damage_penalty = {"None": 0, "Minor": 8, "Moderate": 22, "Major": 38}.get(damage, 0)

    repair = (58 if working else 8) + max(-18, 14 - age * 3) - damage_penalty
    repair += 6 if battery == "Normal" else 0

    refurbish = (22 if working else 4) + score * 0.35 - age * 2.5 - damage_penalty * 0.4
    if value < 300:
        refurbish -= 18

    harvest = 30 + (28 if not working else 0) + min(24, score * 0.25) + damage_penalty * 0.35
    if result.get("category") == "Hazardous":
        harvest -= 30

    recycle = 38 + (24 if not working else 0) + damage_penalty * 0.5
    if battery == "Unknown":
        recycle += 4

    hazardous = 18 if battery == "Unknown" else 8

    return {
        "Repair": int(max(0, min(99, repair))),
        "Refurbish & Resell": int(max(0, min(99, refurbish))),
        "Harvest Components": int(max(0, min(99, harvest))),
        "Recycle": int(max(0, min(99, recycle))),
        "Hazardous Handling": int(max(0, min(99, hazardous))),
    }


def build_recommendation(result: dict) -> dict:
    battery = result.get("battery_condition", "Unknown")
    hazardous = _battery_is_hazardous(result)
    scores = _scores(result)
    reasons = dict(PATHWAY_NOTES)

    if hazardous:
        ranked = [{"pathway": "Hazardous Handling", "score": 100, "eligible": True, "reason": reasons["Hazardous Handling"]}]
        for pathway in PATHWAY_ORDER:
            if pathway == "Hazardous Handling":
                continue
            ranked.append(
                {
                    "pathway": pathway,
                    "score": 0,
                    "eligible": False,
                    "reason": f"Blocked by the safety override for a {battery.lower()} battery.",
                }
            )
        recommended = "Hazardous Handling"
    else:
        ranked = [
            {"pathway": pathway, "score": scores[pathway], "eligible": True, "reason": reasons[pathway]}
            for pathway in PATHWAY_ORDER
        ]
        ranked.sort(key=lambda item: item["score"], reverse=True)
        recommended = ranked[0]["pathway"]

    estimated_value = int(result.get("estimated_value", 0))
    if recommended == "Repair":
        residual = int(estimated_value * 1.15)
        diverted = round(float(result.get("weight_kg", 0)), 2)
        co2 = round(float(result.get("co2_kg", 0)) * 0.85, 1)
    elif recommended == "Refurbish & Resell":
        residual = int(estimated_value * 1.35)
        diverted = round(float(result.get("weight_kg", 0)), 2)
        co2 = round(float(result.get("co2_kg", 0)) * 0.95, 1)
    elif recommended == "Harvest Components":
        residual = int(estimated_value * 0.55)
        diverted = round(float(result.get("recyclable_kg", result.get("weight_kg", 0))), 2)
        co2 = round(float(result.get("co2_kg", 0)) * 0.7, 1)
    elif recommended == "Recycle":
        residual = int(estimated_value * 0.25)
        diverted = round(float(result.get("recyclable_kg", result.get("weight_kg", 0))), 2)
        co2 = round(float(result.get("co2_kg", 0)), 1)
    else:
        residual = 0
        diverted = round(float(result.get("weight_kg", 0)), 2)
        co2 = round(float(result.get("co2_kg", 0)) * 0.4, 1)

    warnings: list[str] = []
    if hazardous:
        warnings.append(
            f"Battery condition is {battery.lower()}. Do not open, charge, repair, resell or harvest this device."
        )
        warnings.append("Keep the device in a cool, dry, non-flammable place away from children and pets.")
        warnings.append("Use a specialist hazardous e-waste handler and tell them about the battery condition.")
    elif battery == "Unknown":
        warnings.append("Battery condition is unknown. Inspect for swelling or heat before transport and never puncture it.")
    if result.get("physical_damage") in {"Moderate", "Major"}:
        warnings.append("Physical damage may expose sharp edges or internal components. Handle with gloves.")
    if result.get("working"):
        warnings.append("Back up your data and factory reset the device before handing it over.")
    if not warnings:
        warnings.append("Back up your data, sign out of accounts and remove personal accessories before drop-off.")

    if hazardous:
        explanation = (
            "A swollen, overheating or leaking battery is a safety risk. ReLoop blocks repair, resale and "
            "component harvesting and routes this device only to specialist hazardous handling."
        )
    else:
        explanation = (
            f"With a {result.get('condition', 'fair').lower()} condition, {result.get('age_years', 0)}-year age "
            f"and {battery.lower()} battery, the {recommended.lower()} pathway has the best balance of safety, "
            "residual value and avoided emissions."
        )

    return {
        "pathway": recommended,
        "pathway_meta": PATHWAYS[recommended],
        "explanation": explanation,
        "ranked": ranked,
        "repair_feasibility": _repair_feasibility(result),
        "residual_value": residual,
        "e_waste_kg": diverted,
        "co2_kg": co2,
        "warnings": warnings,
        "safety_override": hazardous,
        "centre_types": CENTRE_TYPES[recommended],
        "accepted_type": accepted_type_for(result.get("device", "")),
        "estimated": True,
    }


def matching_centres(
    result: dict,
    recommendation: dict,
    points: list[dict] | None = None,
    limit: int = 4,
) -> list[dict]:
    pool = list(points) if points is not None else list(d.COLLECTION_POINTS)
    preferred_types = recommendation.get("centre_types", [])
    accepted = recommendation.get("accepted_type", "All items")

    typed = [point for point in pool if point["type"] in preferred_types]
    if typed:
        pool = typed

    if recommendation.get("safety_override"):
        safe = [point for point in pool if "Batteries" in point["accepted"]]
        if safe:
            pool = safe
    elif accepted != "All items":
        matching = [point for point in pool if accepted in point["accepted"]]
        if matching:
            pool = matching

    open_points = [point for point in pool if point["open_now"]]
    if open_points:
        pool = open_points

    return sorted(pool, key=lambda point: point["distance_km"])[:limit]
