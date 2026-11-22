"""
Tests for utils/helpers.py
Covers: derive_condition, estimate_identification, format_* functions,
        device_from_category, accepted_type_for, recyclability_band.
"""
from __future__ import annotations

import pytest

from data.mock_data import (
    BATTERY_CONDITIONS,
    CATEGORY_TO_DEVICE,
    DAMAGE_LEVELS,
    DEVICE_CATALOG,
    HAZARDOUS_BATTERY_CONDITIONS,
    IDENTIFY_CATEGORIES,
)
from utils.helpers import (
    accepted_type_for,
    derive_condition,
    device_from_category,
    estimate_identification,
    format_currency,
    format_indian,
    format_number,
    recyclability_band,
)


# ---------------------------------------------------------------------------
# derive_condition
# ---------------------------------------------------------------------------

class TestDeriveCondition:
    def test_non_working_always_non_working(self):
        for damage in DAMAGE_LEVELS:
            for age in (0, 3, 7, 10):
                assert derive_condition(age, False, damage) == "Non-working"

    def test_major_damage_gives_poor(self):
        assert derive_condition(1, True, "Major") == "Poor"

    def test_moderate_damage_gives_fair(self):
        assert derive_condition(1, True, "Moderate") == "Fair"

    def test_old_device_gives_fair(self):
        assert derive_condition(8, True, "None") == "Fair"

    def test_minor_damage_gives_good(self):
        assert derive_condition(2, True, "Minor") == "Good"

    def test_new_undamaged_gives_excellent(self):
        assert derive_condition(1, True, "None") == "Excellent"

    def test_age_boundary_four_years(self):
        # age >= 4 with no damage -> Good (not Excellent)
        assert derive_condition(4, True, "None") == "Good"

    def test_valid_conditions_returned(self):
        valid = {"Non-working", "Poor", "Fair", "Good", "Excellent"}
        for age in (0, 2, 5, 8):
            for working in (True, False):
                for damage in DAMAGE_LEVELS:
                    result = derive_condition(age, working, damage)
                    assert result in valid, f"Unexpected condition '{result}'"


# ---------------------------------------------------------------------------
# estimate_identification
# ---------------------------------------------------------------------------

ESTIMATE_REQUIRED = {
    "device", "condition", "age_years", "working", "score", "band",
    "estimated_value", "weight_kg", "recyclable_kg", "co2_kg",
    "recyclable_pct", "materials", "guidance", "battery_condition",
    "physical_damage", "category",
}

class TestEstimateIdentification:
    def test_returns_all_required_keys(self):
        result = estimate_identification("Smartphone", "Good", 2, True)
        assert ESTIMATE_REQUIRED.issubset(result.keys())

    def test_score_within_valid_range(self):
        for device in DEVICE_CATALOG:
            result = estimate_identification(device, "Good", 2, True)
            assert 0 <= result["score"] <= 100, \
                f"{device} score {result['score']} out of range"

    def test_recyclable_kg_leq_weight_kg(self):
        for device in DEVICE_CATALOG:
            result = estimate_identification(device, "Fair", 4, True)
            assert result["recyclable_kg"] <= result["weight_kg"] + 0.001, \
                f"{device} recyclable_kg > weight_kg"

    def test_hazardous_battery_reduces_score(self):
        base = estimate_identification("Smartphone", "Good", 2, True,
                                       battery_condition="Normal")
        hazardous = estimate_identification("Smartphone", "Good", 2, True,
                                            battery_condition="Swollen")
        assert hazardous["score"] < base["score"]

    def test_hazardous_battery_reduces_value(self):
        base = estimate_identification("Smartphone", "Good", 2, True,
                                       battery_condition="Normal")
        hazardous = estimate_identification("Smartphone", "Good", 2, True,
                                            battery_condition="Leaking")
        assert hazardous["estimated_value"] < base["estimated_value"]

    def test_major_damage_reduces_score(self):
        no_damage = estimate_identification("Laptop", "Good", 3, True,
                                            physical_damage="None")
        major = estimate_identification("Laptop", "Good", 3, True,
                                        physical_damage="Major")
        assert major["score"] < no_damage["score"]

    def test_non_working_reduces_score(self):
        working = estimate_identification("Smartphone", "Good", 2, True)
        broken = estimate_identification("Smartphone", "Non-working", 2, False)
        assert broken["score"] < working["score"]

    def test_deterministic_with_same_inputs(self):
        r1 = estimate_identification("Laptop", "Good", 3, True,
                                     seed_text="test", battery_condition="Normal")
        r2 = estimate_identification("Laptop", "Good", 3, True,
                                     seed_text="test", battery_condition="Normal")
        assert r1["score"] == r2["score"]
        assert r1["weight_kg"] == r2["weight_kg"]
        assert r1["estimated_value"] == r2["estimated_value"]

    def test_device_field_matches_input(self):
        for device in DEVICE_CATALOG:
            result = estimate_identification(device, "Fair", 3, True)
            assert result["device"] == device

    def test_band_label_is_valid(self):
        valid_labels = {"Excellent", "Good", "Moderate", "Low"}
        for device in list(DEVICE_CATALOG.keys())[:5]:
            result = estimate_identification(device, "Good", 2, True)
            assert result["band"]["label"] in valid_labels

    def test_all_device_catalog_entries_work(self):
        for device in DEVICE_CATALOG:
            result = estimate_identification(device, "Good", 2, True)
            assert result["score"] >= 0


