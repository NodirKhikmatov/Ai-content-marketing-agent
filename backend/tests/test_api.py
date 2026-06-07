"""FastAPI integration tests (no live Supabase required)."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


def test_root_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_health_degraded_without_supabase(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "1.0.0"
    assert data["status"] in ("ok", "degraded")


def test_projects_require_auth(client):
    response = client.get("/api/v1/projects")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_me_requires_auth(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
