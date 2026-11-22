from __future__ import annotations

import base64
from html import escape

import streamlit as st

from utils.helpers import format_indian, initials

ICONS = {
    "leaf": '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>',
    "recycle": '<path d="M7 19H4.815a1.83 1.83 0 0 1-1.57-.881 1.785 1.785 0 0 1-.004-1.784L7.196 9.5"/><path d="M11 19h8.203a1.83 1.83 0 0 0 1.556-.89 1.784 1.784 0 0 0 0-1.775l-1.226-2.12"/><path d="m14 16-3 3 3 3"/><path d="M8.293 13.596 7.196 9.5 3.1 10.598"/><path d="m9.344 5.811 1.093-1.892A1.83 1.83 0 0 1 11.985 3a1.784 1.784 0 0 1 1.546.888l3.943 6.843"/><path d="m13.378 9.633 4.096 1.098 1.097-4.096"/>',
    "cloud": '<path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/>',
    "cpu": '<rect width="16" height="16" x="4" y="4" rx="2"/><rect width="6" height="6" x="9" y="9" rx="1"/><path d="M15 2v2M15 20v2M2 15h2M2 9h2M20 15h2M20 9h2M9 2v2M9 20v2"/>',
    "gift": '<rect x="3" y="8" width="18" height="4" rx="1"/><path d="M12 8v13M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7"/><path d="M7.5 8a2.5 2.5 0 0 1 0-5A4.8 8 0 0 1 12 8a4.8 8 0 0 1 4.5-5 2.5 2.5 0 0 1 0 5"/>',
    "map": '<path d="M14.106 5.553a2 2 0 0 0 1.788 0l3.659-1.83A1 1 0 0 1 21 4.619v12.764a1 1 0 0 1-.553.894l-4.553 2.277a2 2 0 0 1-1.788 0l-4.212-2.106a2 2 0 0 0-1.788 0l-3.659 1.83A1 1 0 0 1 3 19.381V6.618a1 1 0 0 1 .553-.894l4.553-2.277a2 2 0 0 1 1.788 0z"/><path d="M15 5.764v15"/><path d="M9 3.236v15"/>',
    "chart": '<path d="M3 3v16a2 2 0 0 0 2 2h16"/><path d="m19 9-5 5-4-4-3 3"/>',
    "spark": '<path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>',
    "arrow-up-right": '<path d="M7 7h10v10"/><path d="M7 17 17 7"/>',
    "arrow-down-right": '<path d="m7 7 10 10"/><path d="M17 7v10H7"/>',
    "arrow-right": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "pin": '<path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
    "battery": '<rect width="16" height="10" x="2" y="7" rx="2"/><line x1="22" x2="22" y1="11" y2="13"/><line x1="6" x2="6" y1="11" y2="13"/><line x1="10" x2="10" y1="11" y2="13"/><line x1="14" x2="14" y1="11" y2="13"/>',
    "laptop": '<path d="M18 5a2 2 0 0 1 2 2v8.526a2 2 0 0 0 .212.897l1.068 2.127a1 1 0 0 1-.9 1.45H3.62a1 1 0 0 1-.9-1.45l1.068-2.127A2 2 0 0 0 4 15.526V7a2 2 0 0 1 2-2z"/><path d="M2 16h20"/>',
    "phone": '<rect width="14" height="20" x="5" y="2" rx="2" ry="2"/><path d="M12 18h.01"/>',
    "monitor": '<rect width="20" height="14" x="2" y="3" rx="2"/><line x1="8" x2="16" y1="21" y2="21"/><line x1="12" x2="12" y1="17" y2="21"/>',
    "truck": '<path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/>',
    "trophy": '<path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "upload": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "info": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
    "calendar": '<path d="M8 2v4M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/>',
    "zap": '<path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "award": '<path d="m15.477 12.89 1.515 8.526a.5.5 0 0 1-.81.47l-3.58-2.687a1 1 0 0 0-1.197 0l-3.586 2.686a.5.5 0 0 1-.81-.469l1.514-8.526"/><circle cx="12" cy="8" r="6"/>',
    "lock": '<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "package": '<path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>',
    "refresh": '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>',
    "star": '<path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"/>',
    "scan": '<path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/><path d="M7 12h10"/>',
    "fact_check": '<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>',
    "recommend": '<path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3z"/><path d="M7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/>',
    "history": '<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l4 2"/>',
    "monitoring": '<path d="M3 3v16a2 2 0 0 0 2 2h16"/><path d="m19 9-5 5-4-4-3 3"/>',
}

