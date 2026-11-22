from __future__ import annotations

import streamlit as st

from components import ui
from data import mock_data as d
from utils import api_client
from utils.helpers import format_number


def render() -> None:
    try:
        impact = api_client.impact_stats("all")
        totals = impact["totals"]
        total_waste = int(totals["weight_kg"])
        total_co2 = int(totals["co2_kg"])
        total_devices = totals["devices_recovered"]
        partner_count = len(api_client.list_centres(limit=200))
    except api_client.ApiError:
        total_waste = int(d.MONTHLY_IMPACT["waste_kg"].sum())
        total_co2 = int(d.MONTHLY_IMPACT["co2_kg"].sum())
        total_devices = int(d.MONTHLY_IMPACT["devices"].sum())
        partner_count = len(d.COLLECTION_POINTS)

    ui.hero(
        eyebrow="ReLoop AI · Circular electronics",
        title="Give Your Electronics",
        accent="a Second Life.",
        subtitle=(
            "ReLoop AI helps you identify, assess and route old devices to demo recyclers. "
            "Get a transparent recyclability score, safe handling guidance and a clear next step — "
            "all in one calm workspace."
        ),
        chips=[
            {"icon": "scan", "text": "AI-powered identification"},
            {"icon": "pin", "text": f"{partner_count} fictional Bengaluru partners"},
            {"icon": "shield", "text": "Battery-safe guidance"},
        ],
        ring_value=68,
        ring_label="circularity",
    )

    start_col, identify_col, _ = st.columns([1, 1, 2.2], gap="small")
    with start_col:
        if st.button(
            "Get Started",
            type="primary",
            icon=":material/rocket_launch:",
            width="stretch",
        ):
            st.switch_page("views/dashboard.py")
    with identify_col:
        if st.button(
            "Identify Device",
            icon=":material/document_scanner:",
            width="stretch",
        ):
            st.switch_page("views/identify.py")

    st.html(
        """
        <div class="rl-landing-trust">
          <span><strong>2,400+</strong> Bengaluru households</span>
          <span><strong>91%</strong> landfill avoided</span>
          <span><strong>4.8/5</strong> average partner rating</span>
        </div>
        """
    )

    ui.section_header(
        "Environmental impact",
        "Real outcomes from the ReLoop demo network",
        kicker="Impact so far",
    )
    ui.metric_grid(
        [
            {
                "label": "E-waste diverted",
                "value": f"{format_number(total_waste)} kg",
                "delta": "+12.4%",
                "direction": "up",
                "icon": "recycle",
                "tone": "green",
                "note": "across the demo network",
            },
            {
                "label": "CO₂ avoided",
                "value": f"{format_number(total_co2)} kg",
                "delta": "+8.2%",
                "direction": "up",
                "icon": "cloud",
                "tone": "blue",
                "note": "equal to 139 tree-years",
            },
            {
                "label": "Devices recovered",
                "value": format_number(total_devices),
                "delta": "+6.5%",
                "direction": "up",
                "icon": "cpu",
                "tone": "amber",
                "note": "reused, repaired or recycled",
            },
            {
                "label": "Demo partners",
                "value": str(partner_count),
                "icon": "pin",
                "tone": "purple",
                "note": "open, mapped and rated",
            },
        ]
    )

    ui.section_header(
        "How it works",
        "Four simple steps from drawer to safe recovery",
        kicker="The process",
    )
    ui.how_it_works(
        [
            {
                "title": "Identify",
                "body": "Upload a photo or describe the device you want to retire.",
                "icon": "scan",
                "tone": "green",
            },
            {
                "title": "Assess",
                "body": "See a transparent recyclability score, materials and value.",
                "icon": "fact_check",
                "tone": "blue",
            },
            {
                "title": "Decide",
                "body": "Compare reuse, repair, pickup and drop-off routes.",
                "icon": "target",
                "tone": "amber",
            },
            {
                "title": "Connect",
                "body": "Route to a demo centre or schedule a home pickup.",
                "icon": "pin",
                "tone": "purple",
            },
        ]
    )

    ui.section_header(
        "Everything you need",
        "A complete circular flow, designed around your device",
        kicker="Features",
    )
    features = [
        {
            "title": "AI identification",
            "body": "Upload a photo or describe the device. Get a consistent recyclability score and a clear material breakdown.",
            "kicker": "Smart scan",
            "icon": "scan",
            "tone": "green",
            "page": "views/identify.py",
            "cta": "Try AI identification",
            "page_icon": ":material/document_scanner:",
        },
        {
            "title": "Smart recommendations",
            "body": "Compare reuse, repair, pickup and drop-off routes with impact estimates and preparation steps.",
            "kicker": "Best next step",
            "icon": "recommend",
            "tone": "blue",
            "page": "views/recommendations.py",
            "cta": "See smart routes",
            "page_icon": ":material/recommend:",
        },
        {
            "title": "Battery safety",
            "body": "Get clear handling guidance for swollen, damaged or ageing batteries before the device moves.",
            "kicker": "Safety first",
            "icon": "battery",
            "tone": "amber",
            "page": "views/identify.py",
            "cta": "Assess battery safety",
            "page_icon": ":material/battery_alert:",
        },
        {
            "title": "Nearby recycling centres",
            "body": "Find open drop-off points, accepted items, live capacity and directions across Bengaluru.",
            "kicker": "Local recovery",
            "icon": "map",
            "tone": "purple",
            "page": "views/map_view.py",
            "cta": "Find a centre",
            "page_icon": ":material/location_on:",
        },
    ]
    feature_cols = st.columns(2, gap="medium")
    for index, item in enumerate(features):
        with feature_cols[index % 2]:
            ui.feature_tile(item)

    about_col, principles_col = st.columns([1.15, 1], gap="medium")
    with about_col:
        tags = "".join(
            ui.pill(item, "outline")
            for item in ["Bengaluru-first", "Demo partners", "Transparent estimates", "Privacy-first"]
        )
        st.html(
            f"""
            <div class="rl-landing-about">
              <span class="rl-kicker">About ReLoop AI</span>
              <h2>Circular electronics should feel simple, safe and worth it.</h2>
              <p>
                ReLoop AI is a Bengaluru-first circular electronics platform. It turns an uncertain
                question — “what do I do with this old device?” — into a clear, responsible next step.
              </p>
              <p>
                We combine transparent assessments, verified local partners and practical safety
                guidance so more materials stay in circulation and fewer devices end up in landfill.
              </p>
              <div class="rl-landing-tags">{tags}</div>
            </div>
            """
        )
    with principles_col:
        with st.container(border=True):
            ui.section_header(
                "Our principles",
                "What guides every recommendation",
                kicker="About",
            )
            ui.insight_list(
                [
                    {
                        "title": "Transparent by design",
                        "body": "Every score, material estimate and route is explained in plain language.",
                        "icon": "info",
                        "tone": "green",
                    },
                    {
                        "title": "Safety first",
                        "body": "Battery handling and data-wiping guidance come before pickup or drop-off.",
                        "icon": "shield",
                        "tone": "amber",
                    },
                    {
                        "title": "Local recovery",
                        "body": "Devices go to demo Bengaluru partners with capacity today.",
                        "icon": "pin",
                        "tone": "blue",
                    },
                ]
            )

    st.html(
        """
        <div class="rl-landing-cta">
          <div>
            <span class="rl-kicker">Start today</span>
            <h2>Ready to give your electronics a second life?</h2>
            <p>Run a free assessment in under a minute, then choose the route that works for you.</p>
          </div>
        </div>
        """
    )
    cta_primary, cta_secondary, _ = st.columns([1, 1, 2.2], gap="small")
    with cta_primary:
        if st.button(
            "Identify Device",
            type="primary",
            icon=":material/document_scanner:",
            width="stretch",
        ):
            st.switch_page("views/identify.py")
    with cta_secondary:
        if st.button(
            "Get Started",
            icon=":material/rocket_launch:",
            width="stretch",
        ):
            st.switch_page("views/dashboard.py")

    ui.banner(
        "Built as a connected prototype",
        "Partners are fictional demo records. Assessments, routes and account data persist through the ReLoop API, while AI and impact values remain transparent estimates.",
        tone="green",
        icon_name="spark",
    )


render()
