"""
Tests for utils/identification.py
Covers: predict_from_image (mock classifier), manual_identification,
        return schema, confidence thresholds, keyword hints, determinism.
"""
from __future__ import annotations

import io

import pytest
from PIL import Image

from data.mock_data import IDENTIFY_CATEGORIES
from utils.identification import manual_identification, predict_from_image


def _make_png(color: tuple[int, int, int] = (100, 150, 200)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (32, 32), color).save(buf, format="PNG")
    return buf.getvalue()


REQUIRED_KEYS = {"device", "confidence", "predictions", "needs_review", "method", "source"}


class TestPredictFromImage:
    def test_returns_all_required_keys(self):
        result = predict_from_image(_make_png(), "phone.jpg")
        assert REQUIRED_KEYS.issubset(result.keys())

    def test_predicted_device_is_a_known_category(self):
        result = predict_from_image(_make_png(), "device.jpg")
        assert result["device"] in IDENTIFY_CATEGORIES

    def test_confidence_is_between_zero_and_one(self):
        result = predict_from_image(_make_png(), "device.jpg")
        assert 0.0 < result["confidence"] <= 1.0

    def test_predictions_list_has_three_entries(self):
        result = predict_from_image(_make_png(), "device.jpg")
        assert len(result["predictions"]) == 3

    def test_predictions_sum_less_than_or_equal_one(self):
        result = predict_from_image(_make_png(), "device.jpg")
        total = sum(p["confidence"] for p in result["predictions"])
        assert total <= 1.001  # floating point tolerance

    def test_predictions_sorted_descending_by_confidence(self):
        result = predict_from_image(_make_png(), "device.jpg")
        confs = [p["confidence"] for p in result["predictions"]]
        assert confs == sorted(confs, reverse=True)

    def test_top_prediction_matches_device_field(self):
        result = predict_from_image(_make_png(), "device.jpg")
        assert result["predictions"][0]["category"] == result["device"]

    def test_needs_review_true_when_confidence_below_threshold(self):
        # Force low confidence by providing no image data and no hint
        result = predict_from_image(None, "unknown.jpg", hint="")
        # needs_review should be consistent with confidence < 0.6
        expected = result["confidence"] < 0.6
        assert result["needs_review"] == expected

    def test_needs_review_false_when_confidence_high(self):
        # Strong keyword hint pushes confidence up
        result = predict_from_image(_make_png(), "phone.jpg", hint="smartphone")
        if result["confidence"] >= 0.6:
            assert result["needs_review"] is False

    def test_keyword_hint_biases_toward_correct_category(self):
        for hint, expected_category in [
            ("smartphone iphone", "Phone"),
            ("laptop macbook", "Laptop"),
            ("usb cable wire", "Cable"),
            ("battery lithium", "Battery"),
        ]:
            result = predict_from_image(_make_png(), "device.jpg", hint=hint)
            assert result["device"] == expected_category, \
                f"Hint '{hint}' should bias toward '{expected_category}', got '{result['device']}'"

    def test_deterministic_same_input_same_output(self):
        data = _make_png((10, 20, 30))
        r1 = predict_from_image(data, "test.jpg", hint="phone")
        r2 = predict_from_image(data, "test.jpg", hint="phone")
        assert r1["device"] == r2["device"]
        assert r1["confidence"] == r2["confidence"]

    def test_different_images_can_produce_different_results(self):
        r1 = predict_from_image(_make_png((0, 0, 0)), "a.jpg", hint="")
        r2 = predict_from_image(_make_png((255, 255, 255)), "b.jpg", hint="")
        # They might be the same or different — just check both are valid
        assert r1["device"] in IDENTIFY_CATEGORIES
        assert r2["device"] in IDENTIFY_CATEGORIES

    def test_method_field_is_mock_classifier(self):
        result = predict_from_image(_make_png(), "device.jpg")
        assert result["method"] == "mock-classifier"

    def test_no_image_data_still_returns_valid_result(self):
        result = predict_from_image(None, "device.jpg", hint="laptop")
        assert result["device"] in IDENTIFY_CATEGORIES
        assert 0.0 < result["confidence"] <= 1.0

    def test_all_prediction_categories_are_known(self):
        result = predict_from_image(_make_png(), "device.jpg")
        for pred in result["predictions"]:
            assert pred["category"] in IDENTIFY_CATEGORIES, \
                f"Prediction category '{pred['category']}' not in IDENTIFY_CATEGORIES"


class TestManualIdentification:
    def test_returns_all_required_keys(self):
        result = manual_identification("Laptop")
        assert REQUIRED_KEYS.issubset(result.keys())

    def test_device_matches_input_category(self):
        for category in IDENTIFY_CATEGORIES:
            result = manual_identification(category)
            assert result["device"] == category

    def test_confidence_is_one(self):
        result = manual_identification("Phone")
        assert result["confidence"] == 1.0

    def test_needs_review_is_false(self):
        result = manual_identification("Battery")
        assert result["needs_review"] is False

    def test_method_is_manual(self):
        result = manual_identification("Earbuds")
        assert result["method"] == "manual"

    def test_predictions_list_has_one_entry_at_full_confidence(self):
        result = manual_identification("Charger")
        assert len(result["predictions"]) == 1
        assert result["predictions"][0]["confidence"] == 1.0
