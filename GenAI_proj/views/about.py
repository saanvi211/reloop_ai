from __future__ import annotations

import streamlit as st

from components import ui
from data import mock_data as d
from utils import api_client


def _partner_count() -> int:
    try:
        return len(api_client.list_centres(limit=200))
    except api_client.ApiError:
        return len(d.COLLECTION_POINTS)


def render() -> None:
    ui.page_header(
        "About ReLoop AI",
        "Circular electronics, designed for everyone",
        "A sustainability-first product concept that helps people identify, route and measure the impact of their electronic waste.",
    )

    st.html(
        f"""
        <div class="rl-about-hero">
          <span class="rl-kicker">{ui.icon("globe", 14)} Our mission</span>
          <h2>Make circular electronics the default, not the exception.</h2>
          <p>
            Most old phones, laptops and appliances still end up in drawers or informal waste streams.
            ReLoop AI brings identification, verified routing and measurable impact into one calm,
            accessible experience — starting with a transparent frontend prototype.
          </p>
          <div class="rl-about-stats">
            <span class="rl-about-stat">{ui.icon("scan", 14)} AI-ready workflows</span>
            <span class="rl-about-stat">{ui.icon("map", 14)} Local collection network</span>
            <span class="rl-about-stat">{ui.icon("chart", 14)} Environmental Impact</span>
            <span class="rl-about-stat">{ui.icon("shield", 14)} Privacy-first design</span>
          </div>
        </div>
        """,
    )

    ui.metric_grid(
        [
            {
                "label": "Core product pages",
                "value": "6",
                "icon": "globe",
                "tone": "green",
                "note": "dashboard to about",
            },
            {
                "label": "Demo partner hubs",
                "value": str(_partner_count()),
                "icon": "map",
                "tone": "blue",
                "note": "seeded across Bengaluru",
            },
            {
                "label": "Device types supported",
                "value": str(len(d.DEVICE_CATALOG)),
                "icon": "cpu",
                "tone": "amber",
                "note": "with material estimates",
            },
            {
                "label": "Backend",
                "value": "Live API",
                "icon": "shield",
                "tone": "purple",
                "note": "FastAPI + SQLite",
            },
        ]
    )

    st.html('<div style="height:4px"></div>')
    ui.section_header(
        "Product principles",
        "The decisions behind the experience",
        kicker="Design",
    )
    principle_left, principle_right = st.columns(2, gap="medium")
    with principle_left:
        ui.insight_list(
            [
                {
                    "title": "Trust first",
                    "body": "Clear estimates, verified partners and no hidden data collection.",
                    "icon": "shield",
                    "tone": "green",
                },
                {
                    "title": "Local by design",
                    "body": "Neighbourhood drop-offs, area filters and live capacity signals.",
                    "icon": "map",
                    "tone": "blue",
                },
            ]
        )
    with principle_right:
        ui.insight_list(
            [
                {
                    "title": "Measurable impact",
                    "body": "Every kilogram connects to carbon, materials and circularity.",
                    "icon": "chart",
                    "tone": "amber",
                },
                {
                    "title": "Reward the loop",
                    "body": "Points, badges and friendly competition make recycling habitual.",
                    "icon": "gift",
                    "tone": "purple",
                },
            ]
        )

    process_col, stack_col = st.columns([1.1, 1], gap="medium")
    with process_col:
        with st.container(border=True):
            ui.section_header(
                "How ReLoop works",
                "A simple loop from drawer to recovered material",
                kicker="Journey",
            )
            ui.steps(
                [
                    {"title": "Identify", "body": "Scan a device or enter details to understand its recovery potential."},
                    {"title": "Route", "body": "Match it to a nearby verified recycler, refurbisher or kiosk."},
                    {"title": "Measure", "body": "Track diversion, carbon savings and recovered materials over time."},
                    {"title": "Reward", "body": "Earn points and badges for every verified circular action."},
                ]
            )
    with stack_col:
        with st.container(border=True):
            ui.section_header(
                "Built with",
                "A lightweight full-stack prototype",
                kicker="Technology",
            )
            st.html(
                '<div class="rl-chip-line">'
                + "".join(
                    ui.pill(item, "outline")
                    for item in [
                        "Python",
                        "Streamlit",
                        "FastAPI",
                        "SQLAlchemy",
                        "SQLite",
                        "Plotly",
                        "Folium",
                        "Pandas",
                    ]
                )
                + "</div>",
            )
            ui.kv_list(
                [
                    {"label": "Architecture", "value": "Streamlit + FastAPI"},
                    {"label": "State", "value": "Account-scoped"},
                    {"label": "Database", "value": "SQLite"},
                    {"label": "ML model", "value": "Deterministic mock"},
                ]
            )
            ui.banner(
                "Connected prototype",
                "Assessments, routes, settings and history persist through the API. Classification and impact values remain transparent estimates.",
                tone="blue",
                icon_name="info",
            )

    roadmap_col, faq_col = st.columns([1, 1.15], gap="medium")
    with roadmap_col:
        with st.container(border=True):
            ui.section_header(
                "Roadmap",
                "From prototype to production platform",
                kicker="What's next",
            )
            ui.timeline(d.ROADMAP)
    with faq_col:
        with st.container(border=True):
            ui.section_header(
                "Frequently asked",
                "Prototype questions, answered",
                kicker="FAQ",
            )
            with st.expander("Is this connected to a real recycling network?", expanded=True):
                st.write(
                    "No. All centres, capacities, ratings and distances are mock data created for this frontend prototype."
                )
            with st.expander("Does the AI actually identify devices?"):
                st.write(
                    "The backend runs a deterministic mock classifier and stores each identification with your account. A real vision model can replace it behind the same API."
                )
            with st.expander("Where does the data come from?"):
                st.write(
                    "Account records are stored in SQLite through the ReLoop API. Partner and demo figures come from seeded fictional data in data/mock_data.py."
                )
            with st.expander("Does it work on mobile?"):
                st.write(
                    "Yes. The layout uses responsive Streamlit columns, fluid grids and custom CSS breakpoints for smaller screens."
                )
            with st.expander("Can I reset my demo state?"):
                st.write(
                    "Refresh the browser tab to clear local session state. Account records remain in the ReLoop database unless you delete them through the API or reset the database."
                )

    ui.banner(
        "Connected circular recovery prototype",
        "The ReLoop API persists account, assessment and history data. Partner records are fictional and AI or impact figures remain estimates.",
        tone="blue",
        icon_name="info",
    )


render()