TYPE_TONES = {
    "Recycling Centre": "green",
    "Drop-off": "teal",
    "Refurbisher": "blue",
    "Kiosk": "amber",
    "Repair Shop": "purple",
}


def _e(value: object) -> str:
    return escape(str(value))


def icon(name: str, size: int = 18) -> str:
    body = ICONS.get(name, ICONS["spark"])
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>'
    )


def hero(
    eyebrow: str,
    title: str,
    accent: str,
    subtitle: str,
    chips: list[dict],
    ring_value: int,
    ring_label: str,
) -> None:
    chips_html = "".join(
        f'<span class="rl-hero-chip">{icon(chip.get("icon", "spark"), 14)}{_e(chip["text"])}</span>'
        for chip in chips
    )
    st.html(
        f"""
        <div class="rl-hero">
          <div class="rl-hero-copy">
            <div class="rl-eyebrow"><span class="rl-dot"></span>{_e(eyebrow)}</div>
            <h1>{_e(title)} <br><span>{_e(accent)}</span></h1>
            <p>{_e(subtitle)}</p>
            <div class="rl-hero-chips">{chips_html}</div>
          </div>
          <div class="rl-hero-ring" style="--value:{int(ring_value)}">
            <div class="rl-ring-inner"><span>{int(ring_value)}%</span><small>{_e(ring_label)}</small></div>
          </div>
        </div>
        """,
    )


def page_header(kicker: str, title: str, subtitle: str) -> None:
    st.html(
        f"""
        <div class="rl-page-header">
          <span class="rl-kicker">{_e(kicker)}</span>
          <h1>{_e(title)}</h1>
          <p>{_e(subtitle)}</p>
        </div>
        """,
    )


def section_header(title: str, subtitle: str = "", kicker: str = "") -> None:
    kicker_html = f'<span class="rl-section-kicker">{_e(kicker)}</span>' if kicker else ""
    subtitle_html = f"<p>{_e(subtitle)}</p>" if subtitle else ""
    st.html(
        f"""
        <div class="rl-section-head">
          <div>{kicker_html}<h3>{_e(title)}</h3>{subtitle_html}</div>
        </div>
        """,
    )


def feature_card(item: dict) -> None:
    st.html(
        f"""
        <div class="rl-feature-body">
          <span class="rl-feature-icon {_e(item.get("tone", ""))}">{icon(item.get("icon", "spark"), 20)}</span>
          <span class="rl-feature-kicker">{_e(item.get("kicker", ""))}</span>
          <h4>{_e(item["title"])}</h4>
          <p>{_e(item["body"])}</p>
        </div>
        """,
    )


def feature_tile(item: dict) -> None:
    with st.container(border=True):
        feature_card(item)
        st.page_link(
            item["page"],
            label=item.get("cta", "Open"),
            icon=item.get("page_icon", ":material/arrow_forward:"),
        )


def flow_rail(steps: list[dict], active: int) -> None:
    rows = []
    for index, step in enumerate(steps, start=1):
        state = "done" if index < active else "active" if index == active else ""
        marker = icon("check", 13) if index < active else str(index)
        rows.append(
            f"""
            <div class="rl-flow-step {state}">
              <span class="rl-flow-num">{marker}</span>
              <div><strong>{_e(step["title"])}</strong><span>{_e(step["body"])}</span></div>
            </div>
            """
        )
    st.html(f'<div class="rl-flow-rail">{"".join(rows)}</div>')


