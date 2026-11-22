from __future__ import annotations

import json

import streamlit as st

from components import ui
from components.charts import PLOTLY_CONFIG, gauge_chart
from data import mock_data as d
from utils import api_client, flow
from utils.helpers import (
    derive_condition,
    device_from_category,
    estimate_identification,
    format_currency,
)
from utils.recommendations_engine import build_recommendation, matching_centres


def _recommendation_for(result: dict) -> dict:
    stored = result.get("recommendation")
    if stored and stored.get("pathway"):
        return stored
    return build_recommendation(result)

FLOW_STEPS = [
    {"title": "Identify", "body": "Add a photo or device details"},
    {"title": "Assess", "body": "Answer condition questions"},
    {"title": "Route", "body": "Follow the recommendation"},
]

FORM_STEPS = ["Device basics", "Condition & safety", "Review & generate"]

WIDGET_KEYS = [
    "assess_age",
    "assess_brand",
    "assess_model",
    "assess_working",
    "assess_damage",
    "assess_battery",
    "assess_description",
]


def _reset_widgets(identification: dict, result: dict | None) -> None:
    answers = flow.get_answers()
    signature = "|".join(
        [
            str(identification.get("device", "")),
            str(identification.get("source", "")),
            str(identification.get("confidence", "")),
            str(result.get("condition", "") if result else ""),
        ]
    )
    if st.session_state.get("assessment_signature") == signature:
        return
    st.session_state["assessment_signature"] = signature
    st.session_state["assess_age"] = int(answers.get("age_years", result.get("age_years", 3) if result else 3))
    st.session_state["assess_brand"] = answers.get("brand", result.get("brand", "") if result else "")
    st.session_state["assess_model"] = answers.get("model", result.get("model", "") if result else "")
    st.session_state["assess_working"] = answers.get(
        "working", ("Yes" if result.get("working") else "No") if result else "Select an option"
    )
    st.session_state["assess_damage"] = answers.get(
        "physical_damage", result.get("physical_damage", "Select an option") if result else "Select an option"
    )
    st.session_state["assess_battery"] = answers.get(
        "battery_condition", result.get("battery_condition", "Select an option") if result else "Select an option"
    )
    st.session_state["assess_description"] = answers.get(
        "description", result.get("description", "") if result else ""
    )


def _current_answers() -> dict:
    saved = flow.get_answers()
    answers = {
        "age_years": int(saved.get("age_years", 3)),
        "brand": saved.get("brand", "") or "Not specified",
        "model": saved.get("model", "") or "Not specified",
        "working": saved.get("working", "Select an option"),
        "physical_damage": saved.get("physical_damage", "Select an option"),
        "battery_condition": saved.get("battery_condition", "Select an option"),
        "description": saved.get("description", ""),
    }
    step = int(st.session_state.get("assessment_step", 1))
    if step == 1:
        answers["age_years"] = int(st.session_state.get("assess_age", answers["age_years"]))
        answers["brand"] = st.session_state.get("assess_brand", "").strip() or "Not specified"
        answers["model"] = st.session_state.get("assess_model", "").strip() or "Not specified"
    elif step == 2:
        answers["working"] = st.session_state.get("assess_working", answers["working"])
        answers["physical_damage"] = st.session_state.get(
            "assess_damage", answers["physical_damage"]
        )
        answers["battery_condition"] = st.session_state.get(
            "assess_battery", answers["battery_condition"]
        )
    else:
        answers["description"] = st.session_state.get(
            "assess_description", answers["description"]
        ).strip()
    return answers


def _condition_errors(answers: dict) -> list[str]:
    errors = []
    if answers["working"] not in {"Yes", "No"}:
        errors.append("Select whether the device powers on.")
    if answers["physical_damage"] not in d.DAMAGE_LEVELS:
        errors.append("Select the physical damage level.")
    if answers["battery_condition"] not in d.BATTERY_CONDITIONS:
        errors.append("Select the battery condition.")
    return errors


def _store_answers() -> dict:
    answers = _current_answers()
    flow.save_answers(answers)
    return answers


def _local_assessment(identification: dict, answers: dict) -> dict:
    device = device_from_category(identification["device"])
    working = answers["working"] == "Yes"
    condition = derive_condition(answers["age_years"], working, answers["physical_damage"])
    photo = flow.get_photo()
    result = estimate_identification(
        device,
        condition,
        answers["age_years"],
        working,
        seed_text=f"{answers['brand']}|{answers['model']}|{photo['name'] if photo else ''}",
        battery_condition=answers["battery_condition"],
        physical_damage=answers["physical_damage"],
        description=answers["description"],
    )
    result["brand"] = answers["brand"]
    result["model"] = answers["model"]
    result["photo_name"] = photo["name"] if photo else ""
    result["identified_category"] = identification["device"]
    result["identification_confidence"] = identification["confidence"]
    result["pathway"] = build_recommendation(result)["pathway"]
    return result


