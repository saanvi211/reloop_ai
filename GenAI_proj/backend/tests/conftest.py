from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

TEMP_ROOT = Path(tempfile.mkdtemp(prefix="reloop-api-tests-"))
os.environ["DATABASE_URL"] = f"sqlite:///{(TEMP_ROOT / 'test.db').as_posix()}"
os.environ["UPLOAD_DIR"] = str(TEMP_ROOT / "uploads")
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["SEED_DEMO_DATA"] = "true"
os.environ["DEMO_EMAIL"] = "demo@reloop.example"
os.environ["DEMO_PASSWORD"] = "reloop123"

from fastapi.testclient import TestClient  # noqa: E402

from backend.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/auth/login",
        json={"email": "demo@reloop.example", "password": "reloop123"},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