def how_it_works(steps: list[dict]) -> None:
    rows = []
    for index, step in enumerate(steps, start=1):
        rows.append(
            f"""
            <div class="rl-how-step">
              <span class="rl-how-num">{index:02d}</span>
              <span class="rl-how-icon {_e(step.get("tone", ""))}">{icon(step.get("icon", "spark"), 20)}</span>
              <strong>{_e(step["title"])}</strong>
              <p>{_e(step["body"])}</p>
            </div>
            """
        )
        if index < len(steps):
            rows.append(f'<span class="rl-how-arrow">{icon("arrow-right", 18)}</span>')
    st.html(f'<div class="rl-how">{"".join(rows)}</div>')


def metric_grid(items: list[dict]) -> None:
    cards = []
    for item in items:
        direction = item.get("direction", "up")
        delta = item.get("delta")
        if delta:
            trend_icon = "arrow-up-right" if direction == "up" else "arrow-down-right"
            if direction == "flat":
                trend_icon = "arrow-right"
            trend = (
                f'<span class="rl-trend {_e(direction)}">{icon(trend_icon, 12)}{_e(delta)}</span>'
            )
        else:
            trend = ""
        note = item.get("note")
        note_html = f'<div class="rl-metric-note">{_e(note)}</div>' if note else ""
        cards.append(
            f"""
            <div class="rl-metric">
              <div class="rl-metric-top">
                <span class="rl-icon {_e(item.get("tone", ""))}">{icon(item.get("icon", "spark"))}</span>
                {trend}
              </div>
              <div class="rl-metric-value">{_e(item["value"])}</div>
              <div class="rl-metric-label">{_e(item["label"])}</div>
              {note_html}
            </div>
            """
        )
    st.html(f'<div class="rl-metric-grid">{"".join(cards)}</div>')


def pill(text: str, tone: str = "green") -> str:
    return f'<span class="rl-pill {_e(tone)}">{_e(text)}</span>'


def pills(items: list[str], tone: str = "outline") -> str:
    return "".join(pill(item, tone) for item in items)


def activity_list(items: list[dict]) -> None:
    rows = []
    for item in items:
        points = item.get("points", "")
        points_class = " negative" if str(points).startswith("-") else ""
        points_html = (
            f'<span class="rl-activity-points{points_class}">{_e(points)}</span>' if points else ""
        )
        rows.append(
            f"""
            <div class="rl-activity-item">
              <span class="rl-activity-icon {_e(item.get("tone", ""))}">{icon(item.get("icon", "spark"), 16)}</span>
              <div class="rl-activity-body">
                <div class="rl-activity-title">{_e(item["title"])}</div>
                <div class="rl-activity-sub">{_e(item["detail"])}</div>
              </div>
              <div class="rl-activity-meta">
                {points_html}
                <span class="rl-activity-time">{_e(item["time"])}</span>
              </div>
            </div>
            """
        )
    st.html(f'<div class="rl-activity">{"".join(rows)}</div>')


def progress_bar(label: str, current: float, target: float, unit: str = "", tone: str = "") -> None:
    pct = min(100.0, (current / target) * 100) if target else 0.0
    st.html(
        f"""
        <div class="rl-progress">
          <div class="rl-progress-head"><span>{_e(label)}</span><strong>{pct:.1f}%</strong></div>
          <div class="rl-progress-track"><div class="rl-progress-fill {_e(tone)}" style="width:{pct:.1f}%"></div></div>
          <div class="rl-progress-foot"><span><strong>{_e(format_indian(current))} {_e(unit)}</strong> completed</span><span>Goal {_e(format_indian(target))} {_e(unit)}</span></div>
        </div>
        """,
    )


def goal_meta(items: list[dict]) -> None:
    cards = "".join(
        f'<div><span>{_e(item["label"])}</span><strong>{_e(item["value"])}</strong></div>'
        for item in items
    )
    st.html(f'<div class="rl-goal-meta">{cards}</div>')


