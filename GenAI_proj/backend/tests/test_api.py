from __future__ import annotations

import io
import uuid

from fastapi.testclient import TestClient
from PIL import Image

from data.mock_data import HAZARDOUS_BATTERY_CONDITIONS, IDENTIFY_CATEGORIES, PATHWAYS


def _png_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (12, 12), (30, 180, 120)).save(buffer, format="PNG")
    return buffer.getvalue()


def _create_assessment(
    client: TestClient,
    headers: dict[str, str],
    *,
    battery: str = "Normal",
    selected_pathway: str | None = None,
) -> dict:
    payload = {
        "device": "Smartphone",
        "age_years": 2,
        "working": battery not in HAZARDOUS_BATTERY_CONDITIONS,
        "physical_damage": "None",
        "battery_condition": battery,
        "brand": "TestBrand",
        "model": f"Model-{uuid.uuid4().hex[:6]}",
        "description": "Backend test assessment",
    }
    if selected_pathway:
        payload["selected_pathway"] = selected_pathway
    response = client.post("/api/assessments", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def test_health(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_login_and_current_user(client: TestClient, auth_headers: dict[str, str]) -> None:
    me = client.get("/api/auth/me", headers=auth_headers)
    assert me.status_code == 200
    body = me.json()
    assert body["email"] == "demo@reloop.example"
    assert "password_hash" not in body
    assert client.get("/api/auth/me").status_code == 401


def test_register_and_login(client: TestClient) -> None:
    email = f"new-{uuid.uuid4().hex[:8]}@example.com"
    response = client.post(
        "/api/auth/register",
        json={"name": "New User", "email": email, "password": "strongpass123", "city": "Mysuru"},
    )
    assert response.status_code == 201, response.text
    assert response.json()["user"]["email"] == email

    duplicate = client.post(
        "/api/auth/register",
        json={"name": "New User", "email": email, "password": "strongpass123"},
    )
    assert duplicate.status_code == 409

    login = client.post("/api/auth/login", json={"email": email, "password": "strongpass123"})
    assert login.status_code == 200
    assert client.post(
        "/api/auth/login", json={"email": email, "password": "wrong-password"}
    ).status_code == 401


def test_dashboard_and_centres(client: TestClient, auth_headers: dict[str, str]) -> None:
    stats = client.get("/api/dashboard/stats", headers=auth_headers)
    assert stats.status_code == 200, stats.text
    body = stats.json()
    assert body["totals"]["devices_assessed"] >= 1
    assert body["recent_activity"]

    impact = client.get("/api/dashboard/impact", headers=auth_headers)
    assert impact.status_code == 200
    assert "equivalents" in impact.json()

    centres = client.get("/api/centres", headers=auth_headers)
    assert centres.status_code == 200
    assert centres.json()
    assert all(item["fictional"] for item in centres.json())
    meta = client.get("/api/centres/meta", headers=auth_headers)
    assert meta.status_code == 200
    assert meta.json()["fictional"] is True


def test_image_upload_validation(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/identifications",
        headers=auth_headers,
        files={"file": ("device.png", _png_bytes(), "image/png")},
        data={"hint": "phone"},
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["device"] in IDENTIFY_CATEGORIES
    assert body["image_url"]

    image = client.get(body["image_url"], headers=auth_headers)
    assert image.status_code == 200
    assert image.headers["content-type"].startswith("image/")

    bad = client.post(
        "/api/identifications",
        headers=auth_headers,
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert bad.status_code == 400

    manual = client.post(
        "/api/identifications/manual",
        headers=auth_headers,
        json={"category": "Laptop", "hint": "manual"},
    )
    assert manual.status_code == 201
    assert manual.json()["mapped_device"] == "Laptop"


def test_hazardous_battery_safety_rule(client: TestClient, auth_headers: dict[str, str]) -> None:
    assessment = _create_assessment(client, auth_headers, battery="Swollen")
    assert assessment["pathway"] == "Hazardous Handling"
    recommendation = assessment["recommendation"]
    assert recommendation["pathway"] == "Hazardous Handling"
    assert recommendation["safety_override"] is True
    assert all(
        item["eligible"] is False or item["pathway"] == "Hazardous Handling"
        for item in recommendation["ranked"]
    )

    blocked = client.patch(
        f"/api/assessments/{assessment['id']}",
        headers=auth_headers,
        json={"selected_pathway": "Repair"},
    )
    assert blocked.status_code == 422

    history = client.post(
        "/api/history",
        headers=auth_headers,
        json={"assessment_id": assessment["id"], "pathway": "Recycle", "status": "Processing"},
    )
    assert history.status_code == 422

    safe_history = client.post(
        "/api/history",
        headers=auth_headers,
        json={"assessment_id": assessment["id"], "status": "Completed"},
    )
    assert safe_history.status_code == 201, safe_history.text
    assert safe_history.json()["pathway"] == "Hazardous Handling"

    for pathway in PATHWAYS:
        if pathway == "Hazardous Handling":
            continue
        direct = client.post(
            "/api/assessments",
            headers=auth_headers,
            json={
                "device": "Smartphone",
                "working": False,
                "battery_condition": "Leaking",
                "selected_pathway": pathway,
            },
        )
        assert direct.status_code == 422


def test_normal_assessment_history_and_recommendation(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    assessment = _create_assessment(client, auth_headers)
    assert assessment["pathway"] in PATHWAYS
    assert assessment["recommendation"]["pathway"] in PATHWAYS

    history = client.post(
        "/api/history",
        headers=auth_headers,
        json={
            "assessment_id": assessment["id"],
            "status": "Completed",
            "notes": "Drop-off completed",
        },
    )
    assert history.status_code == 201, history.text
    entry = history.json()
    assert entry["status"] == "Completed"
    assert entry["points"] > 0

    duplicate = client.post(
        "/api/history",
        headers=auth_headers,
        json={"assessment_id": assessment["id"], "status": "Completed"},
    )
    assert duplicate.status_code == 409

    listed = client.get("/api/history", headers=auth_headers)
    assert listed.status_code == 200
    assert any(item["id"] == entry["id"] for item in listed.json()["items"])

    summary = client.get("/api/history/summary", headers=auth_headers)
    assert summary.status_code == 200
    assert summary.json()["devices"] >= 1

    recommendation = client.get(
        f"/api/assessments/{assessment['id']}/recommendation", headers=auth_headers
    )
    assert recommendation.status_code == 200
    assert recommendation.json()["assessment_id"] == assessment["id"]


def test_profile_and_settings(client: TestClient, auth_headers: dict[str, str]) -> None:
    profile = client.put(
        "/api/users/me/profile",
        headers=auth_headers,
        json={"phone": "+91 90000 00000", "home_area": "Indiranagar"},
    )
    assert profile.status_code == 200
    assert profile.json()["phone"] == "+91 90000 00000"

    settings = client.put(
        "/api/settings",
        headers=auth_headers,
        json={"pickup_reminders": False, "max_distance_km": 8, "accent": "Ocean"},
    )
    assert settings.status_code == 200, settings.text
    assert settings.json()["pickup_reminders"] is False
    assert settings.json()["max_distance_km"] == 8

    fetched = client.get("/api/settings/preferences", headers=auth_headers)
    assert fetched.status_code == 200
    assert fetched.json()["accent"] == "Ocean"


def test_user_cannot_read_another_users_assessment(client: TestClient) -> None:
    owner_email = f"owner-{uuid.uuid4().hex[:8]}@example.com"
    other_email = f"other-{uuid.uuid4().hex[:8]}@example.com"
    owner = client.post(
        "/api/auth/register",
        json={"name": "Owner", "email": owner_email, "password": "strongpass123"},
    ).json()
    other = client.post(
        "/api/auth/register",
        json={"name": "Other", "email": other_email, "password": "strongpass123"},
    ).json()
    owner_headers = {"Authorization": f"Bearer {owner['access_token']}"}
    other_headers = {"Authorization": f"Bearer {other['access_token']}"}

    assessment = _create_assessment(client, owner_headers)
    assert client.get(
        f"/api/assessments/{assessment['id']}", headers=other_headers
    ).status_code == 404
    assert client.get(
        f"/api/assessments/{assessment['id']}/recommendation", headers=other_headers
    ).status_code == 404
