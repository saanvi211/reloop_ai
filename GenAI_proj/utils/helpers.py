from __future__ import annotations

import random

from data.mock_data import (
    CATEGORY_TO_DEVICE,
    CONDITIONS,
    DEVICE_CATALOG,
    DEVICE_CATEGORY_GROUP,
    GUIDANCE,
    HAZARDOUS_BATTERY_CONDITIONS,
)

ACCEPTED_TYPE_BY_DEVICE = {
    "Smartphone": "Smartphones",
    "Laptop": "Laptops",
    "Tablet": "Tablets",
    "Charger & cables": "Cables",
    "Monitor": "Monitors",
    "Desktop PC": "Desktops",
    "Printer": "Printers",
    "Television": "Appliances",
    "Refrigerator": "Appliances",
    "Washing machine": "Appliances",
    "Microwave": "Appliances",
    "Battery": "Batteries",
    "Power Bank": "Batteries",
    "Earbuds": "Cables",
    "Cable": "Cables",
    "Small Appliance": "Appliances",
}

DEVICE_ICONS = {
    "Smartphone": "phone",
    "Laptop": "laptop",
    "Tablet": "phone",
    "Charger & cables": "zap",
    "Monitor": "monitor",
    "Desktop PC": "cpu",
    "Printer": "package",
    "Television": "monitor",
    "Refrigerator": "package",
    "Washing machine": "package",
    "Microwave": "package",
    "Battery": "battery",
    "Power Bank": "battery",
    "Earbuds": "phone",
    "Cable": "zap",
    "Small Appliance": "package",
}

DAMAGE_PENALTY = {"None": 0, "Minor": 4, "Moderate": 12, "Major": 24}
DAMAGE_VALUE_FACTOR = {"None": 1.0, "Minor": 0.92, "Moderate": 0.78, "Major": 0.55}


def device_from_category(category: str) -> str:
    return CATEGORY_TO_DEVICE.get(category, category)


def category_group(device: str) -> str:
    return DEVICE_CATEGORY_GROUP.get(device, "Other")


def derive_condition(age_years: int, working: bool, physical_damage: str) -> str:
    if not working:
        return "Non-working"
    if physical_damage == "Major":
        return "Poor"
    if physical_damage == "Moderate":
        return "Fair"
    if age_years >= 7:
        return "Fair"
    if physical_damage == "Minor" or age_years >= 4:
        return "Good"
    return "Excellent"


def accepted_type_for(device: str) -> str:
    return ACCEPTED_TYPE_BY_DEVICE.get(device, "All items")


def device_icon(device: str) -> str:
    return DEVICE_ICONS.get(device, "cpu")


def format_indian(value: int | float) -> str:
    number = int(round(value))
    text = str(abs(number))
    if len(text) <= 3:
        grouped = text
    else:
        head, tail = text[:-3], text[-3:]
        chunks = []
        while len(head) > 2:
            chunks.insert(0, head[-2:])
            head = head[:-2]
        if head:
            chunks.insert(0, head)
        grouped = ",".join(chunks + [tail])
    return f"-{grouped}" if number < 0 else grouped


def format_number(value: int | float) -> str:
    return format_indian(value)


def format_currency(value: int | float) -> str:
    return f"₹{format_indian(value)}"


def format_weight(value: int | float) -> str:
    if value >= 1000:
        return f"{value / 1000:.2f} t"
    return f"{value:.1f} kg"


def format_compact(value: int | float) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}k"
    return str(int(value))


def initials(name: str) -> str:
    parts = [part for part in name.split() if part]
    return "".join(part[0].upper() for part in parts[:2])


def recyclability_band(score: int) -> dict:
    if score >= 80:
        return {"label": "Excellent", "tone": "green", "color": "#22A06B"}
    if score >= 60:
        return {"label": "Good", "tone": "teal", "color": "#2FBFA3"}
    if score >= 40:
        return {"label": "Moderate", "tone": "amber", "color": "#E0B45C"}
    return {"label": "Low", "tone": "coral", "color": "#E08A77"}


def estimate_identification(
    device: str,
    condition: str,
    age_years: int,
    working: bool,
    seed_text: str = "",
    battery_condition: str = "Normal",
    physical_damage: str = "None",
    description: str = "",
) -> dict:
    spec = DEVICE_CATALOG[device]
    condition_spec = CONDITIONS[condition]
    rng = random.Random(
        f"{device}|{condition}|{age_years}|{working}|{seed_text}|{battery_condition}|{physical_damage}"
    )

    age_factor = max(0.35, 1 - age_years * 0.055)
    value = spec["base_value"] * condition_spec["value_factor"] * age_factor
    value *= DAMAGE_VALUE_FACTOR.get(physical_damage, 1.0)
    if working:
        value *= 1.15
    if battery_condition in HAZARDOUS_BATTERY_CONDITIONS:
        value *= 0.35

    weight = round(spec["weight_kg"] * rng.uniform(0.92, 1.08), 2)
    co2 = round(spec["co2_kg"] * rng.uniform(0.9, 1.1), 1)
    score = condition_spec["score"] + (6 if working else -6) + rng.randint(-4, 4)
    score -= DAMAGE_PENALTY.get(physical_damage, 0)
    if battery_condition == "Normal":
        score += 2
    elif battery_condition == "Unknown":
        score -= 2
    elif battery_condition in HAZARDOUS_BATTERY_CONDITIONS:
        score -= 8
    score = max(12, min(98, score))
    recyclable_kg = round(weight * spec["recyclable_pct"] / 100, 2)
    band = recyclability_band(score)

    return {
        "device": device,
        "category": spec["category"],
        "category_group": DEVICE_CATEGORY_GROUP.get(device, "Other"),
        "condition": condition,
        "age_years": age_years,
        "working": working,
        "score": score,
        "band": band,
        "estimated_value": int(round(value)),
        "weight_kg": weight,
        "recyclable_kg": recyclable_kg,
        "co2_kg": co2,
        "recyclable_pct": spec["recyclable_pct"],
        "materials": spec["materials"],
        "guidance": GUIDANCE[spec["category"]],
        "battery_condition": battery_condition,
        "physical_damage": physical_damage,
        "description": description,
    }
