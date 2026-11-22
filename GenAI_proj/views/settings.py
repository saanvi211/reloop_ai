from __future__ import annotations

import json

import streamlit as st

from components import ui
from data import mock_data as d
from styles.theme import ACCENTS
from utils import api_client, flow


def _area_options() -> list[str]:
    try:
        return sorted({centre["area"] for centre in api_client.list_centres(limit=200)})
    except api_client.ApiError:
        return sorted({point["area"] for point in d.COLLECTION_POINTS})


def render() -> None:
    user = flow.get_user()
    settings = flow.get_settings()
    if "accent" not in st.session_state:
        st.session_state.accent = settings.get("accent", "Emerald")
    st.session_state.preferences = settings

    ui.page_header(
        "Settings",
        "Make ReLoop yours",
        "Manage your profile, notification preferences, appearance and account data. Changes are saved to the ReLoop API.",
    )

    profile_tab, preference_tab, privacy_tab = st.tabs(["Profile", "Preferences", "Privacy & data"])

    with profile_tab:
        profile_col, summary_col = st.columns([1.4, 1], gap="medium")
        with profile_col:
            with st.container(border=True):
                ui.section_header(
                    "Profile details",
                    "Used across your dashboard and assessments",
                    kicker="Account",
                )
                with st.form("profile_form"):
                    name = st.text_input("Full name", value=user["name"])
                    email = st.text_input("Email", value=user["email"])
                    city = st.text_input("City", value=user["city"])
                    st.text_input("Membership tier", value=user["tier"], disabled=True)
                    if st.form_submit_button("Save profile", type="primary", width="stretch"):
                        try:
                            api_client.update_user(
                                {"name": name, "email": email, "city": city}
                            )
                            api_client.update_profile({"city": city})
                        except api_client.ApiError as exc:
                            if exc.offline:
                                st.session_state.profile = {
                                    "name": name or user["name"],
                                    "email": email or user["email"],
                                    "city": city or user["city"],
                                    "tier": user["tier"],
                                }
                                st.warning("The backend is offline. Profile changes stay in this browser.")
                            else:
                                st.error(exc.message)
                        else:
                            flow.refresh_user()
                            st.toast("Profile updated.")
        with summary_col:
            with st.container(border=True):
                ui.section_header(
                    "Your account",
                    "A quick snapshot of your membership",
                    kicker="Summary",
                )
                ui.kv_list(
                    [
                        {"label": "Name", "value": user["name"]},
                        {"label": "City", "value": user["city"]},
                        {"label": "Tier", "value": user["tier"]},
                        {"label": "Points", "value": f"{user['points']:,}"},
                        {"label": "Member since", "value": user["member_since"]},
                    ]
                )
            with st.container(border=True):
                ui.section_header(
                    "About this build",
                    "End-to-end circular recovery prototype",
                    kicker="Build",
                )
                ui.kv_list(
                    [
                        {"label": "Version", "value": "1.0 · Sections 4–10"},
                        {"label": "Environment", "value": "Streamlit + FastAPI"},
                        {"label": "Data mode", "value": "API records + mock AI"},
                        {"label": "AI model", "value": "Deterministic mock"},
                        {"label": "Persistence", "value": "SQLite account storage"},
                    ]
                )

    with preference_tab:
        pref_col, accent_col = st.columns([1.4, 1], gap="medium")
        with pref_col:
            with st.container(border=True):
                ui.section_header(
                    "Notifications",
                    "Choose what ReLoop should remind you about",
                    kicker="Preferences",
                )
                with st.form("preference_form"):
                    pickup_reminders = st.toggle(
                        "Pickup reminders",
                        value=settings["pickup_reminders"],
                        help="Remind me before a scheduled home pickup.",
                    )
                    impact_digest = st.toggle(
                        "Monthly impact digest",
                        value=settings["impact_digest"],
                        help="Send a summary of diversion and carbon savings.",
                    )
                    partner_offers = st.toggle(
                        "Partner offers",
                        value=settings["partner_offers"],
                        help="Occasional offers from verified repair and recycling partners.",
                    )
                    mode_options = ["Home pickup", "Drop-off"]
                    window_options = ["Weekday mornings", "Weekday evenings", "Weekend mornings", "Weekend afternoons"]
                    default_mode = st.selectbox(
                        "Default pickup mode",
                        mode_options,
                        index=mode_options.index(settings["default_mode"]),
                    )
                    preferred_window = st.selectbox(
                        "Preferred pickup window",
                        window_options,
                        index=window_options.index(settings["preferred_window"]),
                    )
                    if st.form_submit_button("Save preferences", type="primary", width="stretch"):
                        try:
                            flow.save_settings(
                                {
                                    "pickup_reminders": pickup_reminders,
                                    "impact_digest": impact_digest,
                                    "partner_offers": partner_offers,
                                    "default_mode": default_mode,
                                    "preferred_window": preferred_window,
                                }
                            )
                        except api_client.ApiError as exc:
                            st.error(exc.message)
                        else:
                            st.toast("Preferences updated.")
                            st.rerun()

            with st.container(border=True):
                ui.section_header(
                    "Location preferences",
                    "Used to personalise nearby centre recommendations",
                    kicker="Location",
                )
                city = st.text_input("City", value=settings.get("city", user["city"]))
                areas = _area_options()
                current_area = settings.get("home_area", areas[0] if areas else "")
                home_area = st.selectbox(
                    "Home area",
                    areas,
                    index=areas.index(current_area) if current_area in areas else 0,
                )
                max_distance = st.slider(
                    "Maximum partner distance (km)",
                    1,
                    20,
                    int(settings.get("max_distance_km", 12)),
                )
                sort_options = ["Nearest first", "Highest rating", "Most capacity available"]
                default_sort = st.selectbox(
                    "Default centre sort",
                    sort_options,
                    index=sort_options.index(settings.get("default_sort", "Nearest first"))
                    if settings.get("default_sort") in sort_options
                    else 0,
                )
                location_sharing = st.toggle(
                    "Use my approximate location for distance estimates",
                    value=settings.get("location_sharing", True),
                )
                if st.button("Save location preferences", type="primary", width="stretch"):
                    try:
                        flow.save_settings(
                            {
                                "city": city or user["city"],
                                "home_area": home_area,
                                "max_distance_km": max_distance,
                                "default_sort": default_sort,
                                "location_sharing": location_sharing,
                            }
                        )
                    except api_client.ApiError as exc:
                        st.error(exc.message)
                    else:
                        flow.refresh_user()
                        st.toast("Location preferences updated.")
                        st.rerun()
        with accent_col:
            with st.container(border=True):
                ui.section_header(
                    "Appearance",
                    "Choose the accent that feels right",
                    kicker="Theme",
                )
                st.selectbox("Accent colour", list(ACCENTS.keys()), key="accent")
                st.caption("The accent updates buttons, highlights and the interface focus colour.")
                if st.button("Save appearance", type="primary", width="stretch"):
                    try:
                        flow.save_settings({"accent": st.session_state.get("accent", "Emerald")})
                    except api_client.ApiError as exc:
                        st.error(exc.message)
                    else:
                        st.toast("Appearance saved.")
                if st.button("Reset to Emerald", width="stretch"):
                    st.session_state.accent = "Emerald"
                    flow.save_settings({"accent": "Emerald"})
                    st.rerun()
            with st.container(border=True):
                ui.section_header(
                    "Interface",
                    "The ReLoop design system",
                    kicker="System",
                )
                ui.kv_list(
                    [
                        {"label": "Theme", "value": "Premium environmental"},
                        {"label": "Layout", "value": "Responsive dashboard"},
                        {"label": "Navigation", "value": "Sidebar · 9 pages"},
                        {"label": "Icons", "value": "Material + inline SVG"},
                    ]
                )

    with privacy_tab:
        privacy_col, export_col = st.columns([1.35, 1], gap="medium")
        with privacy_col:
            with st.container(border=True):
                ui.section_header(
                    "Privacy controls",
                    "You decide what stays on this device",
                    kicker="Privacy",
                )
                anonymous_analytics = st.toggle(
                    "Anonymous product analytics",
                    value=settings["anonymous_analytics"],
                )
                photo_retention = st.toggle(
                    "Keep uploaded photos after assessment",
                    value=settings["photo_retention"],
                )
                share_impact = st.toggle(
                    "Include me in citywide impact benchmarks",
                    value=settings["share_impact"],
                )
                if st.button("Save privacy settings", type="primary", width="stretch"):
                    try:
                        flow.save_settings(
                            {
                                "anonymous_analytics": anonymous_analytics,
                                "photo_retention": photo_retention,
                                "share_impact": share_impact,
                            }
                        )
                    except api_client.ApiError as exc:
                        st.error(exc.message)
                    else:
                        st.toast("Privacy settings updated.")
                        st.rerun()
        with export_col:
            with st.container(border=True):
                ui.section_header(
                    "Your demo data",
                    "Export or reset this browser session",
                    kicker="Data",
                )
                payload = {
                    "user": flow.get_user(),
                    "settings": flow.get_settings(),
                    "history": flow.get_history(),
                    "assessment": flow.get_assessment(),
                }
                st.download_button(
                    "Export my demo data",
                    data=json.dumps(payload, indent=2, default=str).encode("utf-8"),
                    file_name="reloop_demo_data.json",
                    mime="application/json",
                    icon=":material/download:",
                    width="stretch",
                )
                st.divider()
                confirm = st.checkbox("I understand this clears the current session.")
                if st.button(
                    "Reset demo session",
                    disabled=not confirm,
                    icon=":material/restart_alt:",
                    width="stretch",
                ):
                    for key in [
                        "profile",
                        "preferences",
                        "privacy",
                        "accent",
                        "settings_cache",
                        "user_cache",
                        "identify_result",
                        "assessment_saved",
                        "recycling_history",
                        "pickup_booked",
                    ]:
                        st.session_state.pop(key, None)
                    st.toast("Demo session reset.")
                    st.rerun()

    ui.banner(
        "Account settings are persisted",
        "Profile, preferences, privacy choices and history are stored by the ReLoop API. If the backend is unavailable, changes stay in this browser session until it reconnects.",
        tone="blue",
        icon_name="shield",
    )


render()