def pickup_card(pickup: dict) -> None:
    st.html(
        f"""
        <div class="rl-pickup">
          <div class="rl-pickup-date"><span>{_e(pickup["day"])}</span><small>{_e(pickup["month"])}</small></div>
          <div class="rl-pickup-info">
            <strong>{_e(pickup["title"])}</strong>
            <span>{_e(pickup["when"])}</span>
            <span>{_e(pickup["partner"])}</span>
          </div>
          {pill(pickup["status"], "green")}
        </div>
        """,
    )


def collection_card(point: dict) -> None:
    tone = TYPE_TONES.get(point["type"], "neutral")
    capacity = int(point["capacity"])
    capacity_tone = "amber" if capacity >= 70 else ""
    directions = (
        f"https://www.google.com/maps/dir/?api=1&destination={point['lat']},{point['lon']}"
    )
    open_pill = pill("Open now", "green") if point["open_now"] else pill("Closed", "neutral")
    accepted = "".join(pill(item, "outline") for item in point["accepted"])
    phone = point.get("phone", "")
    email = point.get("email", "")
    contact = ""
    if phone or email:
        contact = (
            '<div class="rl-center-contact">'
            + (f'<span>{icon("phone", 13)}{_e(phone)}</span>' if phone else "")
            + (f'<span>{icon("info", 13)}{_e(email)}</span>' if email else "")
            + "</div>"
        )
    st.html(
        f"""
        <div class="rl-center">
          <div class="rl-center-head">
            <div>
              <div class="rl-center-name">{_e(point["name"])}</div>
              <div class="rl-center-address">{_e(point["address"])}</div>
            </div>
            {pill(point["type"], tone)}
          </div>
          <div class="rl-center-meta">
            <span>{icon("clock", 13)}{_e(point["hours"])}</span>
            <span>{icon("pin", 13)}{_e(point["area"])} · {point["distance_km"]} km</span>
            <span>{icon("star", 13)}{point["rating"]}</span>
            {open_pill}
          </div>
          <div class="rl-center-speciality">{icon("spark", 13)}{_e(point.get("speciality", "E-waste drop-off and material recovery"))}</div>
          <div class="rl-chips">{accepted}</div>
          {contact}
          <div class="rl-center-foot">
            <div class="rl-capacity">
              <div class="rl-progress-track"><div class="rl-progress-fill {capacity_tone}" style="width:{capacity}%"></div></div>
              <span>{capacity}% capacity</span>
            </div>
            <a class="rl-directions" href="{_e(directions)}" target="_blank" rel="noopener">Directions {icon("arrow-up-right", 12)}</a>
          </div>
        </div>
        """,
    )


def reward_card(reward: dict) -> None:
    st.html(
        f"""
        <div class="rl-reward-head">
          <span class="rl-reward-icon">{icon(reward.get("icon", "gift"), 19)}</span>
          {pill(reward["category"], "neutral")}
        </div>
        <div class="rl-reward-title">{_e(reward["title"])}</div>
        <div class="rl-reward-desc">{_e(reward["description"])}</div>
        <div class="rl-reward-foot">
          <strong>{_e(format_indian(reward["cost"]))} <small>pts</small></strong>
          <span>{_e(reward["stock"])} left</span>
        </div>
        """,
    )


def badge_card(badge: dict) -> str:
    state = "Earned" if badge["earned"] else "Locked"
    locked = "" if badge["earned"] else " locked"
    return f"""
    <div class="rl-badge-card{locked}">
      <span class="rl-badge-icon">{icon(badge["icon"], 21)}</span>
      <div class="rl-badge-name">{_e(badge["name"])}</div>
      <div class="rl-badge-desc">{_e(badge["description"])}</div>
      <span class="rl-badge-state">{_e(state)} · {_e(badge["rarity"])}</span>
    </div>
    """


