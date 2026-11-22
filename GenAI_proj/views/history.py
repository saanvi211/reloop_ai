from __future__ import annotations

import pandas as pd
import streamlit as st

from components import ui
from data import mock_data as d
from utils import flow
from utils.helpers import format_currency, format_number


def render() -> None:
    ui.page_header(
        "History",
        "Every device, every pathway",
        "A single record of your assessments, scheduled pickups and completed recoveries. Search, filter and open any record for details.",
    )

    history = flow.get_history()

    with st.container(border=True):
        ui.section_header(
            "Filter your record",
            "Find a device, pathway, partner or status",
            kicker="Filters",
        )
        status_col, category_col, pathway_col = st.columns([1.15, 1, 1], gap="small")
        with status_col:
            status = st.segmented_control(
                "Status",
                ["All", "Completed", "Scheduled", "Processing"],
                default="All",
                label_visibility="collapsed",
            )
        with category_col:
            categories = sorted({item.get("category", "Other") for item in history})
            category = st.selectbox("Device category", ["All categories"] + categories)
        with pathway_col:
            pathway = st.selectbox("Pathway", ["All pathways"] + list(d.PATHWAYS.keys()))

        device_col, search_col = st.columns([1, 1.6], gap="small")
        with device_col:
            devices = sorted({item["device"] for item in history})
            device = st.selectbox("Device type", ["All devices"] + devices)
        with search_col:
            query = st.text_input("Search", placeholder="Device, partner, detail or notes")

        if not status:
            status = "All"
        filtered = list(history)
        if status != "All":
            filtered = [item for item in filtered if item["status"] == status]
        if category != "All categories":
            filtered = [item for item in filtered if item.get("category") == category]
        if pathway != "All pathways":
            filtered = [item for item in filtered if item.get("pathway") == pathway]
        if device != "All devices":
            filtered = [item for item in filtered if item["device"] == device]
        if query:
            needle = query.strip().lower()
            filtered = [
                item
                for item in filtered
                if needle in item["device"].lower()
                or needle in item["detail"].lower()
                or needle in item["partner"].lower()
                or needle in item.get("notes", "").lower()
                or needle in item.get("pathway", "").lower()
            ]

        export = pd.DataFrame(filtered)
        export = export.drop(columns=["image", "image_url"], errors="ignore")
        st.download_button(
            "Export filtered history",
            data=export.to_csv(index=False).encode("utf-8"),
            file_name="reloop_history.csv",
            mime="text/csv",
            icon=":material/download:",
        )

    totals = flow.completed_totals(filtered)
    ui.metric_grid(
        [
            {
                "label": "Devices recovered",
                "value": format_number(totals["devices"]),
                "icon": "cpu",
                "tone": "green",
                "note": "completed drop-offs in filter",
            },
            {
                "label": "Weight diverted (est.)",
                "value": f"{format_number(totals['weight_kg'])} kg",
                "icon": "recycle",
                "tone": "blue",
                "note": "kept out of landfill",
            },
            {
                "label": "CO₂e avoided (est.)",
                "value": f"{format_number(totals['co2_kg'])} kg",
                "icon": "cloud",
                "tone": "amber",
                "note": "estimated avoided emissions",
            },
            {
                "label": "Points earned",
                "value": format_number(totals["points"]),
                "icon": "award",
                "tone": "purple",
                "note": "from completed records",
            },
        ]
    )

    if not filtered:
        ui.empty_state(
            "No records match those filters",
            "Try a different status, category, pathway, device type or search term.",
            icon_name="history",
        )
    else:
        ui.section_header(
            "Assessment & recovery records",
            f"{len(filtered)} matching record(s)",
            kicker="Log",
        )
        ui.history_list(filtered)

        labels = [
            f"{index + 1}. {item['date']} · {item['device']} · {item.get('pathway', 'Recycle')}"
            for index, item in enumerate(filtered)
        ]
        chosen = st.selectbox("Open a record for full details", labels)
        entry = filtered[labels.index(chosen)]
        with st.container(border=True):
            ui.section_header(
                f"{entry['device']} · {entry['date']}",
                f"{entry.get('pathway', 'Recycle')} pathway · {entry['status']}",
                kicker="Record details",
            )
            image_col, detail_col = st.columns([1, 1.8], gap="medium")
            with image_col:
                image = flow.history_image(entry)
                if image:
                    st.image(image, caption=entry.get("image_name") or "Device photo", width="stretch")
                else:
                    st.caption("No photo stored for this record.")
                    ui.empty_state(
                        "Record without a photo",
                        "This entry was created without an uploaded image.",
                        icon_name=entry.get("icon", "cpu"),
                    )
            with detail_col:
                ui.answer_grid(
                    [
                        {"label": "Device", "value": entry["device"]},
                        {"label": "Detail", "value": entry["detail"]},
                        {"label": "Category", "value": entry.get("category", "Other")},
                        {"label": "Pathway", "value": entry.get("pathway", "Recycle")},
                        {"label": "Partner", "value": entry["partner"]},
                        {"label": "Status", "value": entry["status"]},
                        {"label": "Score", "value": f"{entry.get('score', 0)}/100"},
                        {"label": "Battery", "value": entry.get("battery_condition", "Normal")},
                        {"label": "Weight (est.)", "value": f"{entry['weight_kg']} kg"},
                        {"label": "CO₂e avoided (est.)", "value": f"{entry['co2_kg']} kg"},
                        {"label": "Points", "value": format_number(entry.get("points", 0))},
                        {"label": "Value (est.)", "value": format_currency(entry.get("score", 0) * 18)},
                    ]
                )
                st.caption(f"Notes: {entry.get('notes', 'No notes for this record.')}")

    action_col, impact_col, _ = st.columns([1, 1, 2], gap="small")
    with action_col:
        if st.button(
            "Log a new device",
            type="primary",
            icon=":material/document_scanner:",
            width="stretch",
        ):
            st.switch_page("views/identify.py")
    with impact_col:
        if st.button("View environmental impact", icon=":material/monitoring:", width="stretch"):
            st.switch_page("views/analytics.py")

    if st.session_state.get("history_source") == "local":
        ui.banner(
            "Offline demo history",
            "The ReLoop API is not reachable. New records stay in this browser session and the starting records are bundled mock data.",
            tone="amber",
            icon_name="info",
        )
    else:
        ui.banner(
            "Stored by the ReLoop API",
            "Assessments, partner routes and statuses are stored against your account. Photos are served through authenticated API requests.",
            tone="blue",
            icon_name="info",
        )


render()
