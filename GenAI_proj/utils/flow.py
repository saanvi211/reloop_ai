from __future__ import annotations

import copy
import time

import streamlit as st

from data import mock_data as d
from utils import api_client
from utils.helpers import category_group, device_icon

ASSESSMENT_KEY = "identify_result"
HISTORY_KEY = "recycling_history"
SAVED_KEY = "assessment_saved"
IDENTIFICATION_KEY = "identify_detection"
PHOTO_KEY = "identify_photo"
ANSWERS_KEY = "assessment_answers"
RECOMMENDATION_KEY = "recommendation_result"


def get_identification() -> dict | None:
    return st.session_state.get(IDENTIFICATION_KEY)


def save_identification(result: dict) -> None:
    st.session_state[IDENTIFICATION_KEY] = result


def clear_identification() -> None:
    st.session_state.pop(IDENTIFICATION_KEY, None)


def get_photo() -> dict | None:
    return st.session_state.get(PHOTO_KEY)


def save_photo(data: bytes, name: str) -> None:
    st.session_state[PHOTO_KEY] = {"data": data, "name": name}


def clear_photo() -> None:
    st.session_state.pop(PHOTO_KEY, None)


def get_answers() -> dict:
    return st.session_state.get(ANSWERS_KEY, {})


def save_answers(answers: dict) -> None:
    st.session_state[ANSWERS_KEY] = answers


def clear_answers() -> None:
    st.session_state.pop(ANSWERS_KEY, None)


def reset_flow() -> None:
    for key in [ASSESSMENT_KEY, IDENTIFICATION_KEY, PHOTO_KEY, ANSWERS_KEY, SAVED_KEY, RECOMMENDATION_KEY]:
        st.session_state.pop(key, None)


def get_assessment() -> dict | None:
    return st.session_state.get(ASSESSMENT_KEY)


def save_assessment(result: dict) -> None:
    st.session_state[ASSESSMENT_KEY] = result
    st.session_state.pop(SAVED_KEY, None)
    st.session_state.pop(RECOMMENDATION_KEY, None)


def clear_assessment() -> None:
    st.session_state.pop(ASSESSMENT_KEY, None)
    st.session_state.pop(SAVED_KEY, None)
    st.session_state.pop(RECOMMENDATION_KEY, None)


def get_recommendation() -> dict | None:
    return st.session_state.get(RECOMMENDATION_KEY)


def save_recommendation(result: dict) -> None:
    st.session_state[RECOMMENDATION_KEY] = result


def is_assessment_saved() -> bool:
    return bool(st.session_state.get(SAVED_KEY))


def mark_assessment_saved() -> None:
    st.session_state[SAVED_KEY] = True


def _normalise_history_item(item: dict) -> dict:
    entry = dict(item)
    entry.setdefault("category", category_group(entry.get("device", "")))
    entry.setdefault("pathway", "Recycle")
    entry.setdefault("image", None)
    entry.setdefault("image_url", None)
    entry.setdefault("image_name", "")
    entry.setdefault("battery_condition", "Normal")
    entry.setdefault("notes", "Recovery record from the ReLoop demo network.")
    return entry


def _fallback_history() -> list[dict]:
    return [
        _normalise_history_item(copy.deepcopy(item))
        for item in d.RECYCLING_HISTORY
    ]


def get_history(force: bool = False) -> list[dict]:
    cached = st.session_state.get(HISTORY_KEY)
    if not force and cached:
        return cached
    try:
        payload = api_client.list_history(limit=100)
        items = [_normalise_history_item(item) for item in payload.get("items", [])]
        st.session_state[HISTORY_KEY] = items
        st.session_state["history_source"] = "api"
        return items
    except api_client.ApiError:
        if cached:
            return cached
        st.session_state[HISTORY_KEY] = _fallback_history()
        st.session_state["history_source"] = "local"
        return st.session_state[HISTORY_KEY]


def _normalise_user(raw: dict | None) -> dict:
    source = raw or {}
    name = source.get("name") or d.USER["name"]
    parts = [part for part in name.split() if part]
    user = dict(d.USER)
    user.update(
        {
            "name": name,
            "first_name": parts[0] if parts else d.USER["first_name"],
            "initials": "".join(part[0].upper() for part in parts[:2]) or d.USER["initials"],
            "email": source.get("email") or d.USER["email"],
            "tier": source.get("tier") or d.USER["tier"],
            "points": int(source.get("points", d.USER["points"])),
            "streak_days": int(source.get("streak_days", d.USER["streak_days"])),
            "member_since": source.get("member_since") or d.USER["member_since"],
            "city": source.get("city") or d.USER["city"],
            "id": source.get("id"),
            "profile": source.get("profile"),
            "api": bool(source.get("id")),
        }
    )
    return user


def get_user(force: bool = False) -> dict:
    cache = st.session_state.get("user_cache")
    if not force and cache and time.time() - cache.get("loaded_at", 0) < 60:
        return cache["value"]
    try:
        raw = api_client.get_user()
    except api_client.ApiError:
        raw = st.session_state.get("api_user")
    value = _normalise_user(raw)
    st.session_state["user_cache"] = {"value": value, "loaded_at": time.time()}
    return value


def refresh_user() -> dict:
    st.session_state.pop("user_cache", None)
    return get_user(force=True)


def _normalise_settings(raw: dict | None) -> dict:
    settings = dict(d.USER_PREFERENCES)
    settings.update(
        {key: value for key, value in (raw or {}).items() if value is not None}
    )
    settings.setdefault("accent", "Emerald")
    return settings


