from __future__ import annotations

from html import escape

import folium
from folium.features import DivIcon

from data.mock_data import MAP_CENTER

TYPE_COLORS = {
    "Recycling Centre": "#22A06B",
    "Drop-off": "#2FBFA3",
    "Refurbisher": "#6FA8DC",
    "Kiosk": "#E0B45C",
    "Repair Shop": "#A99BE8",
}


def _pin_html(color: str) -> str:
    return f"""
    <div style="width:28px;height:28px;border-radius:50% 50% 50% 0;transform:rotate(-45deg);
        background:{color};border:3px solid #F1F5F2;box-shadow:0 4px 12px rgba(0,0,0,0.45);
        display:flex;align-items:center;justify-content:center;">
      <div style="width:9px;height:9px;border-radius:50%;background:#F1F5F2;transform:rotate(45deg);"></div>
    </div>
    """


def _popup_html(point: dict, color: str) -> str:
    accepted = " · ".join(escape(item) for item in point["accepted"])
    status = "Open now" if point["open_now"] else "Closed"
    status_color = "#8FD3B0" if point["open_now"] else "#91B5A0"
    directions = (
        f"https://www.google.com/maps/dir/?api=1&destination={point['lat']},{point['lon']}"
    )
    return f"""
    <div style="font-family:Inter,Segoe UI,sans-serif;width:232px;padding:2px 2px 4px;">
      <div style="font-size:10px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:{color};">
        {escape(point["type"])}
      </div>
      <div style="margin-top:3px;font-size:14px;font-weight:700;line-height:1.25;color:#F1F5F2;">
        {escape(point["name"])}
      </div>
      <div style="margin-top:5px;font-size:11px;line-height:1.5;color:#C5D0CA;">
        {escape(point["address"])}
      </div>
      <div style="margin-top:7px;font-size:11px;color:{status_color};font-weight:600;">
        {escape(status)} · {escape(point["hours"])}
      </div>
      <div style="margin-top:6px;font-size:10px;line-height:1.5;color:#91B5A0;">
        Accepts: {accepted}
      </div>
      <div style="margin-top:8px;padding-top:7px;border-top:1px solid #2A3D34;font-size:10px;color:#C5D0CA;">
        {point["distance_km"]} km away · {point["rating"]} rating
      </div>
      <a href="{escape(directions)}" target="_blank" rel="noopener"
         style="display:inline-block;margin-top:8px;font-size:11px;font-weight:700;color:#8FD3B0;text-decoration:none;">
        Get directions →
      </a>
    </div>
    """


def create_collection_map(points: list[dict], selected_name: str | None = None) -> folium.Map:
    selected = next((point for point in points if point["name"] == selected_name), None)
    center = (selected["lat"], selected["lon"]) if selected else MAP_CENTER
    zoom = 14 if selected else 11

    map_object = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles="OpenStreetMap",
        control_scale=True,
        prefer_canvas=True,
    )

    map_object.get_root().header.add_child(
        folium.Element(
            """
            <style>
              .leaflet-container { background:#0E1916; font-family:"Inter","Segoe UI",sans-serif; }
              .leaflet-tile-pane {
                filter: invert(1) hue-rotate(180deg) brightness(0.82) contrast(1.08) saturate(0.65);
              }
              .leaflet-popup-content-wrapper, .leaflet-popup-tip {
                background:#172520; color:#F1F5F2;
                border:1px solid #2A3D34;
                box-shadow:0 14px 34px rgba(0,0,0,0.5);
              }
              .leaflet-popup-content { margin:12px 14px; }
              .leaflet-popup-close-button { color:#C5D0CA !important; }
              .leaflet-control-zoom a {
                background:#172520 !important; color:#F1F5F2 !important;
                border-color:#2A3D34 !important;
              }
              .leaflet-control-zoom a:hover { background:#1B2E27 !important; }
              .leaflet-control-attribution {
                background:rgba(16,26,24,0.82) !important; color:#C5D0CA !important;
              }
              .leaflet-control-attribution a { color:#8FD3B0 !important; }
              .leaflet-control-scale-line {
                border-color:#91B5A0 !important; color:#C5D0CA !important;
                background:rgba(16,26,24,0.6) !important;
              }
              .leaflet-tooltip {
                background:#172520; color:#F1F5F2;
                border:1px solid #2A3D34; box-shadow:0 8px 20px rgba(0,0,0,0.4);
              }
              .leaflet-tooltip-top:before { border-top-color:#172520; }
              .leaflet-tooltip-bottom:before { border-bottom-color:#172520; }
              .leaflet-tooltip-left:before { border-left-color:#172520; }
              .leaflet-tooltip-right:before { border-right-color:#172520; }
            </style>
            """
        )
    )

    folium.CircleMarker(
        location=MAP_CENTER,
        radius=6,
        color="#F1F5F2",
        weight=2,
        fill=True,
        fill_color="#6FA8DC",
        fill_opacity=1.0,
        tooltip="Your approximate location",
    ).add_to(map_object)

    for point in points:
        color = TYPE_COLORS.get(point["type"], "#91B5A0")
        folium.Circle(
            location=(point["lat"], point["lon"]),
            radius=420,
            color=color,
            weight=0,
            fill=True,
            fill_opacity=0.10,
        ).add_to(map_object)
        folium.Marker(
            location=(point["lat"], point["lon"]),
            tooltip=folium.Tooltip(
                f"<b>{escape(point['name'])}</b><br>{escape(point['type'])} · {escape(point['area'])}",
                sticky=False,
            ),
            popup=folium.Popup(_popup_html(point, color), max_width=280),
            icon=DivIcon(
                icon_size=(34, 34),
                icon_anchor=(17, 34),
                html=_pin_html(color),
            ),
        ).add_to(map_object)

    if selected:
        folium.Circle(
            location=(selected["lat"], selected["lon"]),
            radius=900,
            color="#8FD3B0",
            weight=2,
            fill=True,
            fill_opacity=0.06,
        ).add_to(map_object)

    return map_object
