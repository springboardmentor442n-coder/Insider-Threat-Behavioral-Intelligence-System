"""Tests for the Phase 0 skeleton endpoints.

These exist from the very first commit on purpose. Tests written at the end of
a project are an afterthought that everyone skips; tests written alongside the
first endpoint set the standard for every endpoint that follows.
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture
def client() -> TestClient:
    """A test client that calls the app in-process (no real network, no server)."""
    return TestClient(app)


def test_root_returns_service_metadata(client: TestClient) -> None:
    """GET / identifies the service and reports it is running."""
    response = client.get("/")

    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "running"
    assert "service" in body
    assert "version" in body
    assert "environment" in body


def test_health_returns_expected_shape(client: TestClient) -> None:
    """GET /health always reports on the api and database checks.

    Note this asserts the SHAPE, not that the database is up. The test must
    pass whether or not Postgres happens to be running, otherwise it is really
    an integration test masquerading as a unit test - and it will fail in CI
    for reasons that have nothing to do with the code being tested.
    """
    response = client.get("/health")

    # Either healthy (200) or correctly reporting a dead dependency (503).
    # Both are correct behaviour; a 500 would not be.
    assert response.status_code in (200, 503)

    body = response.json()
    assert body["status"] in ("healthy", "unhealthy")
    assert body["checks"]["api"] == "ok"
    assert body["checks"]["database"] in ("ok", "unreachable")


def test_health_reports_healthy_when_database_is_up(client: TestClient) -> None:
    """With Postgres reachable, /health returns 200 and status healthy.

    This IS an integration test - it needs a live database. It runs locally
    (your Docker container) and in CI (a Postgres service container).
    """
    response = client.get("/health")

    if response.status_code == 503:
        pytest.skip("Postgres is not reachable - start the Docker container.")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["checks"]["database"] == "ok"