def _generate(identification: dict, existing: dict | None) -> None:
    answers = _store_answers()
    errors = _condition_errors(answers)
    if errors:
        for error in errors:
            st.error(error)
        return

    payload = {
        "identification_id": identification.get("id"),
        "device": identification.get("mapped_device") or device_from_category(identification["device"]),
        "age_years": answers["age_years"],
        "working": answers["working"] == "Yes",
        "physical_damage": answers["physical_damage"],
        "battery_condition": answers["battery_condition"],
        "brand": answers["brand"],
        "model": answers["model"],
        "description": answers["description"] or None,
        "identified_category": identification["device"],
    }
    if payload["identification_id"] is None:
        payload.pop("identification_id")
    if not payload["device"]:
        payload.pop("device")

    with st.spinner("Saving your assessment and building the recommendation…"):
        try:
            if existing and existing.get("id"):
                result = api_client.update_assessment(existing["id"], payload)
            else:
                result = api_client.create_assessment(payload)
        except api_client.ApiError as exc:
            if exc.status_code and not exc.offline:
                st.error(exc.message)
                return
            result = _local_assessment(identification, answers)
            st.session_state["assessment_notice"] = (
                "The backend is offline. This assessment is being kept in the browser "
                "and the safety rules are being enforced locally."
            )
    flow.save_assessment(result)
    st.session_state["assessment_editing"] = False
    st.session_state.pop("assessment_step", None)
    st.toast("Assessment summary ready.")
    st.rerun()


def _render_form(identification: dict) -> None:
    step = int(st.session_state.get("assessment_step", 1))
    step = max(1, min(3, step))
    st.session_state["assessment_step"] = step

    header_col, progress_col = st.columns([1.1, 1], gap="medium")
    with header_col:
        ui.section_header(
            f"Step {step} of 3 · {FORM_STEPS[step - 1]}",
            "Your answers are kept when you move between steps or pages.",
            kicker="Multi-step form",
        )
    with progress_col:
        st.progress((step - 1) / 3)
        st.caption(f"{int((step - 1) / 3 * 100)}% complete · {3 - step} step(s) remaining")

    with st.container(border=True):
        if step == 1:
            st.slider("Device age (years)", min_value=0, max_value=20, key="assess_age")
            first, second = st.columns(2, gap="medium")
            with first:
                st.text_input("Brand (optional)", placeholder="e.g. Samsung", key="assess_brand")
            with second:
                st.text_input("Model (optional)", placeholder="e.g. Galaxy S21", key="assess_model")
            mapped = device_from_category(identification["device"])
            st.caption(
                f"Identified as {identification['device']} ({int(identification['confidence'] * 100)}% mock confidence). "
                f"It will be assessed as a {mapped}."
            )

        elif step == 2:
            working_options = ["Select an option", "Yes", "No"]
            if st.session_state.get("assess_working") not in working_options:
                st.session_state["assess_working"] = "Select an option"
            st.selectbox(
                "Does the device power on?",
                working_options,
                key="assess_working",
                help="Required.",
            )
            damage_options = ["Select an option"] + d.DAMAGE_LEVELS
            if st.session_state.get("assess_damage") not in damage_options:
                st.session_state["assess_damage"] = "Select an option"
            st.selectbox(
                "Physical damage",
                damage_options,
                key="assess_damage",
                help="Required. Choose None if there is no visible damage.",
            )
            battery_options = ["Select an option"] + d.BATTERY_CONDITIONS
            if st.session_state.get("assess_battery") not in battery_options:
                st.session_state["assess_battery"] = "Select an option"
            st.selectbox(
                "Battery condition",
                battery_options,
                key="assess_battery",
                help="Required. Swollen, overheating or leaking batteries trigger a mandatory safety override.",
            )
            answers = _current_answers()
            if answers["battery_condition"] in d.HAZARDOUS_BATTERY_CONDITIONS:
                ui.banner(
                    "Safety override active",
                    f"{answers['battery_condition']} battery detected. Repair, resale and component harvesting will be blocked.",
                    tone="amber",
                    icon_name="battery",
                )

        else:
            answers = _store_answers()
            ui.section_header(
                "Review your answers",
                "Confirm everything before generating the summary",
                kicker="Summary",
            )
            ui.answer_grid(
                [
                    {"label": "Category", "value": identification["device"]},
                    {"label": "Age", "value": f"{answers['age_years']} years"},
                    {"label": "Brand", "value": answers["brand"]},
                    {"label": "Model", "value": answers["model"]},
                    {"label": "Powers on", "value": answers["working"]},
                    {"label": "Physical damage", "value": answers["physical_damage"]},
                    {"label": "Battery", "value": answers["battery_condition"]},
                    {"label": "Description", "value": answers["description"] or "Not provided"},
                ]
            )
            st.text_area(
                "Anything else we should know? (optional)",
                placeholder="e.g. cracked screen, missing charger, data already backed up",
                key="assess_description",
            )
            if answers["battery_condition"] in d.HAZARDOUS_BATTERY_CONDITIONS:
                ui.banner(
                    "Hazardous handling override",
                    "This device will only be routed to specialist hazardous handling. Do not attempt DIY repair.",
                    tone="amber",
                    icon_name="shield",
                )

        st.divider()
        left, middle, right = st.columns([1, 1, 1.2], gap="small")
        with left:
            if step > 1:
                if st.button("Back", icon=":material/arrow_back:", width="stretch"):
                    _store_answers()
                    st.session_state["assessment_step"] = step - 1
                    st.rerun()
        with middle:
            if step < 3:
                if st.button("Continue", type="primary", icon=":material/arrow_forward:", width="stretch"):
                    _store_answers()
                    if step == 2:
                        errors = _condition_errors(_current_answers())
                        if errors:
                            for error in errors:
                                st.error(error)
                        else:
                            st.session_state["assessment_step"] = step + 1
                            st.rerun()
                    else:
                        st.session_state["assessment_step"] = step + 1
                        st.rerun()
        with right:
            if step == 3:
                if st.button(
                    "Generate assessment summary",
                    type="primary",
                    icon=":material/auto_awesome:",
                    width="stretch",
                ):
                    _generate(identification, flow.get_assessment())

    ui.banner(
        "Why we ask these questions",
        "Age, working status, physical damage and battery condition drive the mock score and the safety override. The backend re-checks every safety rule before saving.",
        tone="blue",
        icon_name="info",
    )


