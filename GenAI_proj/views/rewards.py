from __future__ import annotations

import streamlit as st

from components import ui
from data import mock_data as d
from utils.helpers import format_indian

if "points" not in st.session_state:
    st.session_state.points = d.USER["points"]
if "redemptions" not in st.session_state:
    st.session_state.redemptions = []


def render() -> None:
    flash = st.session_state.pop("flash", None)
    if flash:
        st.toast(flash)

    ui.page_header(
        "Rewards · Green Guardian",
        "Turn circular actions into real rewards",
        "Earn points for every verified drop-off, streak and referral. Redeem them for impact, lifestyle and tech rewards. All balances and rewards are mocked.",
    )

    ui.rewards_profile(d.USER, st.session_state.points)

    points = st.session_state.points
    earned_badges = sum(1 for badge in d.BADGES if badge["earned"])
    tier_progress = min(100, points / d.USER["next_tier_points"] * 100)
    ui.metric_grid(
        [
            {
                "label": "Available points",
                "value": format_indian(points),
                "delta": "+320",
                "direction": "up",
                "icon": "gift",
                "tone": "green",
                "note": "earned this month",
            },
            {
                "label": "Tier progress",
                "value": f"{tier_progress:.0f}%",
                "delta": d.USER["next_tier"],
                "direction": "up",
                "icon": "trophy",
                "tone": "amber",
                "note": "next tier target",
            },
            {
                "label": "Badges earned",
                "value": f"{earned_badges} / {len(d.BADGES)}",
                "icon": "award",
                "tone": "purple",
                "note": "keep collecting",
            },
            {
                "label": "Recycling streak",
                "value": f"{d.USER['streak_days']} days",
                "delta": "+4",
                "direction": "up",
                "icon": "zap",
                "tone": "blue",
                "note": "personal best: 18 days",
            },
        ]
    )

    redeem_tab, badges_tab, leaderboard_tab = st.tabs(["Redeem points", "Badges", "Leaderboard"])

    with redeem_tab:
        ui.section_header(
            "Rewards marketplace",
            "Spend points on things that keep the loop going",
            kicker="Redeem",
        )
        categories = ["All"] + sorted({reward["category"] for reward in d.REWARDS})
        selected_category = st.segmented_control(
            "Category",
            categories,
            default="All",
            label_visibility="collapsed",
        )
        if not selected_category:
            selected_category = "All"
        visible_rewards = [
            reward for reward in d.REWARDS if selected_category == "All" or reward["category"] == selected_category
        ]

        columns = st.columns(3, gap="medium")
        for index, reward in enumerate(visible_rewards):
            with columns[index % 3]:
                with st.container(border=True):
                    ui.reward_card(reward)
                    if st.button(
                        "Redeem",
                        key=f"redeem_{reward['title']}",
                        width="stretch",
                        disabled=points < reward["cost"],
                    ):
                        st.session_state.points -= reward["cost"]
                        st.session_state.redemptions.insert(
                            0,
                            {
                                "title": reward["title"],
                                "date": "Today",
                                "points": reward["cost"],
                                "status": "Processing",
                            },
                        )
                        st.session_state["flash"] = f"{reward['title']} redeemed for {reward['cost']} points."
                        st.rerun()

        with st.container(border=True):
            ui.section_header(
                "Redemption history",
                "Your recent rewards and their status",
                kicker="History",
            )
            ui.redemption_history(st.session_state.redemptions + d.REDEMPTION_HISTORY)

    with badges_tab:
        with st.container(border=True):
            ui.section_header(
                "Badge collection",
                f"{earned_badges} of {len(d.BADGES)} unlocked · keep recycling to earn more",
                kicker="Achievements",
            )
            ui.progress_bar("Badge completion", earned_badges, len(d.BADGES), "badges")

        for start in range(0, len(d.BADGES), 4):
            row = d.BADGES[start : start + 4]
            columns = st.columns(4, gap="medium")
            for column, badge in zip(columns, row):
                with column:
                    st.html(ui.badge_card(badge))

    with leaderboard_tab:
        leader_col, perk_col = st.columns([1.5, 1], gap="medium")
        with leader_col:
            with st.container(border=True):
                ui.section_header(
                    "Citywide leaderboard",
                    "Top recyclers in Bengaluru · November 2026",
                    kicker="Ranking",
                )
                ui.leaderboard(d.LEADERBOARD, d.USER["name"])
        with perk_col:
            with st.container(border=True):
                ui.section_header(
                    "Tier benefits",
                    "What Green Guardian unlocks",
                    kicker="Your tier",
                )
                ui.kv_list(
                    [
                        {"label": "Points multiplier", "value": "1.5×"},
                        {"label": "Free home pickups", "value": "2 / month"},
                        {"label": "Priority drop-off", "value": "Included"},
                        {"label": "Next tier", "value": d.USER["next_tier"]},
                        {"label": "Points remaining", "value": format_indian(d.USER["next_tier_points"] - points)},
                    ]
                )
                if st.button("Refer a friend", icon=":material/group_add:", width="stretch"):
                    st.toast("Referral link copied. This is a demo action.")

    ui.banner(
        "Rewards are mock data",
        "Points, badges, stock and redemption history are illustrative. No transaction or fulfilment is connected in Section 1.",
        tone="amber",
        icon_name="info",
    )


render()
