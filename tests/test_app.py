import json
import logging

import pytest
from prometheus_client import REGISTRY

from app import app


class ListHandler(logging.Handler):
    """Collects the raw log messages so a test can inspect them."""

    def __init__(self):
        super().__init__()
        self.lines = []

    def emit(self, record):
        self.lines.append(record.getMessage())


@pytest.fixture
def captured_logs():
    handler = ListHandler()
    logger = logging.getLogger("system-health")
    logger.addHandler(handler)
    yield handler.lines
    logger.removeHandler(handler)


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


def test_metrics_endpoint_returns_prometheus_text(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.content_type.startswith("text/plain")
    assert b"http_requests_total" in response.data
    assert b"http_request_duration_seconds" in response.data


def test_metrics_include_app_info_and_uptime(client):
    body = client.get("/metrics").data.decode()
    assert 'app_info{environment="' in body
    assert 'version="' in body
    assert "app_uptime_seconds" in body


def test_each_request_writes_one_valid_json_log_line(client, captured_logs, monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "staging")
    client.get("/health")
    assert len(captured_logs) == 1
    entry = json.loads(captured_logs[0])
    for field in ("timestamp", "level", "message", "endpoint", "method", "status", "environment"):
        assert field in entry
    assert entry["level"] == "INFO"
    assert entry["endpoint"] == "/health"
    assert entry["method"] == "GET"
    assert entry["status"] == 200
    assert entry["environment"] == "staging"


def test_unknown_route_is_logged_as_warning(client, captured_logs):
    client.get("/does-not-exist")
    entry = json.loads(captured_logs[0])
    assert entry["level"] == "WARNING"
    assert entry["status"] == 404
    assert entry["path"] == "/does-not-exist"


def test_simulate_error_is_404_when_fault_injection_is_off(client, monkeypatch):
    monkeypatch.delenv("ENABLE_FAULT_INJECTION", raising=False)
    assert client.get("/simulate-error").status_code == 404
    monkeypatch.setenv("ENABLE_FAULT_INJECTION", "false")
    assert client.get("/simulate-error").status_code == 404


def test_simulate_error_returns_500_when_fault_injection_is_on(client, monkeypatch):
    monkeypatch.setenv("ENABLE_FAULT_INJECTION", "true")
    response = client.get("/simulate-error")
    assert response.status_code == 500
    assert "error" in response.get_json()


def test_simulate_error_is_logged_at_error_level_and_counted(client, captured_logs, monkeypatch):
    monkeypatch.setenv("ENABLE_FAULT_INJECTION", "true")
    labels = {"method": "GET", "endpoint": "/simulate-error", "status": "500"}
    before = REGISTRY.get_sample_value("http_requests_total", labels) or 0
    client.get("/simulate-error")
    entry = json.loads(captured_logs[0])
    assert entry["level"] == "ERROR"
    assert entry["endpoint"] == "/simulate-error"
    assert entry["status"] == 500
    assert entry["message"] == "Simulated fault injected"
    assert REGISTRY.get_sample_value("http_requests_total", labels) == before + 1


def test_request_counter_increments(client):
    labels = {"method": "GET", "endpoint": "/health", "status": "200"}
    before = REGISTRY.get_sample_value("http_requests_total", labels) or 0
    client.get("/health")
    assert REGISTRY.get_sample_value("http_requests_total", labels) == before + 1


def test_unknown_routes_share_one_endpoint_label(client):
    labels = {"method": "GET", "endpoint": "unknown", "status": "404"}
    before = REGISTRY.get_sample_value("http_requests_total", labels) or 0
    client.get("/no-such-page-1")
    client.get("/no-such-page-2")
    assert REGISTRY.get_sample_value("http_requests_total", labels) == before + 2


def test_latency_histogram_records_observations(client):
    labels = {"endpoint": "/version"}
    before = REGISTRY.get_sample_value("http_request_duration_seconds_count", labels) or 0
    client.get("/version")
    assert REGISTRY.get_sample_value("http_request_duration_seconds_count", labels) == before + 1