def leaderboard(rows: list[dict], current_name: str = "") -> None:
    html_rows = []
    for row in rows:
        current = " current" if row["name"] == current_name else ""
        you = "<span>You</span>" if row["name"] == current_name else ""
        html_rows.append(
            f"""
            <div class="rl-leader-row{current}">
              <span class="rl-rank">{row["rank"]}</span>
              <span class="rl-avatar">{_e(initials(row["name"]))}</span>
              <span class="rl-leader-name">{_e(row["name"])}{you}</span>
              <span class="rl-leader-kg">{_e(format_indian(row["kg"]))} kg</span>
              <span class="rl-leader-pts">{_e(format_indian(row["points"]))}</span>
            </div>
            """
        )
    st.html(f'<div class="rl-leaderboard">{"".join(html_rows)}</div>')


def insight_list(items: list[dict]) -> None:
    cards = []
    for item in items:
        cards.append(
            f"""
            <div class="rl-insight">
              <span class="rl-insight-icon {_e(item.get("tone", ""))}">{icon(item.get("icon", "spark"), 17)}</span>
              <div>
                <strong>{_e(item["title"])}</strong>
                <p>{_e(item["body"])}</p>
              </div>
            </div>
            """
        )
    st.html("".join(cards))


def banner(title: str, body: str, tone: str = "green", icon_name: str = "info") -> None:
    st.html(
        f"""
        <div class="rl-banner {_e(tone)}">
          <span class="rl-banner-icon">{icon(icon_name, 17)}</span>
          <div><strong>{_e(title)}</strong><span>{_e(body)}</span></div>
        </div>
        """,
    )


def steps(items: list[dict]) -> None:
    rows = []
    for index, item in enumerate(items, start=1):
        rows.append(
            f"""
            <div class="rl-step">
              <span class="rl-step-num">{index}</span>
              <div><strong>{_e(item["title"])}</strong><p>{_e(item["body"])}</p></div>
            </div>
            """
        )
    st.html(f'<div class="rl-steps">{"".join(rows)}</div>')


def result_hero(result: dict) -> None:
    band = result["band"]
    st.html(
        f"""
        <div class="rl-result-hero">
          <div class="rl-result-score" style="--value:{result["score"]}; --score-color:{band["color"]}">
            <div class="rl-result-score-inner"><strong>{result["score"]}</strong><small>/100</small></div>
          </div>
          <div class="rl-result-copy">
            <span class="rl-pill green">{_e(band["label"])} recyclability</span>
            <h3>{_e(result["device"])} · {_e(result["condition"])}</h3>
            <p>Mock estimate generated from device type, condition and age. No model is connected yet.</p>
            <div class="rl-result-stats">
              <div class="rl-result-stat"><span>Est. value</span><strong>₹{_e(format_indian(result["estimated_value"]))}</strong></div>
              <div class="rl-result-stat"><span>Weight</span><strong>{result["weight_kg"]} kg</strong></div>
              <div class="rl-result-stat"><span>CO₂ avoided</span><strong>{result["co2_kg"]} kg</strong></div>
              <div class="rl-result-stat"><span>Recoverable</span><strong>{result["recyclable_kg"]} kg</strong></div>
            </div>
          </div>
        </div>
        """,
    )


def guidance_list(items: list[str]) -> None:
    rows = "".join(
        f'<div class="rl-guidance-item">{icon("check", 15)}<span>{_e(item)}</span></div>' for item in items
    )
    st.html(f'<div class="rl-guidance">{rows}</div>')


def warning_list(items: list[str]) -> None:
    rows = "".join(
        f'<div class="rl-warning-item">{icon("shield", 15)}<span>{_e(item)}</span></div>' for item in items
    )
    st.html(f'<div class="rl-warnings">{rows}</div>')


def material_rows(materials: dict) -> None:
    rows = []
    for material, share in sorted(materials.items(), key=lambda item: item[1], reverse=True):
        rows.append(
            f"""
            <div class="rl-material-row">
              <span>{_e(material)}</span>
              <div class="rl-material-bar"><i style="width:{int(share)}%"></i></div>
              <strong>{int(share)}%</strong>
            </div>
            """
        )
    st.html("".join(rows))


