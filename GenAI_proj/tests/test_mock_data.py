"""
Tests for data/mock_data.py
Covers: COLLECTION_POINTS structure, DEVICE_CATALOG completeness,
        IDENTIFY_CATEGORIES / CATEGORY_TO_DEVICE consistency,
        HAZARDOUS_BATTERY_CONDITIONS, PATHWAYS, and ancillary data.
"""
from __future__ import annotations

import pytest

from data import mock_data as d


# ---------------------------------------------------------------------------
# COLLECTION_POINTS
# ---------------------------------------------------------------------------

class TestCollectionPoints:
    REQUIRED_FIELDS = ["name", "type", "area", "address", "lat", "lon",
                       "hours", "open_now", "accepted", "capacity",
                       "rating", "distance_km", "partner",
                       "id", "fictional", "phone", "email", "speciality"]

    def test_minimum_partner_count(self):
        """Directory must have at least 13 entries (11 original + 2 repair shops)."""
        assert len(d.COLLECTION_POINTS) >= 13

    def test_all_required_fields_present(self):
        for point in d.COLLECTION_POINTS:
            missing = [f for f in self.REQUIRED_FIELDS if f not in point]
            assert missing == [], f"{point['name']} is missing fields: {missing}"

    def test_coordinates_within_bengaluru_bounds(self):
        """All lat/lon must fall within a generous bounding box around Bengaluru."""
        for point in d.COLLECTION_POINTS:
            assert 12.7 <= point["lat"] <= 13.3, \
                f"{point['name']} lat {point['lat']} outside Bengaluru bounds"
            assert 77.3 <= point["lon"] <= 77.9, \
                f"{point['name']} lon {point['lon']} outside Bengaluru bounds"

    def test_capacity_valid_percentage(self):
        for point in d.COLLECTION_POINTS:
            assert 0 <= point["capacity"] <= 100, \
                f"{point['name']} capacity {point['capacity']} not in 0–100"

    def test_rating_valid_range(self):
        for point in d.COLLECTION_POINTS:
            assert 1.0 <= point["rating"] <= 5.0, \
                f"{point['name']} rating {point['rating']} not in 1–5"

    def test_distance_km_positive(self):
        for point in d.COLLECTION_POINTS:
            assert point["distance_km"] > 0, \
                f"{point['name']} has non-positive distance_km"

    def test_accepted_is_non_empty_list(self):
        for point in d.COLLECTION_POINTS:
            assert isinstance(point["accepted"], list), \
                f"{point['name']} accepted is not a list"
            assert len(point["accepted"]) > 0, \
                f"{point['name']} has empty accepted list"

    def test_fictional_flag_is_true(self):
        for point in d.COLLECTION_POINTS:
            assert point["fictional"] is True, \
                f"{point['name']} fictional flag is not True"

    def test_all_facility_types_represented(self):
        types_present = {p["type"] for p in d.COLLECTION_POINTS}
        expected = {"Recycling Centre", "Drop-off", "Refurbisher", "Kiosk", "Repair Shop"}
        assert expected.issubset(types_present), \
            f"Missing facility types: {expected - types_present}"

    def test_names_are_unique(self):
        names = [p["name"] for p in d.COLLECTION_POINTS]
        assert len(names) == len(set(names)), "Duplicate partner names found"

    def test_ids_are_unique(self):
        ids = [p["id"] for p in d.COLLECTION_POINTS]
        assert len(ids) == len(set(ids)), "Duplicate partner IDs found"


# ---------------------------------------------------------------------------
# DEVICE_CATALOG
# ---------------------------------------------------------------------------

