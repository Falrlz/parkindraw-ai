"""Integration tests for root and health check endpoints."""

from fastapi.testclient import TestClient


def test_root_descriptor(client: TestClient) -> None:
    """Ensure root descriptor endpoint returns expected metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "docs" in data
    assert data["docs"] == "/docs"


def test_root_health_check(client: TestClient) -> None:
    """Ensure root /health check endpoint returns valid health payload."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("ok", "degraded")
    assert "models" in data
    assert "circle" in data["models"]
    assert "meander" in data["models"]
    assert "spiral" in data["models"]
    assert isinstance(data["all_models_loaded"], bool)


def test_api_v1_health_check(client: TestClient) -> None:
    """Ensure versioned /api/v1/health check endpoint functions identically."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "device" in data
    assert "timestamp" in data
