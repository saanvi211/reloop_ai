from __future__ import annotations

import random
from typing import Any

from utils import tf_identification


def predict_from_image(
    data: bytes | None,
    filename: str = "",
    hint: str = "",
) -> dict:
    """Tries TensorFlow model first. Raises exception if unavailable."""
    try:
        return tf_identification.predict_from_image(data, filename, hint)
    except Exception as exc:
        raise RuntimeError(
            "Image identification requires the TensorFlow model. "
            "Please provide a trained model at models/ewaste_model.keras"
        ) from exc


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
