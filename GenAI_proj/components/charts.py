from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components import ui

COLORS = {
    "green": "#22A06B",
    "green_dark": "#187A52",
    "teal": "#2FBFA3",
    "lime": "#8FD3B0",
    "blue": "#6FA8DC",
    "amber": "#E0B45C",
    "coral": "#E08A77",
    "purple": "#A99BE8",
    "ink": "#F1F5F2",
    "muted": "#C5D0CA",
    "soft": "#91B5A0",
    "grid": "rgba(145,181,160,0.14)",
}

CATEGORY_COLORS = {
    "Smartphones": "#22A06B",
    "Laptops": "#2FBFA3",
    "Accessories": "#8FD3B0",
    "Home appliances": "#6FA8DC",
    "Tablets": "#E0B45C",
    "Other": "#4A6156",
}

MATERIAL_COLORS = ["#22A06B", "#2FBFA3", "#6FA8DC", "#8FD3B0", "#E0B45C", "#A99BE8", "#4A6156"]

PLOTLY_CONFIG = {"displayModeBar": False, "responsive": True}


def _base_layout(height: int) -> dict:
    return {
        "height": height,
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "Inter, Segoe UI, sans-serif", "color": COLORS["muted"], "size": 11},
        "margin": {"l": 6, "r": 6, "t": 26, "b": 6},
        "hoverlabel": {
            "bgcolor": "#0D1714",
            "bordercolor": "#2A3D34",
            "font": {"color": "#F1F5F2", "size": 11, "family": "Inter, Segoe UI, sans-serif"},
        },
        "showlegend": False,
        "xaxis": {
            "showgrid": False,
            "zeroline": False,
            "linecolor": "rgba(16,35,26,0)",
            "tickfont": {"size": 10, "color": COLORS["soft"]},
        },
        "yaxis": {
            "showgrid": True,
            "gridcolor": COLORS["grid"],
            "zeroline": False,
            "tickfont": {"size": 10, "color": COLORS["soft"]},
            "title": None,
        },
    }


def apply_theme(fig: go.Figure, height: int = 300) -> go.Figure:
    fig.update_layout(**_base_layout(height))
    return fig


def area_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    height: int = 320,
    color: str = COLORS["green"],
    suffix: str = " kg",
    fillcolor: str = "rgba(34,160,107,0.12)",
) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df[x],
            y=df[y],
            mode="lines",
            line={"color": color, "width": 3, "shape": "spline"},
            fill="tozeroy",
            fillcolor=fillcolor,
            hovertemplate=f"<b>%{{x}}</b><br>%{{y:,.0f}}{suffix}<extra></extra>",
            name=y,
        )
    )
    last = df.iloc[-1]
    fig.add_trace(
        go.Scatter(
            x=[last[x]],
            y=[last[y]],
            mode="markers",
            marker={"size": 9, "color": color, "line": {"color": "#172520", "width": 2}},
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.add_annotation(
        x=last[x],
        y=last[y],
        text=f"<b>{last[y]:,.0f}</b>",
        showarrow=False,
        yshift=18,
        font={"size": 11, "color": color, "family": "Sora, sans-serif"},
        bgcolor="rgba(23,37,32,0.94)",
        bordercolor="#2A3D34",
        borderpad=4,
    )
    apply_theme(fig, height)
    fig.update_xaxes(type="category")
    fig.update_yaxes(rangemode="tozero", nticks=5)
    return fig


def donut_chart(
    labels: list[str],
    values: list[float],
    center_label: str,
    center_value: str,
    height: int = 320,
    colors: list[str] | None = None,
) -> go.Figure:
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.68,
            sort=False,
            textinfo="none",
            marker={
                "colors": colors or MATERIAL_COLORS,
                "line": {"color": "#172520", "width": 2},
            },
            hovertemplate="<b>%{label}</b><br>%{value:,.0f} · %{percent}<extra></extra>",
        )
    )
    apply_theme(fig, height)
    fig.update_layout(
        margin={"l": 6, "r": 6, "t": 10, "b": 34},
        legend={
            "orientation": "h",
            "yanchor": "top",
            "y": -0.02,
            "xanchor": "center",
            "x": 0.5,
            "font": {"size": 10, "color": COLORS["muted"]},
        },
        showlegend=True,
    )
    fig.add_annotation(
        text=f"<b>{center_value}</b>",
        x=0.5,
        y=0.54,
        showarrow=False,
        font={"size": 22, "color": COLORS["ink"], "family": "Sora, sans-serif"},
    )
    fig.add_annotation(
        text=center_label,
        x=0.5,
        y=0.42,
        showarrow=False,
        font={"size": 10, "color": COLORS["muted"]},
    )
    return fig