class TestDeviceCatalog:
    REQUIRED_KEYS = ["category", "weight_kg", "base_value",
                     "co2_kg", "recyclable_pct", "materials"]

    def test_all_mapped_devices_in_catalog(self):
        """Every value in CATEGORY_TO_DEVICE must exist in DEVICE_CATALOG."""
        for category, device in d.CATEGORY_TO_DEVICE.items():
            assert device in d.DEVICE_CATALOG, \
                f"Category '{category}' maps to '{device}' which is not in DEVICE_CATALOG"

    def test_all_entries_have_required_keys(self):
        for device, spec in d.DEVICE_CATALOG.items():
            missing = [k for k in self.REQUIRED_KEYS if k not in spec]
            assert missing == [], f"{device} missing keys: {missing}"

    def test_materials_sum_to_100(self):
        for device, spec in d.DEVICE_CATALOG.items():
            total = sum(spec["materials"].values())
            assert total == 100, \
                f"{device} material percentages sum to {total}, not 100"

    def test_recyclable_pct_in_valid_range(self):
        for device, spec in d.DEVICE_CATALOG.items():
            assert 0 < spec["recyclable_pct"] <= 100, \
                f"{device} recyclable_pct {spec['recyclable_pct']} out of range"

    def test_weights_are_positive(self):
        for device, spec in d.DEVICE_CATALOG.items():
            assert spec["weight_kg"] > 0, f"{device} has non-positive weight_kg"

    def test_base_values_are_positive(self):
        for device, spec in d.DEVICE_CATALOG.items():
            assert spec["base_value"] > 0, f"{device} has non-positive base_value"

    def test_co2_values_are_positive(self):
        for device, spec in d.DEVICE_CATALOG.items():
            assert spec["co2_kg"] > 0, f"{device} has non-positive co2_kg"


# ---------------------------------------------------------------------------
# IDENTIFY_CATEGORIES / CATEGORY_TO_DEVICE consistency
# ---------------------------------------------------------------------------

class TestCategories:
    def test_exactly_eight_identify_categories(self):
        assert len(d.IDENTIFY_CATEGORIES) == 8, \
            f"Expected 8 categories, got {len(d.IDENTIFY_CATEGORIES)}"

    def test_category_to_device_covers_all_identify_categories(self):
        for cat in d.IDENTIFY_CATEGORIES:
            assert cat in d.CATEGORY_TO_DEVICE, \
                f"IDENTIFY_CATEGORY '{cat}' has no entry in CATEGORY_TO_DEVICE"

    def test_no_duplicate_identify_categories(self):
        assert len(d.IDENTIFY_CATEGORIES) == len(set(d.IDENTIFY_CATEGORIES)), \
            "Duplicate entries in IDENTIFY_CATEGORIES"


# ---------------------------------------------------------------------------
# BATTERY_CONDITIONS and HAZARDOUS_BATTERY_CONDITIONS
# ---------------------------------------------------------------------------

class TestBatteryConditions:
    def test_hazardous_conditions_are_subset_of_all(self):
        assert d.HAZARDOUS_BATTERY_CONDITIONS.issubset(set(d.BATTERY_CONDITIONS)), \
            "HAZARDOUS_BATTERY_CONDITIONS contains values not in BATTERY_CONDITIONS"

    def test_normal_is_not_hazardous(self):
        assert "Normal" not in d.HAZARDOUS_BATTERY_CONDITIONS

    def test_swollen_overheating_leaking_are_hazardous(self):
        for condition in ("Swollen", "Overheating", "Leaking"):
            assert condition in d.HAZARDOUS_BATTERY_CONDITIONS, \
                f"'{condition}' should be in HAZARDOUS_BATTERY_CONDITIONS"

    def test_unknown_is_not_hazardous(self):
        assert "Unknown" not in d.HAZARDOUS_BATTERY_CONDITIONS


# ---------------------------------------------------------------------------
# PATHWAYS
# ---------------------------------------------------------------------------

class TestPathways:
    def test_five_pathways_defined(self):
        assert len(d.PATHWAYS) == 5

    def test_all_pathway_names_present(self):
        expected = {"Repair", "Refurbish & Resell", "Harvest Components",
                    "Recycle", "Hazardous Handling"}
        assert set(d.PATHWAYS.keys()) == expected

    def test_each_pathway_has_meta_fields(self):
        required = ["title", "description", "icon", "tone", "color"]
        for name, meta in d.PATHWAYS.items():
            missing = [f for f in required if f not in meta]
            assert missing == [], f"Pathway '{name}' missing meta fields: {missing}"
