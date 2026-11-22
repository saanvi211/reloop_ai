from __future__ import annotations

import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from components import ui
from components.maps import create_collection_map
from data import mock_data as d
from utils import api_client, flow
from utils.helpers import accepted_type_for, device_from_category


def _category_for_device(device: str) -> str:
    for category, mapped in d.CATEGORY_TO_DEVICE.items():
        if mapped == device:
            return category
    return "All categories"


def _centre_pool() -> list[dict]:
    try:
        points = api_client.list_centres(limit=200)
        st.session_state["centres_source"] = "api"
        return points
    except api_client.ApiError:
        st.session_state["centres_source"] = "local"
        return list(d.COLLECTION_POINTS)


def render() -> None:
    assessment = flow.get_assessment()
    identification = flow.get_identification()
    all_points = _centre_pool()
    ui.page_header(
        "Nearby centres · Bengaluru",
        "Find a demo repair shop or recycling centre",
        "Explore fictional repair shops, recyclers, drop-off points and kiosks. Filter by area, facility type, device or distance. All partners are unverified demo data.",
    )

    ui.banner(
        "Fictional demo directory",
        "Every shop, centre, phone number, email, rating, capacity and distance on this page is fictional and unverified. It exists only to test the interface.",
        tone="amber",
        icon_name="info",
    )

    requested_device = st.session_state.pop("map_device_default", None)
    requested_item = st.session_state.pop("map_item_default", None)
    if requested_device:
        st.session_state["map_category"] = _category_for_device(requested_device)
    elif requested_item and "map_category" not in st.session_state:
        st.session_state["map_category"] = "All categories"

    preferences = flow.get_settings()
    distance_default = max(1, min(20, int(preferences.get("max_distance_km", 12))))
    sort_options = ["Nearest first", "Highest rating", "Most capacity available"]
    sort_default = preferences.get("default_sort", "Nearest first")
    sort_index = sort_options.index(sort_default) if sort_default in sort_options else 0
    area_default = preferences.get("home_area", "All areas")

    if st.session_state.pop("map_reset_requested", False):
        for key in ["map_category", "map_max_distance", "map_sort"]:
            st.session_state.pop(key, None)

    with st.container(border=True):
        ui.section_header(
            "Filter centres",
            "Narrow the network by what matters to you",
            kicker="Filters",
        )
        search_col, area_col, type_col, category_col = st.columns([1.25, 0.9, 1, 1], gap="small")
        with search_col:
            query = st.text_input("Search", placeholder="Name, area or speciality")
        with area_col:
            area_options = ["All areas"] + sorted({point["area"] for point in all_points})
            area_index = area_options.index(area_default) if area_default in area_options else 0
            area = st.selectbox("Area", area_options, index=area_index)
        with type_col:
            facility = st.selectbox(
                "Facility type",
                ["All types"] + sorted({point["type"] for point in all_points}),
            )
        with category_col:
            category_options = ["All categories"] + d.IDENTIFY_CATEGORIES
            if st.session_state.get("map_category") not in category_options:
                st.session_state["map_category"] = "All categories"
            category = st.selectbox("Device category", category_options, key="map_category")

        distance_col, sort_col, open_col, reset_col = st.columns([1.4, 1, 0.8, 0.6], gap="small")
        with distance_col:
            max_distance = st.slider("Maximum distance (km)", 1, 20, distance_default, key="map_max_distance")
        with sort_col:
            sort_by = st.selectbox("Sort by", sort_options, index=sort_index, key="map_sort")
        with open_col:
            open_only = st.toggle("Open now only", value=False)
        with reset_col:
            st.write("")
            if st.button("Reset filters", icon=":material/restart_alt:", width="stretch"):
                st.session_state["map_reset_requested"] = True
                st.rerun()

    points = list(all_points)
    item = "All items"
    if category != "All categories":
        item = accepted_type_for(device_from_category(category))

    if query:
        needle = query.strip().lower()
        points = [
            point
            for point in points
            if needle in point["name"].lower()
            or needle in point["area"].lower()
            or needle in point.get("speciality", "").lower()
        ]
    if area != "All areas":
        points = [point for point in points if point["area"] == area]
    if facility != "All types":
        points = [point for point in points if point["type"] == facility]
    if item != "All items":
        points = [point for point in points if item in point["accepted"]]
    if open_only:
        points = [point for point in points if point["open_now"]]
    points = [point for point in points if point["distance_km"] <= max_distance]

    if sort_by == "Highest rating":
        points = sorted(points, key=lambda point: point["rating"], reverse=True)
    elif sort_by == "Most capacity available":
        points = sorted(points, key=lambda point: point["capacity"])
    else:
        points = sorted(points, key=lambda point: point["distance_km"])

    legend = "".join(
        [
            ui.pill("Recycling Centre", "green"),
            ui.pill("Drop-off", "teal"),
            ui.pill("Refurbisher", "blue"),
            ui.pill("Kiosk", "amber"),
            ui.pill("Repair Shop", "purple"),
        ]
    )
    result_html = f"""
    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;margin:6px 0 10px;">
      <div style="display:flex;align-items:baseline;gap:8px;">
        <strong style="font-family:'Sora',sans-serif;font-size:1.05rem;color:#F1F5F2;">{len(points)} demo centres</strong>
        <span style="font-size:.72rem;color:#91B5A0;">{sort_by.lower()} · within {max_distance} km · fictional data</span>
      </div>
      <div style="display:flex;flex-wrap:wrap;gap:6px;">{legend}</div>
    </div>
    """
    st.html(result_html)

    if not points:
        ui.empty_state(
            "No centres match those filters",
            "Try clearing the search, choosing a different area or increasing the maximum distance.",
            icon_name="search",
        )
        return

    with st.container(border=True):
        map_head, focus_head = st.columns([1.5, 1], gap="medium")
        with map_head:
            ui.section_header(
                "Coverage map",
                f"{len(points)} fictional points across Bengaluru",
                kicker="Map",
            )
        with focus_head:
            focus = st.selectbox(
                "Focus map on",
                ["All of Bengaluru"] + [point["name"] for point in points],
            )
        map_object = create_collection_map(
            points,
            selected_name=None if focus == "All of Bengaluru" else focus,
        )
        st_folium(
            map_object,
            height=540,
            use_container_width=True,
            returned_objects=[],
            key="collection_map",
        )

    export = pd.DataFrame(
        [
            {
                "name": point["name"],
                "type": point["type"],
                "area": point["area"],
                "address": point["address"],
                "phone": point.get("phone", ""),
                "email": point.get("email", ""),
                "hours": point["hours"],
                "capacity_pct": point["capacity"],
                "rating": point["rating"],
                "distance_km": point["distance_km"],
                "speciality": point.get("speciality", ""),
                "fictional": "Yes",
            }
            for point in points
        ]
    )
    st.download_button(
        "Download demo partner list",
        data=export.to_csv(index=False).encode("utf-8"),
        file_name="reloop_demo_partners.csv",
        mime="text/csv",
        icon=":material/download:",
    )

    st.html('<div style="height:8px"></div>')
    ui.section_header(
        "Demo partner directory",
        "Addresses, hours, contacts and accepted items — all fictional and unverified",
        kicker="Directory",
    )
    left, right = st.columns(2, gap="medium")
    for index, point in enumerate(points):
        with left if index % 2 == 0 else right:
            ui.collection_card(point)

    if identification and not assessment:
        ui.banner(
            "You have an identified device",
            f"{identification['device']} was identified but not assessed yet. Complete the assessment to get a pathway-specific partner suggestion.",
            tone="blue",
            icon_name="scan",
        )

    if st.session_state.get("centres_source") == "local":
        ui.banner(
            "Offline demo directory",
            "The ReLoop API is not reachable, so the bundled fictional partner list is shown. Start the backend to load the seeded directory.",
            tone="amber",
            icon_name="info",
        )
    else:
        ui.banner(
            "Served by the ReLoop API",
            "Partner records, accepted items, capacity and coordinates come from the backend directory. Every partner remains fictional demo data.",
            tone="green",
            icon_name="info",
        )


render()
