from __future__ import annotations

import streamlit as st

from components import ui
from data import mock_data as d
from utils import api_client, flow
from utils.helpers import device_from_category, format_currency
from utils.identification import manual_identification, predict_from_image

FLOW_STEPS = [
    {"title": "Identify", "body": "Add a photo or device details"},
    {"title": "Assess", "body": "Answer condition questions"},
    {"title": "Route", "body": "Follow the recommendation"},
]


def _next_photo_version() -> None:
    st.session_state["photo_version"] = int(st.session_state.get("photo_version", 1)) + 1


def _remove_photo() -> None:
    flow.clear_photo()
    flow.clear_identification()
    flow.clear_assessment()
    flow.clear_answers()
    _next_photo_version()
    st.toast("Photo removed.")
    st.rerun()


def _new_assessment() -> None:
    flow.clear_assessment()
    flow.clear_answers()
    st.session_state.pop("assessment_step", None)
    st.session_state.pop("assessment_editing", None)


def render() -> None:
    ui.page_header(
        "Identify e-waste · Step 1 of 3",
        "Tell us what you're retiring",
        "Upload a photo, use your camera, or pick the device category manually. ReLoop AI returns mock predictions with confidence scores.",
    )
    ui.flow_rail(FLOW_STEPS, active=1)
    ui.banner(
        "Mock classifier, real persistence",
        "The backend runs a deterministic mock classifier and stores each identification with your account. The module is ready for a real vision model later.",
        tone="blue",
        icon_name="info",
    )

    version = st.session_state.get("photo_version", 1)
    photo = flow.get_photo()

    form_col, info_col = st.columns([1.35, 0.85], gap="medium")

    with form_col:
        with st.container(border=True):
            ui.section_header(
                "Add a device photo",
                "Drag and drop a file or capture one with your camera",
                kicker="Step 1 · Image",
            )
            upload_tab, camera_tab = st.tabs(["Upload image", "Use camera"])

            with upload_tab:
                uploaded = st.file_uploader(
                    "Drag and drop a device photo",
                    type=["png", "jpg", "jpeg"],
                    help="JPG or PNG up to 5 MB. The image is uploaded securely to your ReLoop account.",
                    key=f"identify_upload_{version}",
                )
            with camera_tab:
                captured = st.camera_input(
                    "Take a photo of the device",
                    help="Allow camera access in your browser.",
                    key=f"identify_camera_{version}",
                )

            if uploaded is not None:
                data = uploaded.getvalue()
                if not photo or photo.get("data") != data:
                    flow.save_photo(data, uploaded.name)
                    flow.clear_identification()
                    _new_assessment()
                    photo = flow.get_photo()
            elif captured is not None:
                data = captured.getvalue()
                if not photo or photo.get("data") != data:
                    flow.save_photo(data, "camera-capture.png")
                    flow.clear_identification()
                    _new_assessment()
                    photo = flow.get_photo()

            if photo:
                preview_col, action_col = st.columns([1, 1], gap="small")
                with preview_col:
                    st.image(photo["data"], caption=photo["name"], width="stretch")
                with action_col:
                    st.caption("Image ready for identification.")
                    if st.button("Remove photo", icon=":material/delete:", width="stretch"):
                        _remove_photo()
                    if st.button("Replace photo", icon=":material/sync:", width="stretch"):
                        _remove_photo()
            else:
                ui.empty_state(
                    "No photo added yet",
                    "Upload or capture a photo, or choose the category manually below.",
                    icon_name="upload",
                )

        with st.container(border=True):
            ui.section_header(
                "Run identification",
                "Mock predictions include confidence scores",
                kicker="Step 1 · Identify",
            )
            hint = st.text_input(
                "Optional description to improve the mock guess",
                placeholder="e.g. black smartphone, tangled USB cable",
                key="identify_hint",
            )
            identify = st.button(
                "Identify device",
                type="primary",
                icon=":material/auto_awesome:",
                width="stretch",
                disabled=not bool(photo),
            )
            if identify and photo:
                with st.spinner("Uploading the image and running the mock classifier…"):
                    try:
                        content_type = (
                            "image/png"
                            if photo["name"].lower().endswith(".png")
                            else "image/jpeg"
                        )
                        prediction = api_client.upload_identification(
                            photo["data"], photo["name"], content_type, hint
                        )
                    except api_client.ApiError as exc:
                        if exc.status_code and not exc.offline:
                            st.error(exc.message)
                            prediction = None
                        else:
                            prediction = predict_from_image(photo["data"], photo["name"], hint)
                            st.warning(
                                "The backend is offline. This identification stays in the browser "
                                "and will not be saved to your account."
                            )
                if prediction:
                    flow.save_identification(prediction)
                    _new_assessment()
                    st.toast("Identification complete.")
                    st.rerun()

            identification = flow.get_identification()
            if identification:
                st.divider()
                confidence = int(round(identification["confidence"] * 100))
                if identification["method"] == "manual":
                    ui.banner(
                        "Category selected manually",
                        f"{identification['device']} · manual confidence {confidence}%.",
                        tone="green",
                        icon_name="check",
                    )
                else:
                    detected = identification.get("detected_device")
                    if detected and detected != identification["device"]:
                        pred_title = f"Predicted: {detected} ({identification['device']})"
                    else:
                        pred_title = f"Predicted: {identification['device']}"

                    ui.banner(
                        pred_title,
                        f"Confidence {confidence}% · top {len(identification['predictions'])} matches shown below.",
                        tone="green" if confidence >= 60 else "amber",
                        icon_name="scan",
                    )
                ui.prediction_rows(identification["predictions"])
                if identification.get("needs_review"):
                    st.warning("Confidence is low. Confirm or change the device category before continuing.")
                selected_device = device_from_category(identification["device"])
                spec = d.DEVICE_CATALOG[selected_device]
                st.caption(
                    f"{identification['device']} maps to {selected_device} · typical weight {spec['weight_kg']} kg · "
                    f"{spec['recyclable_pct']}% recyclable."
                )
                if st.button(
                    "Continue to assessment",
                    type="primary",
                    icon=":material/fact_check:",
                    width="stretch",
                ):
                    st.switch_page("views/assessment.py")

        with st.container(border=True):
            ui.section_header(
                "Manual category",
                "Use this when confidence is low or no photo is available",
                kicker="Fallback",
            )
            manual = st.selectbox(
                "Device category",
                d.IDENTIFY_CATEGORIES,
                index=d.IDENTIFY_CATEGORIES.index(identification["device"])
                if identification and identification["device"] in d.IDENTIFY_CATEGORIES
                else 0,
            )
            if st.button("Use selected category", icon=":material/touch_app:", width="stretch"):
                try:
                    identification = api_client.manual_identification(manual)
                except api_client.ApiError as exc:
                    if exc.status_code and not exc.offline:
                        st.error(exc.message)
                        identification = None
                    else:
                        identification = manual_identification(manual)
                        st.warning(
                            "The backend is offline. This manual identification stays in the browser."
                        )
                if identification:
                    flow.save_identification(identification)
                    _new_assessment()
                    st.toast(f"{manual} selected manually.")
                    st.rerun()

    with info_col:
        with st.container(border=True):
            ui.section_header("How it works", "Three steps from drawer to recycler", kicker="Process")
            ui.steps(
                [
                    {"title": "Add a photo", "body": "Upload, capture or skip straight to manual selection."},
                    {"title": "Confirm the device", "body": "Review confidence and correct the category if needed."},
                    {"title": "Assess it", "body": "Answer a short multi-step form about condition and safety."},
                ]
            )

        with st.container(border=True):
            ui.section_header("Categories we recognise", "Eight consumer device groups", kicker="Coverage")
            st.html(
                '<div class="rl-chip-line">'
                + "".join(ui.pill(item, "outline") for item in d.IDENTIFY_CATEGORIES)
                + "</div>",
            )

        if identification:
            with st.container(border=True):
                ui.section_header(
                    "Current selection",
                    f"{identification['device']} · {int(identification['confidence'] * 100)}%",
                    kicker="Status",
                )
                ui.kv_list(
                    [
                        {"label": "Category", "value": identification["device"]},
                        {"label": "Mapped device", "value": device_from_category(identification["device"])},
                        {"label": "Source", "value": identification.get("source", "image")},
                        {"label": "Low confidence", "value": "Yes" if identification.get("needs_review") else "No"},
                    ]
                )
                if st.button("Start over", icon=":material/refresh:", width="stretch"):
                    flow.reset_flow()
                    _next_photo_version()
                    st.rerun()

        assessment = flow.get_assessment()
        if assessment:
            with st.container(border=True):
                ui.section_header(
                    "Assessment ready",
                    f"{assessment['device']} · {assessment['score']}/100",
                    kicker="Continue",
                )
                if st.button("Open assessment", type="primary", width="stretch"):
                    st.switch_page("views/assessment.py")

        if identification:
            mapped = device_from_category(identification["device"])
            if mapped in d.DEVICE_CATALOG:
                st.caption(
                    f"Estimated reusable value for a typical {mapped.lower()}: "
                    f"up to {format_currency(d.DEVICE_CATALOG[mapped]['base_value'])}."
                )

        ui.banner(
            "Stored with your account",
            "Photos are validated, size-limited and saved by the ReLoop API. You can remove an identification before assessing it.",
            tone="green",
            icon_name="shield",
        )


render()
