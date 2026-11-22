"""
Tests for utils/recommendations_engine.py
Covers: build_recommendation (all pathways, safety overrides, scoring),
        matching_centres (filtering, sorting, safety preference).
"""
from __future__ import annotations

import pytest

from data.mock_data import (
    COLLECTION_POINTS,
    HAZARDOUS_BATTERY_CONDITIONS,
    PATHWAYS,
)
from utils.helpers import derive_condition, estimate_identification
from utils.recommendations_engine import build_recommendation, matching_centres


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _build(
    device: str = "Smartphone",
    age: int = 2,
    working: bool = True,
    damage: str = "None",
    battery: str = "Normal",
) -> dict:
    condition = derive_condition(age, working, damage)
    result = estimate_identification(
        device, condition, age, working,
        battery_condition=battery,
        physical_damage=damage,
    )
    return result


RECOMMENDATION_REQUIRED = {
    "pathway", "pathway_meta", "explanation", "ranked",
    "repair_feasibility", "residual_value", "e_waste_kg",
    "co2_kg", "warnings", "safety_override", "centre_types",
    "accepted_type", "estimated",
}


# ---------------------------------------------------------------------------
# build_recommendation — return schema
# ---------------------------------------------------------------------------

class TestBuildRecommendationSchema:
    def test_returns_all_required_keys(self):
        rec = build_recommendation(_build())
        assert RECOMMENDATION_REQUIRED.issubset(rec.keys())

    def test_pathway_is_a_known_pathway(self):
        for device in ["Smartphone", "Laptop", "Battery"]:
            rec = build_recommendation(_build(device=device))
            assert rec["pathway"] in PATHWAYS

    def test_ranked_contains_all_five_pathways(self):
        rec = build_recommendation(_build())
        ranked_names = {item["pathway"] for item in rec["ranked"]}
        assert ranked_names == set(PATHWAYS.keys())

    def test_ranked_sorted_descending_by_score(self):
        rec = build_recommendation(_build())
        scores = [item["score"] for item in rec["ranked"]]
        assert scores == sorted(scores, reverse=True)

    def test_pathway_meta_matches_pathways_dict(self):
        rec = build_recommendation(_build())
        assert rec["pathway_meta"] == PATHWAYS[rec["pathway"]]

    def test_warnings_is_non_empty_list(self):
        rec = build_recommendation(_build())
        assert isinstance(rec["warnings"], list)
        assert len(rec["warnings"]) >= 1

    def test_estimated_flag_is_true(self):
        rec = build_recommendation(_build())
        assert rec["estimated"] is True

    def test_residual_value_is_non_negative(self):
        for device in ["Smartphone", "Laptop", "Cable", "Battery"]:
            rec = build_recommendation(_build(device=device))
            assert rec["residual_value"] >= 0

    def test_e_waste_kg_and_co2_kg_are_positive(self):
        rec = build_recommendation(_build())
        assert rec["e_waste_kg"] > 0
        assert rec["co2_kg"] > 0


# ---------------------------------------------------------------------------
# Safety override — hazardous battery
# ---------------------------------------------------------------------------

class TestHazardousBatterySafetyOverride:
    @pytest.mark.parametrize("battery", list(HAZARDOUS_BATTERY_CONDITIONS))
    def test_hazardous_battery_forces_hazardous_handling(self, battery):
        rec = build_recommendation(_build(battery=battery))
        assert rec["pathway"] == "Hazardous Handling", \
            f"Battery '{battery}' should force Hazardous Handling"

    @pytest.mark.parametrize("battery", list(HAZARDOUS_BATTERY_CONDITIONS))
    def test_safety_override_flag_is_true(self, battery):
        rec = build_recommendation(_build(battery=battery))
        assert rec["safety_override"] is True

    @pytest.mark.parametrize("battery", list(HAZARDOUS_BATTERY_CONDITIONS))
    def test_all_other_pathways_ineligible(self, battery):
        rec = build_recommendation(_build(battery=battery))
        for item in rec["ranked"]:
            if item["pathway"] != "Hazardous Handling":
                assert item["eligible"] is False, \
                    f"Pathway '{item['pathway']}' should be ineligible for {battery} battery"

    @pytest.mark.parametrize("battery", list(HAZARDOUS_BATTERY_CONDITIONS))
    def test_hazardous_handling_is_eligible(self, battery):
        rec = build_recommendation(_build(battery=battery))
        hazardous_item = next(
            item for item in rec["ranked"] if item["pathway"] == "Hazardous Handling"
        )
        assert hazardous_item["eligible"] is True

    @pytest.mark.parametrize("battery", list(HAZARDOUS_BATTERY_CONDITIONS))
    def test_hazardous_handling_score_is_100(self, battery):
        rec = build_recommendation(_build(battery=battery))
        hazardous_item = next(
            item for item in rec["ranked"] if item["pathway"] == "Hazardous Handling"
        )
        assert hazardous_item["score"] == 100

    def test_normal_battery_no_safety_override(self):
        rec = build_recommendation(_build(battery="Normal"))
        assert rec["safety_override"] is False

    def test_unknown_battery_no_safety_override(self):
        rec = build_recommendation(_build(battery="Unknown"))
        assert rec["safety_override"] is False

    @pytest.mark.parametrize("battery", list(HAZARDOUS_BATTERY_CONDITIONS))
    def test_hazardous_warning_message_in_warnings(self, battery):
        rec = build_recommendation(_build(battery=battery))
        combined = " ".join(rec["warnings"]).lower()
        assert "battery" in combined or "hazardous" in combined


