from __future__ import annotations

from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

from components import ui
from components.charts import area_chart, donut_chart, hbar_chart
from data import mock_data as d
from utils import api_client, flow
from utils.helpers import format_number
from utils.recommendations_engine import build_recommendation

DATE_RANGES = {
    "Last 30 days": 30,
    "Last 90 days": 90,
    "This year": None,
    "All time": None,
}

RANGE_PARAMS = {
    "Last 30 days": "30d",
    "Last 90 days": "90d",
    "This year": "year",
    "All time": "all",
}


def _parse_date(value: str) -> date:
    if str(value).lower() == "today":
        return date.today()
    for fmt in ("%d %b %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except (TypeError, ValueError):
            continue
    return date.today()


def _filter_history(history: list[dict], date_range: str, categories: list[str]) -> list[dict]:
    today = date.today()
    filtered = list(history)
    if date_range == "Last 30 days":
        cutoff = today - timedelta(days=30)
        filtered = [item for item in filtered if _parse_date(item["date"]) >= cutoff]
    elif date_range == "Last 90 days":
        cutoff = today - timedelta(days=90)
        filtered = [item for item in filtered if _parse_date(item["date"]) >= cutoff]
    elif date_range == "This year":
        filtered = [item for item in filtered if _parse_date(item["date"]).year == today.year]
    if categories:
        filtered = [item for item in filtered if item.get("category") in categories]
    return filtered


def _month_slice(date_range: str):
    if date_range == "Last 30 days":
        return d.MONTHLY_IMPACT.tail(1)
    if date_range == "Last 90 days":
        return d.MONTHLY_IMPACT.tail(3)
    if date_range == "This year":
        return d.MONTHLY_IMPACT.tail(11)
    return d.MONTHLY_IMPACT


def render() -> None:
    history = flow.get_history()
    user = flow.get_user()
    all_categories = sorted(
        {item.get("category", "Other") for item in history}
        | set(d.CATEGORY_BREAKDOWN["category"].tolist())
    )

    totals_all = flow.completed_totals(history)
    total_waste = int(totals_all["weight_kg"])
    total_devices = totals_all["devices"]

    ui.hero(
        eyebrow="Circular command centre",
        title=f"Welcome back, {user['first_name']}.",
        accent="Let's close the loop.",
        subtitle=(
            "Track assessments, recovery pathways and environmental outcomes. Filter by date and device "
            "category, then jump straight into the circular flow."
        ),
        chips=[
            {"icon": "recycle", "text": f"{format_number(total_waste)} kg diverted"},
            {"icon": "zap", "text": f"{user['streak_days']}-day recycling streak"},
            {"icon": "trophy", "text": f"{user['tier']} tier"},
            {"icon": "cpu", "text": f"{format_number(total_devices)} devices recovered"},
        ],
        ring_value=68,
        ring_label="circularity",
    )

    first, second, third, _ = st.columns([1, 1, 1, 2.2], gap="small")
    with first:
        if st.button(
            "Identify a device",
            type="primary",
            icon=":material/document_scanner:",
            width="stretch",
        ):
            st.switch_page("views/identify.py")
    with second:
        if st.button("Find a drop-off", icon=":material/location_on:", width="stretch"):
            st.switch_page("views/map_view.py")
    with third:
        if st.button("View impact", icon=":material/monitoring:", width="stretch"):
            st.switch_page("views/analytics.py")

    with st.container(border=True):
        ui.section_header(
            "Dashboard filters",
            "Filter KPIs, charts and activity by date range and device category",
            kicker="Filters",
        )
        range_col, category_col, reset_col = st.columns([1, 1.8, 0.6], gap="small")
        with range_col:
            date_range = st.selectbox("Date range", list(DATE_RANGES), key="dash_range")
        with category_col:
            categories = st.multiselect(
                "Device categories (leave empty for all)",
                all_categories,
                key="dash_categories",
                placeholder="All categories",
            )
        with reset_col:
            st.write("")
            if st.button("Reset filters", icon=":material/restart_alt:", width="stretch"):
                st.session_state.pop("dash_range", None)
                st.session_state.pop("dash_categories", None)
                st.rerun()

    filtered = _filter_history(history, date_range, categories)
    completed = [item for item in filtered if item["status"] == "Completed"]
    try:
        stats = api_client.dashboard_stats(RANGE_PARAMS.get(date_range, "all"), categories)
    except api_client.ApiError:
        stats = None

    if stats:
        totals = stats["totals"]
        assessed_count = totals["devices_assessed"]
        repaired = totals["repaired"]
        reused = totals["reused"]
        recycled = totals["recycled"] + totals["hazardous"]
        diverted_kg = round(totals["weight_kg"], 2)
        co2_kg = round(totals["co2_kg"], 1)
    else:
        assessed_count = len(filtered)
        repaired = sum(1 for item in completed if item.get("pathway") == "Repair")
        reused = sum(1 for item in completed if item.get("pathway") == "Refurbish & Resell")
        recycled = sum(
            1
            for item in completed
            if item.get("pathway") in {"Recycle", "Harvest Components", "Hazardous Handling"}
        )
        diverted_kg = round(sum(float(item["weight_kg"]) for item in completed), 2)
        co2_kg = round(sum(float(item["co2_kg"]) for item in completed), 1)

    st.caption(
        f"{assessed_count} assessed device(s) · {len(completed)} completed recovery record(s) · "
        f"filter: {date_range}{' · ' + ', '.join(categories) if categories else ' · all categories'}"
    )

    ui.metric_grid(
        [
            {
                "label": "Devices assessed",
                "value": format_number(assessed_count),
                "icon": "scan",
                "tone": "green",
                "note": "all statuses in range",
            },
            {
                "label": "Repaired",
                "value": format_number(repaired),
                "icon": "fact_check",
                "tone": "teal",
                "note": "completed repair pathway",
            },
            {
                "label": "Reused",
                "value": format_number(reused),
                "icon": "refresh",
                "tone": "blue",
                "note": "refurbished & resold",
            },
            {
                "label": "Recycled",
                "value": format_number(recycled),
                "icon": "recycle",
                "tone": "amber",
                "note": "incl. harvested & hazardous",
            },
            {
                "label": "E-waste diverted (est.)",
                "value": f"{format_number(diverted_kg)} kg",
                "icon": "cloud",
                "tone": "purple",
                "note": f"{format_number(co2_kg)} kg CO₂e avoided (est.)",
            },
        ]
    )

    if stats is not None:
        trend = pd.DataFrame(stats.get("monthly") or [])
    else:
        month_df = _month_slice(date_range)
        share = 1.0
        if categories:
            share = sum(
                float(row["share"])
                for _, row in d.CATEGORY_BREAKDOWN.iterrows()
                if row["category"] in categories
            ) / 100
            if share <= 0:
                share = 1.0
        trend = month_df.copy()
        trend["waste_kg"] = trend["waste_kg"] * share
        trend["co2_kg"] = trend["co2_kg"] * share

    chart_left, chart_right = st.columns([1.65, 1], gap="medium")
    with chart_left:
        with st.container(border=True):
            ui.section_header(
                "E-waste diverted",
                "Monthly estimates for the selected filters",
                kicker="Trend (estimate)",
            )
            if trend.empty:
                ui.empty_state(
                    "No completed recoveries in this range",
                    "Complete a recovery or choose a wider date range.",
                    icon_name="chart",
                )
            else:
                st.plotly_chart(
                    area_chart(trend, "month", "waste_kg"),
                    width="stretch",
                    theme=None,
                    config={"displayModeBar": False, "responsive": True},
                )
    with chart_right:
        with st.container(border=True):
            ui.section_header(
                "Category mix",
                "Devices in the selected range",
                kicker="Breakdown",
            )
            if stats is not None:
                category_rows = stats.get("category_breakdown") or []
                mix_labels = [row["category"] for row in category_rows]
                mix_values = [row["devices"] for row in category_rows]
                mix_total = sum(mix_values)
            else:
                mix = d.CATEGORY_BREAKDOWN
                if categories:
                    mix = mix[mix["category"].isin(categories)]
                mix_labels = mix["category"].tolist()
                mix_values = mix["share"].tolist()
                mix_total = int(mix["share"].sum())
            if not mix_labels:
                ui.empty_state("No category data", "Choose a different category filter.", icon_name="chart")
            else:
                st.plotly_chart(
                    donut_chart(
                        mix_labels,
                        mix_values,
                        "devices",
                        format_number(mix_total),
                        colors=["#22A06B", "#2FBFA3", "#8FD3B0", "#6FA8DC", "#E0B45C", "#4A6156"],
                    ),
                    width="stretch",
                    theme=None,
                    config={"displayModeBar": False, "responsive": True},
                )

    pathway_counts: dict[str, int] = {}
    if stats is not None:
        pathway_counts = {
            pathway: int(values.get("devices", 0))
            for pathway, values in stats.get("pathway_breakdown", {}).items()
            if values.get("devices")
        }
    else:
        for item in completed:
            pathway = item.get("pathway", "Recycle")
            pathway_counts[pathway] = pathway_counts.get(pathway, 0) + 1

    pathway_col, co2_col, goal_col = st.columns([1.2, 1, 1], gap="medium")
    with pathway_col:
        with st.container(border=True):
            ui.section_header(
                "Pathway mix",
                "How completed devices were routed",
                kicker="Circular flow",
            )
            if not pathway_counts:
                ui.empty_state(
                    "No completed recoveries in this filter",
                    "Change the date range or category to see pathway data.",
                    icon_name="recycle",
                )
            else:
                st.plotly_chart(
                    hbar_chart(
                        list(pathway_counts.keys()),
                        list(pathway_counts.values()),
                        height=260,
                        suffix="",
                    ),
                    width="stretch",
                    theme=None,
                    config={"displayModeBar": False, "responsive": True},
                )
    with co2_col:
        with st.container(border=True):
            ui.section_header(
                "Environmental statistics",
                "Estimated carbon avoided in range",
                kicker="Climate",
            )
            if trend.empty:
                ui.empty_state(
                    "No carbon data in this range",
                    "Complete a recovery or choose a wider date range.",
                    icon_name="cloud",
                )
            else:
                st.plotly_chart(
                    area_chart(
                        trend,
                        "month",
                        "co2_kg",
                        height=260,
                        color="#6FA8DC",
                        fillcolor="rgba(111,168,220,0.12)",
                    ),
                    width="stretch",
                    theme=None,
                    config={"displayModeBar": False, "responsive": True},
                )
            ui.kv_list(
                [
                    {"label": "CO₂e avoided (est.)", "value": f"{format_number(co2_kg)} kg"},
                    {"label": "Recyclable mass (est.)", "value": f"{format_number(diverted_kg)} kg"},
                ]
            )
    with goal_col:
        with st.container(border=True):
            ui.section_header("Monthly goal", "Keep the momentum going", kicker="Target")
            goal_target = float(d.MONTHLY_GOAL["target"])
            goal_current = (
                round(float(trend.iloc[-1]["waste_kg"]), 1) if not trend.empty else diverted_kg
            )
            ui.progress_bar(
                "Monthly e-waste diverted",
                goal_current,
                goal_target,
                d.MONTHLY_GOAL["unit"],
            )
            ui.goal_meta(
                [
                    {"label": "Remaining", "value": f"{max(goal_target - goal_current, 0):g} kg"},
                    {"label": "Devices", "value": format_number(assessed_count)},
                    {"label": "Streak", "value": f"{user['streak_days']} days"},
                    {"label": "Tier", "value": user["tier"]},
                ]
            )

    activity_col, reco_col = st.columns([1.5, 1], gap="medium")
    with activity_col:
        with st.container(border=True):
            ui.section_header("Recent activity", "Your latest circular actions", kicker="Feed")
            recent = stats.get("recent_activity") if stats else filtered[:6]
            if not recent:
                ui.empty_state(
                    "No activity for these filters",
                    "Try a wider date range or clear the category filter.",
                    icon_name="history",
                )
            else:
                items = []
                for entry in recent[:6]:
                    points = entry.get("points", 0)
                    items.append(
                        {
                            "title": f"{entry.get('pathway', 'Recycle')} · {entry['device']}",
                            "detail": f"{entry['detail']} · {entry['partner']}",
                            "time": entry["date"],
                            "points": f"+{format_number(points)}" if points else "",
                            "icon": entry.get("icon", "cpu"),
                            "tone": entry.get("tone", "green"),
                        }
                    )
                ui.activity_list(items)
    with reco_col:
        with st.container(border=True):
            ui.section_header(
                "Recommendations",
                "Suggested next steps for you",
                kicker="Next actions",
            )
            assessment = flow.get_assessment()
            if assessment:
                recommendation = assessment.get("recommendation") or build_recommendation(assessment)
                ui.insight_list(
                    [
                        {
                            "title": f"Continue with {recommendation['pathway']}",
                            "body": recommendation["explanation"],
                            "icon": recommendation["pathway_meta"]["icon"],
                            "tone": recommendation["pathway_meta"]["tone"],
                        },
                        {
                            "title": "Estimated impact",
                            "body": (
                                f"{recommendation['e_waste_kg']} kg diverted and {recommendation['co2_kg']} kg "
                                "CO₂e avoided (estimates)."
                            ),
                            "icon": "cloud",
                            "tone": "blue",
                        },
                        {
                            "title": "Find a demo partner",
                            "body": "Browse fictional repair shops and recycling centres near you.",
                            "icon": "pin",
                            "tone": "amber",
                        },
                    ]
                )
                if st.button("Open recommendation", type="primary", width="stretch"):
                    st.switch_page("views/recommendations.py")
            else:
                ui.insight_list(
                    [
                        {
                            "title": "Assess a device",
                            "body": "Identify a device and answer the condition form to unlock a pathway.",
                            "icon": "scan",
                            "tone": "green",
                        },
                        {
                            "title": "Clear the small stuff",
                            "body": "Bundle old chargers and cables for a quick recycling drop-off.",
                            "icon": "zap",
                            "tone": "amber",
                        },
                        {
                            "title": "Check partner capacity",
                            "body": "BlueGreen Recyclers is at 81% capacity; Whitefield is at 63%.",
                            "icon": "pin",
                            "tone": "blue",
                        },
                    ]
                )
                if st.button("Start an assessment", type="primary", width="stretch"):
                    st.switch_page("views/identify.py")
            if st.button("Find nearby centres", icon=":material/location_on:", width="stretch"):
                st.switch_page("views/map_view.py")

    st.html('<div style="height:6px"></div>')
    ui.banner(
        "Your next scan takes about 30 seconds",
        "Upload a photo or enter device details to get a recyclability score, pathway recommendation and nearby demo partners. Metrics are computed from your account records.",
        tone="green",
        icon_name="scan",
    )


render()
