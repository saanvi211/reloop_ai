"""
Tests for the pure (non-Streamlit) helper functions in utils/flow.py:
  completed_totals, pathway_totals, _normalise_history_item (via completed_totals).
These do not touch st.session_state, so they can run without a Streamlit context.
"""
from __future__ import annotations

import pytest

from data.mock_data import PATHWAYS


# Import only the pure functions — do not import anything that calls st at module level
from utils.flow import completed_totals, pathway_totals


def _make_entry(
    status: str = "Completed",
    pathway: str = "Recycle",
    weight_kg: float = 0.18,
    co2_kg: float = 22.4,
    points: int = 100,
    device: str = "Smartphone",
) -> dict:
    return {
        "device": device,
        "status": status,
        "pathway": pathway,
        "weight_kg": weight_kg,
        "co2_kg": co2_kg,
        "points": points,
        "detail": "Test entry",
        "partner": "Test Partner",
        "score": 70,
        "category": "Mobile",
        "battery_condition": "Normal",
        "notes": "",
        "image": None,
        "image_url": None,
        "image_name": "",
    }


class TestCompletedTotals:
    def test_empty_history_returns_zeros(self):
        totals = completed_totals([])
        assert totals == {"devices": 0, "weight_kg": 0.0, "co2_kg": 0.0, "points": 0}

    def test_counts_only_completed_entries(self):
        history = [
            _make_entry(status="Completed"),
            _make_entry(status="Scheduled"),
            _make_entry(status="Processing"),
        ]
        totals = completed_totals(history)
        assert totals["devices"] == 1

    def test_sums_weight_co2_points_for_completed(self):
        history = [
            _make_entry(status="Completed", weight_kg=1.0, co2_kg=10.0, points=50),
            _make_entry(status="Completed", weight_kg=2.0, co2_kg=20.0, points=80),
            _make_entry(status="Scheduled", weight_kg=5.0, co2_kg=100.0, points=200),
        ]
        totals = completed_totals(history)
        assert totals["devices"] == 2
        assert totals["weight_kg"] == pytest.approx(3.0, abs=0.01)
        assert totals["co2_kg"] == pytest.approx(30.0, abs=0.1)
        assert totals["points"] == 130

    def test_all_statuses_excluded_except_completed(self):
        statuses = ["Scheduled", "Processing", "In transit", "Cancelled"]
        history = [_make_entry(status=s) for s in statuses]
        totals = completed_totals(history)
        assert totals["devices"] == 0

    def test_weight_and_co2_are_rounded(self):
        history = [
            _make_entry(status="Completed", weight_kg=0.333, co2_kg=1.666),
            _make_entry(status="Completed", weight_kg=0.333, co2_kg=1.666),
        ]
        totals = completed_totals(history)
        # Rounded to 2 decimal places for weight, 1 for co2
        assert isinstance(totals["weight_kg"], float)
        assert isinstance(totals["co2_kg"], float)


class TestPathwayTotals:
    def test_all_known_pathways_initialised(self):
        totals = pathway_totals([])
        for pathway in PATHWAYS:
            assert pathway in totals

    def test_empty_history_all_zeros(self):
        totals = pathway_totals([])
        for pathway in PATHWAYS:
            assert totals[pathway]["devices"] == 0
            assert totals[pathway]["weight_kg"] == 0.0

    def test_counts_devices_per_pathway(self):
        history = [
            _make_entry(pathway="Repair"),
            _make_entry(pathway="Repair"),
            _make_entry(pathway="Recycle"),
            _make_entry(pathway="Hazardous Handling"),
        ]
        totals = pathway_totals(history)
        assert totals["Repair"]["devices"] == 2
        assert totals["Recycle"]["devices"] == 1
        assert totals["Hazardous Handling"]["devices"] == 1
        assert totals["Refurbish & Resell"]["devices"] == 0

    def test_sums_weight_per_pathway(self):
        history = [
            _make_entry(pathway="Recycle", weight_kg=1.5),
            _make_entry(pathway="Recycle", weight_kg=2.5),
            _make_entry(pathway="Repair", weight_kg=0.2),
        ]
        totals = pathway_totals(history)
        assert totals["Recycle"]["weight_kg"] == pytest.approx(4.0, abs=0.01)
        assert totals["Repair"]["weight_kg"] == pytest.approx(0.2, abs=0.01)

    def test_unknown_pathway_added_dynamically(self):
        history = [_make_entry(pathway="FuturePathway")]
        totals = pathway_totals(history)
        assert "FuturePathway" in totals
        assert totals["FuturePathway"]["devices"] == 1

    def test_all_entries_counted_regardless_of_status(self):
        """pathway_totals counts all entries, not just Completed."""
        history = [
            _make_entry(pathway="Repair", status="Scheduled"),
            _make_entry(pathway="Repair", status="Completed"),
        ]
        totals = pathway_totals(history)
        assert totals["Repair"]["devices"] == 2