def kv_list(items: list[dict]) -> None:
    rows = "".join(
        f'<div class="rl-kv"><span>{_e(item["label"])}</span><strong>{_e(item["value"])}</strong></div>'
        for item in items
    )
    st.html(rows)


def timeline(items: list[dict]) -> None:
    rows = []
    for item in items:
        rows.append(
            f"""
            <div class="rl-timeline-item {_e(item["state"])}">
              <span class="rl-timeline-dot"></span>
              <span class="rl-timeline-period">{_e(item["period"])}</span>
              <strong>{_e(item["title"])}</strong>
              <p>{_e(item["body"])}</p>
            </div>
            """
        )
    st.html(f'<div class="rl-timeline">{"".join(rows)}</div>')


def rewards_profile(user: dict, points: int) -> None:
    pct = min(100.0, points / user["next_tier_points"] * 100) if user["next_tier_points"] else 0.0
    remaining = max(0, user["next_tier_points"] - points)
    st.html(
        f"""
        <div class="rl-profile-card">
          <div class="rl-profile-main">
            <span class="rl-profile-avatar">{_e(user["initials"])}</span>
            <div>
              <div class="rl-profile-name">{_e(user["name"])}</div>
              <div class="rl-profile-tier">{_e(user["tier"])} · Member since {_e(user["member_since"])}</div>
            </div>
          </div>
          <div class="rl-profile-points">
            <span>Available points</span>
            <strong>{_e(format_indian(points))}</strong>
          </div>
          <div class="rl-profile-progress">
            <div class="rl-progress-track"><div class="rl-progress-fill" style="width:{pct:.1f}%"></div></div>
            <span>{_e(format_indian(remaining))} pts to {_e(user["next_tier"])}</span>
          </div>
        </div>
        """,
    )


def redemption_history(items: list[dict]) -> None:
    rows = []
    for item in items:
        status_tone = "green" if item["status"] in {"Delivered", "Planted", "Used", "Confirmed"} else "amber"
        rows.append(
            f"""
            <div class="rl-history-row">
              <div class="rl-history-title">{_e(item["title"])}<span>{_e(item["date"])}</span></div>
              <div class="rl-history-points">-{_e(format_indian(item["points"]))} pts</div>
              {pill(item["status"], status_tone)}
            </div>
            """
        )
    st.html(f'<div class="rl-history">{"".join(rows)}</div>')


def history_list(items: list[dict]) -> None:
    status_tones = {
        "Completed": "green",
        "Scheduled": "blue",
        "Processing": "amber",
        "In transit": "teal",
    }
    rows = []
    for item in items:
        tone = status_tones.get(item["status"], "neutral")
        points = item.get("points", 0)
        points_html = (
            f'<span class="rl-record-points">+{_e(format_indian(points))} pts</span>'
            if points
            else '<span class="rl-record-points muted">Pending</span>'
        )
        image = item.get("image")
        if image:
            encoded = base64.b64encode(image).decode("ascii")
            thumbnail = (
                f'<span class="rl-record-icon thumb"><img src="data:image/png;base64,{encoded}" alt=""></span>'
            )
        else:
            thumbnail = (
                f'<span class="rl-record-icon {_e(item.get("tone", ""))}">'
                f'{icon(item.get("icon", "cpu"), 18)}</span>'
            )
        pathway = item.get("pathway")
        pathway_html = pill(pathway, "outline") if pathway else ""
        rows.append(
            f"""
            <div class="rl-record">
              {thumbnail}
              <div class="rl-record-main">
                <div class="rl-record-title">{_e(item["device"])}<span>{_e(item["detail"])}</span></div>
                <div class="rl-record-meta">
                  <span>{icon("calendar", 12)}{_e(item["date"])}</span>
                  <span>{icon("pin", 12)}{_e(item["partner"])}</span>
                </div>
              </div>
              <div class="rl-record-impact">
                <strong>{item["weight_kg"]} kg</strong>
                <span>{item["co2_kg"]} kg CO₂</span>
              </div>
              <div class="rl-record-side">
                {pathway_html}
                {pill(item["status"], tone)}
                {points_html}
              </div>
            </div>
            """
        )
    st.html(f'<div class="rl-record-list">{"".join(rows)}</div>')