def stacked_bar(
    df: pd.DataFrame,
    x: str,
    categories: list[str],
    height: int = 320,
    colors: dict[str, str] | None = None,
) -> go.Figure:
    palette = colors or CATEGORY_COLORS
    fig = go.Figure()
    for category in categories:
        fig.add_trace(
            go.Bar(
                x=df[x],
                y=df[category],
                name=category,
                marker={"color": palette.get(category, COLORS["soft"]), "line": {"width": 0}},
                hovertemplate=f"<b>%{{x}}</b><br>{category}: %{{y}}<extra></extra>",
            )
        )
    apply_theme(fig, height)
    fig.update_layout(
        barmode="stack",
        bargap=0.42,
        margin={"l": 6, "r": 6, "t": 32, "b": 6},
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
            "font": {"size": 10, "color": COLORS["muted"]},
        },
        showlegend=True,
    )
    fig.update_xaxes(type="category")
    fig.update_yaxes(nticks=4)
    return fig


def hbar_chart(
    labels: list[str],
    values: list[float],
    height: int = 320,
    color: str = COLORS["green"],
    highlight: str = COLORS["lime"],
    suffix: str = "",
) -> go.Figure:
    pairs = sorted(zip(labels, values), key=lambda item: item[1])
    sorted_labels = [pair[0] for pair in pairs]
    sorted_values = [pair[1] for pair in pairs]
    bar_colors = [color] * len(sorted_values)
    if bar_colors:
        bar_colors[-1] = highlight

    fig = go.Figure(
        go.Bar(
            x=sorted_values,
            y=sorted_labels,
            orientation="h",
            marker={"color": bar_colors, "line": {"width": 0}},
            text=[f"{value:,.0f}{suffix}" for value in sorted_values],
            textposition="outside",
            textfont={"size": 10, "color": COLORS["muted"]},
            hovertemplate=f"<b>%{{y}}</b><br>%{{x:,.0f}}{suffix}<extra></extra>",
        )
    )
    apply_theme(fig, height)
    fig.update_layout(
        margin={"l": 6, "r": 30, "t": 10, "b": 6},
        xaxis={"showgrid": True, "gridcolor": COLORS["grid"], "zeroline": False, "showticklabels": False},
        yaxis={"showgrid": False, "tickfont": {"size": 10, "color": COLORS["muted"]}},
    )
    fig.update_xaxes(range=[0, max(sorted_values) * 1.18])
    return fig


def gauge_chart(value: int, height: int = 250, title: str = "Circularity score") -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"suffix": "%", "font": {"size": 34, "color": COLORS["ink"], "family": "Sora, sans-serif"}},
            title={"text": title, "font": {"size": 11, "color": COLORS["muted"], "family": "Inter, sans-serif"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 0, "tickcolor": "rgba(0,0,0,0)", "showticklabels": False},
                "bar": {"color": COLORS["green"], "thickness": 0.32},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 40], "color": "#3A2723"},
                    {"range": [40, 60], "color": "#3A3320"},
                    {"range": [60, 80], "color": "#1C3A2D"},
                    {"range": [80, 100], "color": "#1D3B33"},
                ],
                "threshold": {
                    "line": {"color": COLORS["lime"], "width": 3},
                    "thickness": 0.8,
                    "value": value,
                },
            },
        )
    )
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin={"l": 18, "r": 18, "t": 42, "b": 4},
        font={"family": "Inter, Segoe UI, sans-serif", "color": COLORS["muted"]},
    )
    return fig


def chart_card(title: str, subtitle: str, fig: go.Figure, kicker: str = "") -> None:
    with st.container(border=True):
        ui.section_header(title, subtitle, kicker=kicker)
        st.plotly_chart(fig, width="stretch", theme=None, config=PLOTLY_CONFIG)