def _render_summary(result: dict) -> None:
    recommendation = _recommendation_for(result)
    ui.banner(
        "Assessment complete",
        f"Estimated pathway: {recommendation['pathway']}. Review the summary, then continue to full recommendations.",
        tone="green",
        icon_name="check",
    )
    if recommendation["safety_override"]:
        ui.banner(
            "Safety override applied",
            f"The battery is marked {result.get('battery_condition', 'hazardous').lower()}. Only hazardous handling is allowed.",
            tone="amber",
            icon_name="battery",
        )

    ui.result_hero(result)

    top_materials = ", ".join(
        material
        for material, _ in sorted(result["materials"].items(), key=lambda item: item[1], reverse=True)[:3]
    )
    ui.metric_grid(
        [
            {
                "label": "Recyclability score",
                "value": f"{result['score']}/100",
                "delta": result["band"]["label"],
                "direction": "up",
                "icon": "target",
                "tone": "green",
                "note": "estimated from condition and age",
            },
            {
                "label": "Recoverable mass",
                "value": f"{result['recyclable_kg']} kg",
                "delta": f"{result['recyclable_pct']}%",
                "direction": "up",
                "icon": "recycle",
                "tone": "blue",
                "note": f"of {result['weight_kg']} kg total weight",
            },
            {
                "label": "CO₂e avoided (est.)",
                "value": f"{result['co2_kg']} kg",
                "delta": "estimate",
                "direction": "flat",
                "icon": "cloud",
                "tone": "amber",
                "note": "if recovered through a partner",
            },
            {
                "label": "Residual value (est.)",
                "value": format_currency(recommendation["residual_value"]),
                "delta": recommendation["pathway"],
                "direction": "flat",
                "icon": "gift",
                "tone": "purple",
                "note": "illustrative, not a quote",
            },
        ]
    )

    ui.section_header("Your answers", "Stored with your assessment", kicker="Form summary")
    ui.answer_grid(
        [
            {"label": "Identified category", "value": result.get("identified_category", result["device"])},
            {"label": "Assessed device", "value": result["device"]},
            {"label": "Age", "value": f"{result['age_years']} years"},
            {"label": "Brand", "value": result["brand"]},
            {"label": "Model", "value": result["model"]},
            {"label": "Powers on", "value": "Yes" if result["working"] else "No"},
            {"label": "Physical damage", "value": result["physical_damage"]},
            {"label": "Battery", "value": result["battery_condition"]},
            {"label": "Description", "value": result.get("description") or "Not provided"},
        ]
    )

    score_col, material_col, meaning_col = st.columns([0.9, 1.05, 1.05], gap="medium")
    with score_col:
        with st.container(border=True):
            ui.section_header("Recyclability", "Higher is easier to recover", kicker="Score")
            st.plotly_chart(
                gauge_chart(result["score"], height=225, title="Material recovery potential"),
                width="stretch",
                theme=None,
                config=PLOTLY_CONFIG,
            )
            ui.kv_list(
                [
                    {"label": "Condition", "value": result["condition"]},
                    {"label": "Safety override", "value": "Yes" if recommendation["safety_override"] else "No"},
                    {"label": "Repair feasibility", "value": recommendation["repair_feasibility"]},
                ]
            )
    with material_col:
        with st.container(border=True):
            ui.section_header(
                "Recoverable materials",
                f"{result['recyclable_kg']} kg of {result['weight_kg']} kg can be recovered",
                kicker="Composition",
            )
            ui.material_rows(result["materials"])
    with meaning_col:
        with st.container(border=True):
            ui.section_header("What this means", "What to know before routing", kicker="Summary")
            ui.insight_list(
                [
                    {
                        "title": f"{recommendation['pathway']} is recommended",
                        "body": recommendation["explanation"],
                        "icon": recommendation["pathway_meta"]["icon"],
                        "tone": recommendation["pathway_meta"]["tone"],
                    },
                    {
                        "title": f"{top_materials} lead the mix",
                        "body": "These streams are the most valuable to recover and keep in circulation.",
                        "icon": "recycle",
                        "tone": "blue",
                    },
                    {
                        "title": "Preparation matters",
                        "body": "Safety steps and handling warnings appear on the recommendations page.",
                        "icon": "shield",
                        "tone": "amber",
                    },
                ]
            )

    action_col, download_col, route_col = st.columns([1.15, 1, 1], gap="small")
    with action_col:
        if st.button("Edit answers", icon=":material/edit:", width="stretch"):
            st.session_state["assessment_editing"] = True
            st.session_state["assessment_step"] = 1
            st.rerun()
    with download_col:
        st.download_button(
            "Download assessment",
            data=json.dumps(result, indent=2, default=str).encode("utf-8"),
            file_name="reloop_assessment.json",
            mime="application/json",
            icon=":material/download:",
            width="stretch",
        )
    with route_col:
        if st.button(
            "View recommendations",
            type="primary",
            icon=":material/recommend:",
            width="stretch",
        ):
            st.switch_page("views/recommendations.py")

    save_col, _, _ = st.columns([1.2, 1, 1], gap="small")
    with save_col:
        if flow.is_assessment_saved():
            st.success("Assessment saved to history.")
        elif st.button("Save assessment to history", icon=":material/bookmark_add:", width="stretch"):
            try:
                centres = api_client.list_centres(limit=20, accepted=recommendation.get("accepted_type"))
            except api_client.ApiError:
                centres = matching_centres(result, recommendation, limit=1)
            partner = centres[0]["name"] if centres else "ReLoop partner network"
            try:
                flow.add_history(
                    result,
                    partner,
                    status="Processing",
                    points=0,
                    pathway=recommendation["pathway"],
                    notes=result.get("description") or "Assessment saved from the multi-step form.",
                )
            except api_client.ApiError as exc:
                st.error(exc.message)
            else:
                flow.mark_assessment_saved()
                st.toast("Assessment saved to history.")
                st.rerun()

    ui.banner(
        "Assessment values are illustrative",
        "The score, material mix, financial value and CO₂e estimate are deterministic estimates, not quotes. The assessment itself is saved to your account.",
        tone="amber",
        icon_name="info",
    )


def render() -> None:
    ui.page_header(
        "Assessment · Step 2 of 3",
        "A clear read on your device",
        "Answer a short multi-step form about the device. ReLoop saves the assessment and its recommendation to your account through the API.",
    )

    notice = st.session_state.pop("assessment_notice", None)
    if notice:
        st.warning(notice)

    identification = flow.get_identification()
    result = flow.get_assessment()
    ui.flow_rail(FLOW_STEPS, active=2)

    if not identification:
        ui.empty_state(
            "No device identified yet",
            "Identify a device first and ReLoop will guide you through the assessment.",
            icon_name="scan",
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
            if st.button("Open dashboard", icon=":material/space_dashboard:", width="stretch"):
                st.switch_page("views/dashboard.py")
        return

    _reset_widgets(identification, result)
    editing = st.session_state.get("assessment_editing")
    if editing is None:
        editing = result is None
        st.session_state["assessment_editing"] = editing

    if result and not editing:
        _render_summary(result)
        return

    _render_form(identification)


render()