def prediction_rows(predictions: list[dict]) -> None:
    rows = []
    for item in predictions:
        pct = int(round(item["confidence"] * 100))
        label = item.get("label")
        category = item["category"]
        if label and label != category:
            display_name = f"{label} ({category})"
        else:
            display_name = category
        rows.append(
            f"""
            <div class="rl-predict-row">
              <div class="rl-predict-head"><span>{_e(display_name)}</span><strong>{pct}%</strong></div>
              <div class="rl-progress-track"><div class="rl-progress-fill" style="width:{pct}%"></div></div>
            </div>
            """
        )
    st.html(f'<div class="rl-predict">{"".join(rows)}</div>')


def pathway_rank_rows(ranked: list[dict]) -> None:
    rows = []
    for index, item in enumerate(ranked, start=1):
        meta = {"Repair": "green", "Refurbish & Resell": "blue", "Harvest Components": "amber", "Recycle": "teal", "Hazardous Handling": "coral"}
        tone = meta.get(item["pathway"], "neutral")
        score = int(item.get("score", 0))
        eligible = item.get("eligible", True)
        state = "" if eligible else " blocked"
        rows.append(
            f"""
            <div class="rl-path-rank{state}">
              <span class="rl-path-num">{index:02d}</span>
              <div class="rl-path-body">
                <div class="rl-path-head"><strong>{_e(item["pathway"])}</strong>{pill("Eligible", tone) if eligible else pill("Blocked", "coral")}</div>
                <div class="rl-progress-track"><div class="rl-progress-fill" style="width:{score}%"></div></div>
                <p>{_e(item["reason"])}</p>
              </div>
              <span class="rl-path-score">{score}</span>
            </div>
            """
        )
    st.html(f'<div class="rl-path-ranks">{"".join(rows)}</div>')


def answer_grid(items: list[dict]) -> None:
    cards = "".join(
        f'<div class="rl-answer"><span>{_e(item["label"])}</span><strong>{_e(item["value"])}</strong></div>'
        for item in items
    )
    st.html(f'<div class="rl-answer-grid">{cards}</div>')


def empty_state(title: str, body: str, icon_name: str = "search") -> None:
    st.html(
        f"""
        <div class="rl-empty">
          <span class="rl-empty-icon">{icon(icon_name, 21)}</span>
          <strong>{_e(title)}</strong>
          <p>{_e(body)}</p>
        </div>
        """,
    )


def sidebar_profile(user: dict) -> None:
    if user.get("api"):
        note = (
            "<strong>Connected prototype</strong>"
            "Your account, assessments and history are stored by the ReLoop API. "
            "Classification and impact values are still estimates."
        )
    else:
        note = (
            "<strong>Offline demo mode</strong>"
            "The ReLoop API is not reachable, so local demo data is shown. "
            "Start the backend to persist new records."
        )
    st.sidebar.html(
        f"""
        <div class="rl-side-profile">
          <span class="rl-side-avatar">{_e(user["initials"])}</span>
          <div><div class="rl-side-name">{_e(user["name"])}</div><div class="rl-side-tier">{_e(user["tier"])}</div></div>
        </div>
        <div class="rl-side-stats">
          <div class="rl-side-stat"><span>{_e(format_indian(user["points"]))}</span><small>POINTS</small></div>
          <div class="rl-side-stat"><span>{user["streak_days"]} days</span><small>STREAK</small></div>
        </div>
        <div class="rl-side-note">{note}</div>
        """,
    )


def footer() -> None:
    st.html(
        f"""
        <div class="rl-footer">
          <span class="rl-footer-brand">{icon("recycle", 18)}ReLoop AI</span>
          <p>Give your electronics a second life.</p>
          <div class="rl-footer-meta"><span>Bengaluru</span><span>Prototype · mock data</span><span>2026</span></div>
        </div>
        """,
    )
