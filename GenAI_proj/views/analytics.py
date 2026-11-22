from __future__ import annotations

import pandas as pd
import streamlit as st

from components import ui
from components.charts import (
    PLOTLY_CONFIG,
    area_chart,
    donut_chart,
    gauge_chart,
    hbar_chart,
    stacked_bar,
)
from data import mock_data as d
from utils import api_client, flow
from utils.helpers import format_number

PERIOD_RANGES = {
    "Last 90 days": "90d",
    "This year": "year",
    "All time": "all",
}


def _change(current: float, previous: float) -> str:
    if previous == 0:
        return "0.0%"
    return f"{(current - previous) / previous * 100:+.1f}%"


def render() -> None:
    history = flow.get_history()
    completed_history = [item for item in history if item["status"] == "Completed"]

    ui.page_header(
        "Environmental impact",
        "See your circular impact in numbers",
        "Explore diversion, carbon savings, material recovery, pathway mix and device categories. Numbers are computed from your saved recovery records.",
    )

    period_col, download_col = st.columns([2.2, 1], gap="medium")
    with period_col:
        period = st.segmented_control(
            "Reporting period",
            list(PERIOD_RANGES),
            default="This year",
            label_visibility="collapsed",
        )
    try:
        impact = api_client.impact_stats(PERIOD_RANGES.get(period, "year"))
    except api_client.ApiError:
        impact = None

    if impact is not None:
        filtered = pd.DataFrame(impact.get("monthly") or [])
        totals = impact["totals"]
        total_waste = int(totals["weight_kg"])
        total_co2 = int(totals["co2_kg"])
        total_devices = totals["devices_recovered"]
        pathway_totals = impact["pathway_breakdown"]
        equivalents = impact["equivalents"]
        materials = pd.DataFrame(impact.get("materials") or [])
    else:
        if period == "Last 90 days":
            filtered = d.MONTHLY_IMPACT.tail(3)
        elif period == "This year":
            filtered = d.MONTHLY_IMPACT.tail(11)
        else:
            filtered = d.MONTHLY_IMPACT
        total_waste = int(filtered["waste_kg"].sum())
        total_co2 = int(filtered["co2_kg"].sum())
        total_devices = int(filtered["devices"].sum())
        pathway_totals = flow.pathway_totals(completed_history)
        equivalents = d.IMPACT_EQUIVALENTS
        materials = d.MATERIAL_RECOVERY

    avg_waste = total_waste / len(filtered) if len(filtered) else 0
    if len(filtered):
        last = filtered.iloc[-1]
        previous = filtered.iloc[-2] if len(filtered) > 1 else last
    else:
        last = previous = {"waste_kg": 0, "co2_kg": 0, "devices": 0}

    if filtered.empty:
        export = pd.DataFrame(columns=["month", "waste_kg", "devices", "co2_kg", "cumulative_co2_kg"])
    else:
        export = filtered.copy()
        export["cumulative_co2_kg"] = export["co2_kg"].cumsum()
    with download_col:
        st.download_button(
            "Download report",
            data=export.to_csv(index=False).encode("utf-8"),
            file_name="reloop_impact_report.csv",
            mime="text/csv",
            icon=":material/download:",
            width="stretch",
        )

    ui.metric_grid(
        [
            {
                "label": "Waste diverted (est.)",
                "value": f"{format_number(total_waste)} kg",
                "delta": _change(last["waste_kg"], previous["waste_kg"]),
                "direction": "up",
                "icon": "recycle",
                "tone": "green",
                "note": f"across {len(filtered)} months",
            },
            {
                "label": "CO₂e avoided (est.)",
                "value": f"{format_number(total_co2)} kg",
                "delta": _change(last["co2_kg"], previous["co2_kg"]),
                "direction": "up",
                "icon": "cloud",
                "tone": "blue",
                "note": "scope 3 avoided emissions",
            },
            {
                "label": "Devices recovered (est.)",
                "value": format_number(total_devices),
                "delta": _change(last["devices"], previous["devices"]),
                "direction": "up",
                "icon": "cpu",
                "tone": "amber",
                "note": "mock partner records",
            },
            {
                "label": "Avg. monthly diversion (est.)",
                "value": f"{format_number(round(avg_waste))} kg",
                "delta": _change(last["waste_kg"], avg_waste),
                "direction": "up",
                "icon": "chart",
                "tone": "purple",
                "note": "latest month vs. period average",
            },
        ]
    )

    ui.section_header(
        "What your impact equals",
        "A human-scale view of the same recovery",
        kicker="Equivalences",
    )
    ui.metric_grid(equivalents)
    st.caption("Equivalence values are illustrative estimates calculated from recovered totals.")

    co2_col, gauge_col = st.columns([1.65, 1], gap="medium")
    with co2_col:
        with st.container(border=True):
            ui.section_header(
                "Cumulative CO₂ avoided",
                "Every kilogram diverted keeps carbon in the ground",
                kicker="Carbon",
            )
            if filtered.empty:
                ui.empty_state(
                    "No monthly data in this period",
                    "Complete a recovery or choose a wider reporting period.",
                    icon_name="chart",
                )
            else:
                trend = filtered.copy()
                trend["cumulative_co2"] = trend["co2_kg"].cumsum()
                st.plotly_chart(
                    area_chart(
                        trend,
                        "month",
                        "cumulative_co2",
                        color="#6FA8DC",
                        fillcolor="rgba(111,168,220,0.12)",
                    ),
                    width="stretch",
                    theme=None,
                    config=PLOTLY_CONFIG,
                )
    completed_count = sum(int(values.get("devices", 0)) for values in pathway_totals.values())
    reused_count = int(pathway_totals.get("Refurbish & Resell", {}).get("devices", 0))
    repaired_count = int(pathway_totals.get("Repair", {}).get("devices", 0))
    material_count = int(pathway_totals.get("Recycle", {}).get("devices", 0)) + int(
        pathway_totals.get("Harvest Components", {}).get("devices", 0)
    )
    safe_count = completed_count - int(pathway_totals.get("Hazardous Handling", {}).get("devices", 0))
    circularity = round(
        ((repaired_count + reused_count + material_count * 0.75) / completed_count * 100)
        if completed_count
        else 0
    )
    with gauge_col:
        with st.container(border=True):
            ui.section_header(
                "Circularity score",
                "Weighted reuse, recovery and safe disposal",
                kicker="System health",
            )
            st.plotly_chart(
                gauge_chart(circularity, height=215, title="Your circularity"),
                width="stretch",
                theme=None,
                config=PLOTLY_CONFIG,
            )
            ui.kv_list(
                [
                    {
                        "label": "Reuse rate",
                        "value": f"{round(reused_count / completed_count * 100) if completed_count else 0}%",
                    },
                    {
                        "label": "Material recovery",
                        "value": f"{round(material_count / completed_count * 100) if completed_count else 0}%",
                    },
                    {
                        "label": "Landfill avoided",
                        "value": f"{round(safe_count / completed_count * 100) if completed_count else 0}%",
                    },
                ]
            )

    ui.section_header(
        "Recovery pathway breakdown",
        "Repaired, reused, harvested, recycled and hazardous handling — estimated from your history",
        kicker="Pathways",
    )
    repaired = pathway_totals.get("Repair", {})
    reused = pathway_totals.get("Refurbish & Resell", {})
    recycled = pathway_totals.get("Recycle", {})
    harvested = pathway_totals.get("Harvest Components", {})
    hazardous = pathway_totals.get("Hazardous Handling", {})
    ui.metric_grid(
        [
            {
                "label": "Repaired",
                "value": format_number(repaired.get("devices", 0)),
                "icon": "fact_check",
                "tone": "green",
                "note": f"{repaired.get('weight_kg', 0)} kg diverted (est.)",
            },
            {
                "label": "Reused / resold",
                "value": format_number(reused.get("devices", 0)),
                "icon": "refresh",
                "tone": "blue",
                "note": f"{reused.get('weight_kg', 0)} kg diverted (est.)",
            },
            {
                "label": "Recycled",
                "value": format_number(recycled.get("devices", 0) + harvested.get("devices", 0)),
                "icon": "recycle",
                "tone": "teal",
                "note": "recycle + harvest components",
            },
            {
                "label": "Hazardous handled",
                "value": format_number(hazardous.get("devices", 0)),
                "icon": "battery",
                "tone": "coral",
                "note": f"{hazardous.get('weight_kg', 0)} kg safely handled",
            },
        ]
    )

    pathway_col, progress_col = st.columns([1, 1.25], gap="medium")
    with pathway_col:
        with st.container(border=True):
            ui.section_header(
                "Pathway mix",
                "Completed devices by recovery route",
                kicker="Distribution",
            )
            labels = [pathway for pathway, values in pathway_totals.items() if values["devices"]]
            values = [pathway_totals[pathway]["devices"] for pathway in labels]
            if labels:
                st.plotly_chart(
                    donut_chart(
                        labels,
                        values,
                        "devices",
                        format_number(sum(values)),
                        colors=["#22A06B", "#6FA8DC", "#E0B45C", "#2FBFA3", "#E08A77"],
                    ),
                    width="stretch",
                    theme=None,
                    config=PLOTLY_CONFIG,
                )
            else:
                ui.empty_state(
                    "No completed pathway data",
                    "Complete an assessment and save a route to see pathway breakdown.",
                    icon_name="recycle",
                )
    with progress_col:
        with st.container(border=True):
            ui.section_header(
                "Weight diverted by pathway",
                "Progress against total estimated diversion",
                kicker="Progress",
            )
            total_weight = sum(values["weight_kg"] for values in pathway_totals.values()) or 1
            for pathway, values in pathway_totals.items():
                if values["weight_kg"]:
                    ui.progress_bar(
                        f"{pathway} · {values['devices']} device(s)",
                        values["weight_kg"],
                        total_weight,
                        "kg",
                    )
            st.caption("All weight values are mock estimates from the assessment and history records.")

    mix_col, material_col = st.columns([1.5, 1], gap="medium")
    with mix_col:
        with st.container(border=True):
            ui.section_header(
                "Device mix over time",
                "Monthly units by category across the demo network",
                kicker="Composition",
            )
            if filtered.empty:
                ui.empty_state(
                    "No composition data in this period",
                    "Choose a wider reporting period to see the monthly mix.",
                    icon_name="chart",
                )
            else:
                category_df = d.MONTHLY_BY_CATEGORY.tail(len(filtered))
                categories = [
                    "Smartphones",
                    "Laptops",
                    "Accessories",
                    "Home appliances",
                    "Tablets",
                    "Other",
                ]
                st.plotly_chart(
                    stacked_bar(category_df, "month", categories),
                    width="stretch",
                    theme=None,
                    config=PLOTLY_CONFIG,
                )
    with material_col:
        with st.container(border=True):
            ui.section_header(
                "Material recovery",
                "Mass recovered by material stream",
                kicker="Resources",
            )
            if materials.empty:
                ui.empty_state(
                    "No material data yet",
                    "Complete an assessment or recovery to populate material estimates.",
                    icon_name="recycle",
                )
            else:
                st.plotly_chart(
                    donut_chart(
                        materials["material"].tolist(),
                        materials["kg"].tolist(),
                        "kg recovered",
                        format_number(materials["kg"].sum()),
                    ),
                    width="stretch",
                    theme=None,
                    config=PLOTLY_CONFIG,
                )

    category_counts: dict[str, int] = {}
    for item in completed_history:
        category = item.get("category", "Other")
        category_counts[category] = category_counts.get(category, 0) + 1
    if category_counts:
        with st.container(border=True):
            ui.section_header(
                "Your category-wise impact",
                "Completed devices by category from your history",
                kicker="Categories",
            )
            st.plotly_chart(
                hbar_chart(
                    list(category_counts.keys()),
                    list(category_counts.values()),
                    height=280,
                    suffix="",
                ),
                width="stretch",
                theme=None,
                config=PLOTLY_CONFIG,
            )

    device_counts: dict[str, int] = {}
    for item in completed_history:
        device = item.get("device", "Other")
        device_counts[device] = device_counts.get(device, 0) + 1
    if not device_counts:
        device_labels = d.DEVICE_TYPE_VOLUME["device"].tolist()
        device_values = d.DEVICE_TYPE_VOLUME["units"].tolist()
    else:
        ordered = sorted(device_counts.items(), key=lambda item: item[1], reverse=True)[:6]
        device_labels = [item[0] for item in ordered]
        device_values = [item[1] for item in ordered]

    volume_col, insight_col = st.columns([1.05, 1.25], gap="medium")
    with volume_col:
        with st.container(border=True):
            ui.section_header(
                "Top device types",
                "Your most recovered device types",
                kicker="Volume",
            )
            st.plotly_chart(
                hbar_chart(
                    device_labels,
                    device_values,
                    suffix="",
                ),
                width="stretch",
                theme=None,
                config=PLOTLY_CONFIG,
            )
    with insight_col:
        with st.container(border=True):
            ui.section_header(
                "What the data says",
                "Signals worth acting on this month",
                kicker="Insights",
            )
            if completed_history:
                ui.insight_list(
                    [
                        {
                            "title": "Recovery is compounding",
                            "body": (
                                f"{format_number(completed_count)} completed recoveries have diverted "
                                f"{format_number(total_waste)} kg from landfill."
                            ),
                            "icon": "recycle",
                            "tone": "green",
                        },
                        {
                            "title": "Reuse outperforms recycling",
                            "body": (
                                f"Refurbish & Resell accounts for {round(reused_count / completed_count * 100) if completed_count else 0}% "
                                "of completed recoveries, preserving more embedded carbon."
                            ),
                            "icon": "refresh",
                            "tone": "blue",
                        },
                        {
                            "title": "Safety remains the gate",
                            "body": "Hazardous battery conditions are always routed to safe handling before any resale or repair.",
                            "icon": "shield",
                            "tone": "amber",
                        },
                    ]
                )
            else:
                ui.insight_list(d.INSIGHTS)

    ui.banner(
        "Build the report you need",
        "Use the download button above to export the monthly impact data as a CSV. Recovery records come from your account; impact assumptions remain estimates.",
        tone="blue",
        icon_name="info",
    )


render()