def get_settings(force: bool = False) -> dict:
    cache = st.session_state.get("settings_cache")
    if not force and cache and time.time() - cache.get("loaded_at", 0) < 60:
        return cache["value"]
    try:
        raw = api_client.get_settings()
        value = _normalise_settings(raw)
        value["api"] = True
    except api_client.ApiError:
        value = _normalise_settings(st.session_state.get("preferences"))
        value["api"] = False
    st.session_state["settings_cache"] = {"value": value, "loaded_at": time.time()}
    return value


def save_settings(payload: dict, *, force: bool = False) -> dict:
    try:
        raw = api_client.update_settings(payload)
        value = _normalise_settings(raw)
        value["api"] = True
    except api_client.ApiError as exc:
        if not exc.offline:
            raise
        current = get_settings(force=True)
        current.update(payload)
        value = current
        value["api"] = False
    st.session_state["settings_cache"] = {"value": value, "loaded_at": time.time()}
    st.session_state["preferences"] = value
    return value


def history_image(item: dict) -> bytes | None:
    image = item.get("image")
    if image:
        return image
    path = item.get("image_url")
    if not path:
        return None
    cache_key = f"history_image_{item.get('id') or path}"
    cached = st.session_state.get(cache_key)
    if cached is not None:
        return cached
    try:
        data = api_client.fetch_image(path)
    except api_client.ApiError:
        return None
    if data:
        st.session_state[cache_key] = data
    return data


def _local_history_entry(
    result: dict,
    partner: str,
    status: str,
    points: int | None,
    pathway: str | None,
    notes: str | None,
) -> dict:
    detail = " ".join(
        part
        for part in [result.get("brand", ""), result.get("model", "")]
        if part and part != "Not specified"
    ) or result.get("condition", "Device assessment")
    tone = {
        "Completed": "green",
        "Scheduled": "blue",
        "Processing": "amber",
        "In transit": "teal",
    }.get(status, "green")
    photo = get_photo()
    entry = {
        "date": "Today",
        "device": result["device"],
        "detail": detail,
        "partner": partner,
        "status": status,
        "weight_kg": result["weight_kg"],
        "co2_kg": result["co2_kg"],
        "points": max(40, result["score"] * 2) if points is None else points,
        "score": result["score"],
        "icon": device_icon(result["device"]),
        "tone": tone,
        "category": result.get("category_group") or category_group(result["device"]),
        "pathway": pathway or result.get("pathway") or "Recycle",
        "image": photo["data"] if photo else result.get("image"),
        "image_url": result.get("image_url"),
        "image_name": photo["name"] if photo else result.get("photo_name", ""),
        "battery_condition": result.get("battery_condition", "Normal"),
        "notes": notes or result.get("description") or "Session assessment record.",
    }
    return _normalise_history_item(entry)


def add_history(
    result: dict,
    partner: str,
    status: str = "Scheduled",
    points: int | None = None,
    pathway: str | None = None,
    notes: str | None = None,
) -> dict:
    assessment_id = result.get("id")
    if assessment_id:
        payload: dict = {
            "assessment_id": assessment_id,
            "partner": partner,
            "status": status,
            "notes": notes,
        }
        if pathway:
            payload["pathway"] = pathway
        if points is not None:
            payload["points"] = points
        try:
            entry = _normalise_history_item(api_client.create_history(payload))
            cached = st.session_state.get(HISTORY_KEY)
            if cached is None:
                st.session_state[HISTORY_KEY] = [entry]
            else:
                cached.insert(0, entry)
            st.session_state["history_source"] = "api"
            return entry
        except api_client.ApiError as exc:
            if exc.status_code == 409:
                refreshed = get_history(force=True)
                updates = {
                    key: value
                    for key, value in payload.items()
                    if key != "assessment_id" and value is not None
                }
                for index, item in enumerate(refreshed):
                    if item.get("assessment_id") == assessment_id:
                        if updates:
                            entry = _normalise_history_item(
                                api_client.update_history(item["id"], updates)
                            )
                            refreshed[index] = entry
                            return entry
                        return item
                raise
            if not exc.offline:
                raise

    entry = _local_history_entry(result, partner, status, points, pathway, notes)
    get_history().insert(0, entry)
    return entry


def completed_totals(history: list[dict]) -> dict:
    completed = [item for item in history if item["status"] == "Completed"]
    return {
        "devices": len(completed),
        "weight_kg": round(sum(item["weight_kg"] for item in completed), 2),
        "co2_kg": round(sum(item["co2_kg"] for item in completed), 1),
        "points": sum(item["points"] for item in completed),
    }


def pathway_totals(history: list[dict]) -> dict[str, dict]:
    totals = {
        pathway: {"devices": 0, "weight_kg": 0.0, "co2_kg": 0.0, "points": 0}
        for pathway in d.PATHWAYS
    }
    for item in history:
        pathway = item.get("pathway", "Recycle")
        if pathway not in totals:
            totals[pathway] = {"devices": 0, "weight_kg": 0.0, "co2_kg": 0.0, "points": 0}
        totals[pathway]["devices"] += 1
        totals[pathway]["weight_kg"] += float(item.get("weight_kg", 0))
        totals[pathway]["co2_kg"] += float(item.get("co2_kg", 0))
        totals[pathway]["points"] += int(item.get("points", 0))
    for values in totals.values():
        values["weight_kg"] = round(values["weight_kg"], 2)
        values["co2_kg"] = round(values["co2_kg"], 1)
    return totals