# ---------------------------------------------------------------------------
# device_from_category
# ---------------------------------------------------------------------------

class TestDeviceFromCategory:
    def test_all_identify_categories_map_correctly(self):
        for category in IDENTIFY_CATEGORIES:
            result = device_from_category(category)
            assert result in DEVICE_CATALOG, \
                f"'{category}' maps to '{result}' which is not in DEVICE_CATALOG"

    def test_unknown_category_returns_itself(self):
        assert device_from_category("UnknownWidget") == "UnknownWidget"

    def test_phone_maps_to_smartphone(self):
        assert device_from_category("Phone") == "Smartphone"

    def test_charger_maps_to_charger_and_cables(self):
        assert device_from_category("Charger") == "Charger & cables"


# ---------------------------------------------------------------------------
# accepted_type_for
# ---------------------------------------------------------------------------

class TestAcceptedTypeFor:
    def test_smartphone_maps_to_smartphones(self):
        assert accepted_type_for("Smartphone") == "Smartphones"

    def test_battery_maps_to_batteries(self):
        assert accepted_type_for("Battery") == "Batteries"

    def test_unknown_device_returns_all_items(self):
        assert accepted_type_for("GadgetX") == "All items"

    def test_all_catalog_devices_return_a_string(self):
        for device in DEVICE_CATALOG:
            result = accepted_type_for(device)
            assert isinstance(result, str) and len(result) > 0


# ---------------------------------------------------------------------------
# recyclability_band
# ---------------------------------------------------------------------------

class TestRecyclabilityBand:
    def test_score_80_plus_is_excellent(self):
        assert recyclability_band(80)["label"] == "Excellent"
        assert recyclability_band(99)["label"] == "Excellent"

    def test_score_60_79_is_good(self):
        assert recyclability_band(60)["label"] == "Good"
        assert recyclability_band(79)["label"] == "Good"

    def test_score_40_59_is_moderate(self):
        assert recyclability_band(40)["label"] == "Moderate"
        assert recyclability_band(59)["label"] == "Moderate"

    def test_score_below_40_is_low(self):
        assert recyclability_band(0)["label"] == "Low"
        assert recyclability_band(39)["label"] == "Low"

    def test_band_has_tone_and_color(self):
        band = recyclability_band(75)
        assert "tone" in band
        assert "color" in band
        assert band["color"].startswith("#")


# ---------------------------------------------------------------------------
# format_* helpers
# ---------------------------------------------------------------------------

class TestFormatHelpers:
    def test_format_indian_zero(self):
        assert format_indian(0) == "0"

    def test_format_indian_hundreds(self):
        assert format_indian(999) == "999"

    def test_format_indian_thousands(self):
        assert format_indian(1000) == "1,000"

    def test_format_indian_lakhs(self):
        assert format_indian(100000) == "1,00,000"

    def test_format_indian_negative(self):
        assert format_indian(-500) == "-500"

    def test_format_number_delegates_correctly(self):
        assert format_number(2500) == format_indian(2500)

    def test_format_currency_prefixes_rupee(self):
        result = format_currency(1500)
        assert result.startswith("₹")
        assert "1,500" in result

    def test_format_currency_zero(self):
        assert format_currency(0) == "₹0"