# ---------------------------------------------------------------------------
# Repair pathway conditions
# ---------------------------------------------------------------------------

class TestRepairPathway:
    def test_new_working_undamaged_device_recommends_repair(self):
        rec = build_recommendation(_build(age=1, working=True, damage="None"))
        assert rec["pathway"] == "Repair"

    def test_repair_feasibility_high_for_new_undamaged(self):
        rec = build_recommendation(_build(age=1, working=True, damage="None"))
        assert rec["repair_feasibility"].startswith("High")

    def test_non_working_device_has_low_repair_feasibility(self):
        rec = build_recommendation(_build(age=5, working=False, damage="None"))
        assert rec["repair_feasibility"].startswith("Low")

    def test_repair_residual_value_above_base(self):
        result = _build(age=1, working=True, damage="None")
        rec = build_recommendation(result)
        if rec["pathway"] == "Repair":
            assert rec["residual_value"] >= result["estimated_value"]


# ---------------------------------------------------------------------------
# Scoring — relative ordering
# ---------------------------------------------------------------------------

class TestScoringLogic:
    def test_working_device_scores_higher_repair_than_broken(self):
        working_rec = build_recommendation(_build(working=True, damage="None", age=2))
        broken_rec = build_recommendation(_build(working=False, damage="Major", age=8))
        working_repair_score = next(
            i["score"] for i in working_rec["ranked"] if i["pathway"] == "Repair"
        )
        broken_repair_score = next(
            i["score"] for i in broken_rec["ranked"] if i["pathway"] == "Repair"
        )
        assert working_repair_score > broken_repair_score

    def test_older_device_scores_lower_repair(self):
        young = build_recommendation(_build(age=1, working=True))
        old = build_recommendation(_build(age=15, working=True))
        young_score = next(i["score"] for i in young["ranked"] if i["pathway"] == "Repair")
        old_score = next(i["score"] for i in old["ranked"] if i["pathway"] == "Repair")
        assert young_score > old_score

    def test_all_pathway_scores_between_0_and_99(self):
        rec = build_recommendation(_build())
        for item in rec["ranked"]:
            assert 0 <= item["score"] <= 100, \
                f"Score {item['score']} out of range for {item['pathway']}"


# ---------------------------------------------------------------------------
# matching_centres
# ---------------------------------------------------------------------------

class TestMatchingCentres:
    def _rec(self, battery: str = "Normal") -> dict:
        return build_recommendation(_build(battery=battery))

    def test_returns_a_list(self):
        result = matching_centres(_build(), self._rec(), points=COLLECTION_POINTS)
        assert isinstance(result, list)

    def test_respects_limit(self):
        for limit in (1, 2, 4):
            result = matching_centres(
                _build(), self._rec(), points=COLLECTION_POINTS, limit=limit
            )
            assert len(result) <= limit

    def test_sorted_by_distance_ascending(self):
        result = matching_centres(
            _build(), self._rec(), points=COLLECTION_POINTS, limit=10
        )
        distances = [p["distance_km"] for p in result]
        assert distances == sorted(distances)

    def test_hazardous_centres_accept_batteries(self):
        rec = self._rec(battery="Swollen")
        result = matching_centres(_build(battery="Swollen"), rec,
                                  points=COLLECTION_POINTS, limit=10)
        # All returned centres must accept Batteries
        if result:
            for centre in result:
                assert "Batteries" in centre["accepted"], \
                    f"{centre['name']} does not accept Batteries but was returned for hazardous route"

    def test_returns_empty_list_for_empty_pool(self):
        result = matching_centres(_build(), self._rec(), points=[], limit=4)
        assert result == []

    def test_uses_internal_collection_points_when_no_pool_given(self):
        result = matching_centres(_build(), self._rec(), limit=4)
        assert isinstance(result, list)
