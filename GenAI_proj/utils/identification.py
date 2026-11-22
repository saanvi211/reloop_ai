from __future__ import annotations

import hashlib
import random

from data.mock_data import IDENTIFY_CATEGORIES

KEYWORDS = {
    "Phone": ("phone", "mobile", "smartphone", "iphone", "galaxy", "pixel"),
    "Charger": ("charger", "adapter", "brick", "power adapter"),
    "Power Bank": ("powerbank", "power-bank", "power bank", "battery pack"),
    "Earbuds": ("earbud", "earphone", "airpod", "headphone", "buds"),
    "Laptop": ("laptop", "notebook", "macbook", "thinkpad", "chromebook"),
    "Cable": ("cable", "wire", "usb", "lightning", "type-c", "typec"),
    "Battery": ("battery", "cell", "lithium", "li-ion", "liion"),
    "Small Appliance": ("appliance", "kettle", "toaster", "blender", "iron", "mixer", "microwave"),
}

CATEGORY_BIAS = {
    "Phone": 1.0,
    "Charger": 0.8,
    "Power Bank": 0.65,
    "Earbuds": 0.7,
    "Laptop": 0.9,
    "Cable": 0.75,
    "Battery": 0.55,
    "Small Appliance": 0.5,
}


def _keyword_hint(text: str) -> str | None:
    lowered = text.lower()
    for category, words in KEYWORDS.items():
        if any(word in lowered for word in words):
            return category
    return None


def _seed_from(data: bytes | None, filename: str, hint: str) -> str:
    payload = (data or b"") + (filename or "").encode("utf-8") + (hint or "").encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()
    return digest[:16]


def predict_from_image(
    data: bytes | None,
    filename: str = "",
    hint: str = "",
) -> dict:
    """Deterministic mock classifier. Replace this function with an ML call later."""
    seed = _seed_from(data, filename, hint)
    rng = random.Random(seed)
    hinted = _keyword_hint(f"{filename} {hint}")

    candidates = list(IDENTIFY_CATEGORIES)
    rng.shuffle(candidates)
    if hinted:
        candidates.remove(hinted)
        candidates.insert(0, hinted)
    else:
        candidates.sort(key=lambda item: CATEGORY_BIAS.get(item, 0.5) + rng.uniform(0, 0.55), reverse=True)

    top = candidates[:3]
    if hinted:
        primary = round(rng.uniform(0.78, 0.96), 3)
    elif data:
        primary = round(rng.uniform(0.42, 0.9), 3)
    else:
        primary = round(rng.uniform(0.34, 0.6), 3)

    remaining = max(0.02, 1 - primary)
    second = round(remaining * rng.uniform(0.55, 0.75), 3)
    third = round(max(0.01, remaining - second), 3)

    predictions = [
        {"category": top[0], "confidence": primary},
        {"category": top[1], "confidence": second},
        {"category": top[2], "confidence": third},
    ]
    predictions.sort(key=lambda item: item["confidence"], reverse=True)
    return {
        "device": predictions[0]["category"],
        "confidence": predictions[0]["confidence"],
        "predictions": predictions,
        "needs_review": predictions[0]["confidence"] < 0.6,
        "method": "mock-classifier",
        "hint_matched": hinted,
        "source": filename or ("camera capture" if data else "manual"),
    }


def manual_identification(category: str) -> dict:
    return {
        "device": category,
        "confidence": 1.0,
        "predictions": [{"category": category, "confidence": 1.0}],
        "needs_review": False,
        "method": "manual",
        "hint_matched": None,
        "source": "manual selection",
    }
