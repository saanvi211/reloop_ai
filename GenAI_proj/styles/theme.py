from pathlib import Path

import streamlit as st

CSS_PATH = Path(__file__).resolve().parent.parent / "assets" / "styles.css"

ACCENTS = {
    "Emerald": {
        "green": "#22A06B",
        "dark": "#187A52",
        "soft": "rgba(34, 160, 107, 0.14)",
        "lime": "#8FD3B0",
    },
    "Forest": {
        "green": "#3E9E6E",
        "dark": "#2E8057",
        "soft": "rgba(62, 158, 110, 0.15)",
        "lime": "#A8D8B9",
    },
    "Teal": {
        "green": "#2FBFA3",
        "dark": "#249782",
        "soft": "rgba(47, 191, 163, 0.15)",
        "lime": "#9ADFD2",
    },
}


def load_css() -> None:
    css = CSS_PATH.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def apply_accent() -> None:
    accent = st.session_state.get("accent", "Emerald")
    colors = ACCENTS.get(accent, ACCENTS["Emerald"])
    st.markdown(
        "<style>:root {"
        f"--rl-green: {colors['green']};"
        f"--rl-green-dark: {colors['dark']};"
        f"--rl-green-soft: {colors['soft']};"
        f"--rl-lime: {colors['lime']};"
        "}</style>",
        unsafe_allow_html=True,
    )
