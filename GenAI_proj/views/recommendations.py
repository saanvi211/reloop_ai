from __future__ import annotations

import streamlit as st

from components import ui
from data import mock_data as d
from utils import api_client, flow
from utils.helpers import format_currency, format_indian
from utils.recommendations_engine import build_recommendation, matching_centres

FLOW_STEPS = [
    {"title": "Identify", "body": "Add a photo or device details"},
    {"title": "Assess", "body": "Answer condition questions"},
    {"title": "Route", "body": "Follow the recommendation"},
]


def _recommendation_for(result: dict) -> dict:
    recommendation = result.get("recommendation")
    if result.get("id"):
        try:
            recommendation = api_client.get_recommendation(result["id"])
        except api_client.ApiError:
            pass
    return recommendation or build_recommendation(result)


def _centre_pool() -> list[dict]:
    try:
        return api_client.list_centres(limit=200)
    except api_client.ApiError:
        return list(d.COLLECTION_POINTS)


def _save_route(result: dict, partner: str, status: str, recommendation: dict, notes: str) -> bool:
    try:
        flow.add_history(
            result,
            partner,
            status=status,
            points=0,
            pathway=recommendation["pathway"],
            notes=notes,
        )
    except api_client.ApiError as exc:
        st.error(exc.message)
        return False
    return True


def _find_centres(result: dict, recommendation: dict) -> None:
    st.session_state["map_device_default"] = result.get("device", "")
    st.session_state["map_item_default"] = recommendation.get("accepted_type", "All items")
    st.session_state["map_pathway_default"] = recommendation.get("pathway", "")
    st.switch_page("views/map_view.py")


