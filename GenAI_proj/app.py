import streamlit as st

from components import ui
from styles.theme import apply_accent, load_css
from utils import flow

st.set_page_config(
    page_title="ReLoop AI",
    page_icon="assets/logo_mark.svg",
    layout="wide",
    initial_sidebar_state="auto",
)

load_css()
user = flow.get_user()
if "accent" not in st.session_state:
    settings = {} if st.session_state.get("api_online") is False else flow.get_settings()
    st.session_state.accent = settings.get("accent", "Emerald")
apply_accent()
st.logo("assets/logo.svg", icon_image="assets/logo_mark.svg", size="large")

pages = {
    "Overview": [
        st.Page(
            "views/home.py",
            title="Home",
            icon=":material/home:",
            url_path="home",
            default=True,
        ),
        st.Page(
            "views/dashboard.py",
            title="Dashboard",
            icon=":material/space_dashboard:",
            url_path="dashboard",
        ),
    ],
    "Circular flow": [
        st.Page(
            "views/identify.py",
            title="Identify E-Waste",
            icon=":material/document_scanner:",
            url_path="identify",
        ),
        st.Page(
            "views/assessment.py",
            title="Assessment",
            icon=":material/fact_check:",
            url_path="assessment",
        ),
        st.Page(
            "views/recommendations.py",
            title="Recommendations",
            icon=":material/recommend:",
            url_path="recommendations",
        ),
        st.Page(
            "views/map_view.py",
            title="Nearby Centres",
            icon=":material/location_on:",
            url_path="nearby-centres",
        ),
    ],
    "Insights": [
        st.Page(
            "views/history.py",
            title="History",
            icon=":material/history:",
            url_path="history",
        ),
        st.Page(
            "views/analytics.py",
            title="Environmental Impact",
            icon=":material/monitoring:",
            url_path="environmental-impact",
        ),
    ],
    "Account": [
        st.Page(
            "views/rewards.py",
            title="Rewards",
            icon=":material/emoji_events:",
            url_path="rewards",
        ),
        st.Page(
            "views/about.py",
            title="About",
            icon=":material/info:",
            url_path="about",
        ),
        st.Page(
            "views/settings.py",
            title="Settings",
            icon=":material/settings:",
            url_path="settings",
        ),
    ],
}

navigation = st.navigation(pages, position="sidebar", expanded=True)
ui.sidebar_profile(user)
navigation.run()
ui.footer()
