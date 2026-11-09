import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_health_returns_healthy(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_version_returns_a_version(client):
    response = client.get("/version")
    assert response.status_code == 200
    assert "version" in response.get_json()


def test_environment_defaults_to_development(client, monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    response = client.get("/environment")
    assert response.status_code == 200
    assert response.get_json()["environment"] == "development"


def test_environment_reads_app_env(client, monkeypatch):
    monkeypatch.setenv("APP_ENV", "staging")
    response = client.get("/environment")
    assert response.get_json()["environment"] == "staging"


def test_environment_variable_takes_priority_over_app_env(client, monkeypatch):
    monkeypatch.setenv("APP_ENV", "staging")
    monkeypatch.setenv("ENVIRONMENT", "production")
    response = client.get("/environment")
    assert response.get_json()["environment"] == "production"


def test_unknown_route_returns_404(client):
    response = client.get("/does-not-exist")
    assert response.status_code == 404