def render() -> None:
    ui.page_header(
        "Recommendations · Step 3 of 3",
        "The best next step for this device",
        "Five possible pathways ranked with safety rules, repair feasibility, estimated value and estimated environmental impact.",
    )

    result = flow.get_assessment()
    ui.flow_rail(FLOW_STEPS, active=3)

    if not result:
        ui.empty_state(
            "No recommendation yet",
            "Complete identification and the assessment form first. ReLoop will then rank five recovery pathways.",
            icon_name="recommend",
        )
        first, second, _ = st.columns([1, 1, 2], gap="small")
        with first:
            if st.button(
                "Identify a device",
                type="primary",
                icon=":material/document_scanner:",
                width="stretch",
            ):
                st.switch_page("views/identify.py")
        with second:
            if st.button("View assessment", icon=":material/fact_check:", width="stretch"):
                st.switch_page("views/assessment.py")
        return

    recommendation = _recommendation_for(result)
    flow.save_recommendation(recommendation)
    centres = matching_centres(result, recommendation, points=_centre_pool(), limit=4)
    nearest = centres[0] if centres else None

    if recommendation["safety_override"]:
        ui.banner(
            "Safety override: Hazardous Handling only",
            f"The battery is {result.get('battery_condition', 'unsafe').lower()}. Repair, resale and component harvesting are blocked.",
            tone="amber",
            icon_name="battery",
        )
    else:
        ui.banner(
            f"Recommended pathway: {recommendation['pathway']}",
            f"{recommendation['pathway_meta']['description']} All values below are estimates.",
            tone="green",
            icon_name=recommendation["pathway_meta"]["icon"],
        )

    ui.metric_grid(
        [
            {
                "label": "Recommended pathway",
                "value": recommendation["pathway"],
                "delta": "Safety override" if recommendation["safety_override"] else "Best match",
                "direction": "flat",
                "icon": recommendation["pathway_meta"]["icon"],
                "tone": recommendation["pathway_meta"]["tone"],
                "note": "server decision logic",
            },
            {
                "label": "Repair feasibility",
                "value": recommendation["repair_feasibility"],
                "icon": "fact_check",
                "tone": "green" if recommendation["repair_feasibility"].startswith("High") else "amber",
                "note": "diagnostic estimate only",
            },
            {
                "label": "Residual value (est.)",
                "value": format_currency(recommendation["residual_value"]),
                "icon": "gift",
                "tone": "purple",
                "note": "illustrative, not a quote",
            },
            {
                "label": "E-waste diverted (est.)",
                "value": f"{recommendation['e_waste_kg']} kg",
                "icon": "recycle",
                "tone": "blue",
                "note": f"{recommendation['co2_kg']} kg CO₂e avoided (est.)",
            },
        ]
    )

    main_col, ranking_col = st.columns([1.15, 1], gap="medium")
    with main_col:
        with st.container(border=True):
            ui.section_header(
                f"Recommended: {recommendation['pathway']}",
                "Why this pathway wins for this assessment",
                kicker="Decision",
            )
            ui.insight_list(
                [
                    {
                        "title": recommendation["pathway_meta"]["title"],
                        "body": recommendation["explanation"],
                        "icon": recommendation["pathway_meta"]["icon"],
                        "tone": recommendation["pathway_meta"]["tone"],
                    },
                    {
                        "title": "Safety rule",
                        "body": (
                            "A hazardous battery blocks DIY repair, resale and component harvesting."
                            if recommendation["safety_override"]
                            else "No hazardous battery signals were reported."
                        ),
                        "icon": "shield",
                        "tone": "amber" if recommendation["safety_override"] else "green",
                    },
                    {
                        "title": "Estimated impact",
                        "body": (
                            f"About {recommendation['e_waste_kg']} kg diverted and {recommendation['co2_kg']} kg CO₂e "
                            "avoided if the device is recovered through this route. These are estimates."
                        ),
                        "icon": "cloud",
                        "tone": "blue",
                    },
                ]
            )
            ui.progress_bar(
                f"{recommendation['pathway']} confidence score",
                recommendation["ranked"][0]["score"],
                100,
            )
            if recommendation["safety_override"]:
                ui.warning_list(recommendation["warnings"])
            else:
                ui.guidance_list(recommendation["warnings"][:3])

        with st.container(border=True):
            ui.section_header(
                "Preparation & safety",
                "Complete these steps before handing the device over",
                kicker="Safety",
            )
            ui.warning_list(recommendation["warnings"])
            ui.guidance_list(result.get("guidance", []))

    with ranking_col:
        with st.container(border=True):
            ui.section_header(
                "Ranked alternatives",
                "All five pathways, scored by the server decision logic",
                kicker="Comparison",
            )
            ui.pathway_rank_rows(recommendation["ranked"])
            st.caption(
                "Scores are relative estimates from device type, age, working status, damage and battery condition."
            )

    route_col, impact_col = st.columns([1.3, 1], gap="medium")
    with route_col:
        with st.container(border=True):
            ui.section_header(
                "Suggested partner",
                "Closest demo partner that fits this pathway",
                kicker="Nearby centres",
            )
            if nearest:
                ui.collection_card(nearest)
            else:
                ui.empty_state(
                    "No matching centre found",
                    "Open the nearby centres page to browse all fictional demo partners.",
                    icon_name="map",
                )
            find_col, browse_col = st.columns(2, gap="small")
            with find_col:
                if st.button(
                    "Find nearby centres",
                    type="primary",
                    icon=":material/location_on:",
                    width="stretch",
                ):
                    _find_centres(result, recommendation)
            with browse_col:
                if st.button("Browse all centres", icon=":material/map:", width="stretch"):
                    _find_centres(result, recommendation)
    with impact_col:
        with st.container(border=True):
            ui.section_header(
                "Estimated impact",
                "What this route could unlock",
                kicker="Impact (estimates)",
            )
            ui.kv_list(
                [
                    {"label": "Pathway", "value": recommendation["pathway"]},
                    {"label": "E-waste diverted (est.)", "value": f"{recommendation['e_waste_kg']} kg"},
                    {"label": "CO₂e avoided (est.)", "value": f"{recommendation['co2_kg']} kg"},
                    {"label": "Residual value (est.)", "value": format_currency(recommendation["residual_value"])},
                    {"label": "Points on drop-off (est.)", "value": f"+{format_indian(max(40, result['score'] * 2))} pts"},
                ]
            )
            ui.progress_bar("Recyclability score", result["score"], 100)

    if nearest:
        ui.banner(
            "Route summary",
            f"{result['device']} → {recommendation['pathway']} → {nearest['name']} in {nearest['area']} "
            f"({nearest['distance_km']} km away).",
            tone="blue",
            icon_name="pin",
        )

    if len(centres) > 1:
        ui.section_header(
            "Other matching demo partners",
            "Backup routes if the first one is busy",
            kicker="Alternatives",
        )
        alt_cols = st.columns(min(3, len(centres) - 1), gap="medium")
        for column, point in zip(alt_cols, centres[1:]):
            with column:
                ui.collection_card(point)

    action_col, pickup_col, reset_col = st.columns([1.2, 1, 1], gap="small")
    with action_col:
        if st.button("Save route to history", icon=":material/bookmark_add:", width="stretch"):
            partner = nearest["name"] if nearest else "ReLoop partner network"
            if _save_route(
                result,
                partner,
                "Scheduled",
                recommendation,
                f"Recommended pathway: {recommendation['pathway']} (server decision).",
            ):
                st.toast("Route saved to history.")
                st.rerun()
    with pickup_col:
        if st.session_state.get("pickup_booked"):
            st.success("Home pickup requested.")
        elif st.button(
            "Book home pickup",
            type="primary",
            icon=":material/local_shipping:",
            width="stretch",
        ):
            if _save_route(
                result,
                "Home pickup · Ravi K.",
                "Scheduled",
                recommendation,
                "Home pickup requested from recommendations.",
            ):
                st.session_state["pickup_booked"] = True
                st.toast("Home pickup requested. This is a demo action.")
                st.rerun()
    with reset_col:
        if st.button("Start a new assessment", icon=":material/refresh:", width="stretch"):
            flow.reset_flow()
            st.session_state.pop("pickup_booked", None)
            st.session_state.pop("assessment_editing", None)
            st.session_state.pop("assessment_step", None)
            st.switch_page("views/identify.py")

    ui.banner(
        "Every value here is an estimate",
        "Pathways, residual values, e-waste diverted and CO₂e avoided are estimates. Recommendations and saved routes are persisted by the API; partner data is fictional and unverified.",
        tone="amber",
        icon_name="info",
    )


render()
