from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlsplit

import httpx
import streamlit as st

DEFAULT_API_URL = "http://127.0.0.1:8000/api"
TIMEOUT = 8.0


class ApiError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None, offline: bool = False) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.offline = offline


def api_url() -> str:
    return os.getenv("RELOOP_API_URL", DEFAULT_API_URL).rstrip("/")


def server_root() -> str:
    parts = urlsplit(api_url())
    return f"{parts.scheme}://{parts.netloc}"


def absolute_url(path: str | None) -> str | None:
    if not path:
        return None
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return f"{server_root()}{path if path.startswith('/') else '/' + path}"


def _token() -> str | None:
    return st.session_state.get("api_token")


def _store_auth(payload: dict) -> None:
    st.session_state["api_token"] = payload["access_token"]
    st.session_state["api_user"] = payload.get("user")
    st.session_state["api_online"] = True


def clear_auth() -> None:
    st.session_state.pop("api_token", None)
    st.session_state.pop("api_user", None)


def _detail(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return f"Request failed with status {response.status_code}."
    detail = payload.get("detail") if isinstance(payload, dict) else None
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list):
        messages = []
        for item in detail:
            if isinstance(item, dict):
                location = ".".join(str(part) for part in item.get("loc", []) if part != "body")
                message = item.get("msg", "Invalid value")
                messages.append(f"{location}: {message}" if location else message)
            else:
                messages.append(str(item))
        if messages:
            return "; ".join(messages)
    return f"Request failed with status {response.status_code}."


def login(email: str | None = None, password: str | None = None) -> dict:
    email = email or os.getenv("DEMO_EMAIL", "demo@reloop.example")
    password = password or os.getenv("DEMO_PASSWORD", "reloop123")
    try:
        response = httpx.post(
            f"{api_url()}/auth/login",
            json={"email": email, "password": password},
            timeout=TIMEOUT,
        )
    except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout, httpx.TransportError) as exc:
        st.session_state["api_online"] = False
        raise ApiError(
            "Cannot reach the ReLoop API. Start it with: uvicorn backend.main:app --reload",
            offline=True,
        ) from exc
    if response.status_code >= 400:
        st.session_state["api_online"] = True
        raise ApiError(_detail(response), status_code=response.status_code)
    payload = response.json()
    _store_auth(payload)
    return payload


def ensure_auth() -> None:
    if _token():
        return
    login()


def _request(method: str, path: str, *, retry: bool = True, **kwargs: Any) -> httpx.Response:
    ensure_auth()
    headers = kwargs.pop("headers", {})
    token = _token()
    if token:
        headers = {**headers, "Authorization": f"Bearer {token}"}
    try:
        response = httpx.request(
            method,
            f"{api_url()}{path}",
            headers=headers,
            timeout=TIMEOUT,
            **kwargs,
        )
    except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout, httpx.TransportError) as exc:
        st.session_state["api_online"] = False
        raise ApiError(
            "The ReLoop API is unavailable. Showing local demo data instead.",
            offline=True,
        ) from exc

    st.session_state["api_online"] = True
    if response.status_code == 401 and retry:
        clear_auth()
        login()
        return _request(method, path, retry=False, **kwargs)
    if response.status_code >= 400:
        raise ApiError(_detail(response), status_code=response.status_code)
    return response


def request(method: str, path: str, **kwargs: Any) -> Any:
    response = _request(method, path, **kwargs)
    if response.status_code == 204 or not response.content:
        return None
    return response.json()


def get_user() -> dict:
    return request("GET", "/users/me")


def update_user(payload: dict) -> dict:
    return request("PATCH", "/users/me", json=payload)


def get_profile() -> dict:
    return request("GET", "/users/me/profile")


def update_profile(payload: dict) -> dict:
    return request("PUT", "/users/me/profile", json=payload)


def get_settings() -> dict:
    return request("GET", "/settings")


def update_settings(payload: dict) -> dict:
    return request("PUT", "/settings", json=payload)


def upload_identification(data: bytes, filename: str, content_type: str, hint: str = "") -> dict:
    return request(
        "POST",
        "/identifications",
        files={"file": (filename, data, content_type)},
        data={"hint": hint},
    )


def manual_identification(category: str, hint: str | None = None) -> dict:
    return request(
        "POST",
        "/identifications/manual",
        json={"category": category, "hint": hint},
    )


def create_assessment(payload: dict) -> dict:
    return request("POST", "/assessments", json=payload)


def update_assessment(assessment_id: int, payload: dict) -> dict:
    return request("PATCH", f"/assessments/{assessment_id}", json=payload)


def get_recommendation(assessment_id: int) -> dict:
    return request("GET", f"/assessments/{assessment_id}/recommendation")


def create_history(payload: dict) -> dict:
    return request("POST", "/history", json=payload)


def list_history(limit: int = 100) -> dict:
    return request("GET", "/history", params={"limit": limit})


def update_history(history_id: int, payload: dict) -> dict:
    return request("PATCH", f"/history/{history_id}", json=payload)


def history_summary() -> dict:
    return request("GET", "/history/summary")


def list_centres(**params: Any) -> list[dict]:
    return request("GET", "/centres", params=params)


def centre_meta() -> dict:
    return request("GET", "/centres/meta")


def dashboard_stats(range_value: str = "all", categories: list[str] | None = None) -> dict:
    params: dict[str, Any] = {"range": range_value}
    if categories:
        params["categories"] = ",".join(categories)
    return request("GET", "/dashboard/stats", params=params)


def impact_stats(range_value: str = "all", categories: list[str] | None = None) -> dict:
    params: dict[str, Any] = {"range": range_value}
    if categories:
        params["categories"] = ",".join(categories)
    return request("GET", "/dashboard/impact", params=params)


def fetch_image(path: str | None) -> bytes | None:
    if not path:
        return None
    image_path = path
    if image_path.startswith("http://") or image_path.startswith("https://"):
        parts = urlsplit(image_path)
        image_path = parts.path
        if parts.query:
            image_path = f"{image_path}?{parts.query}"
    response = _request("GET", image_path)
    return response.content
