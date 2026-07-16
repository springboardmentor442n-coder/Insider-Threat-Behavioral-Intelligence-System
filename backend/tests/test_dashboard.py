"""The dashboard aggregation endpoints, and the two things about them that must
never break: the ground-truth leak guard on top-risks, and the admin-only gate on
the audit log.

These endpoints are read-only and derived, so most of what could go wrong is a wrong
number - and a wrong number in a chart is caught by eye. What is NOT caught by eye is
a security regression: top-risks quietly returning is_insider, or the audit log
quietly becoming readable by an analyst. Those are the tests that earn their keep.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from backend.app.database import SessionLocal
from backend.app.models import Alert, AlertSeverity

PW = "Tr0ub4dor-Horse!"


def _make(client: TestClient, role: str = "security_analyst") -> dict:
    """Register an operator of the given role and return its auth header.

    Mirrors the helper in test_users.py: the registration endpoint accepts a role,
    and the id comes straight from the response rather than by scanning a paginated
    list.
    """
    email = f"u{uuid.uuid4().hex[:8]}@dtaa.com"
    reg = client.post(
        "/api/auth/register",
        json={"email": email, "full_name": "Op", "password": PW, "role": role},
    )
    assert reg.status_code == 201, reg.text
    tok = client.post(
        "/api/auth/login", data={"username": email, "password": PW}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}


def _has_alerts() -> bool:
    with SessionLocal() as db:
        return db.scalar(select(Alert.id).limit(1)) is not None


# --- the leak guard --------------------------------------------------------

def test_top_risks_never_returns_ground_truth(client: TestClient) -> None:
    """top-risks is open to analysts and ranks on model risk score. It must NOT leak
    is_insider - that is the CERT answer key, and exposing it here would turn a
    watch-list into a covert channel to the labels.
    """
    h = _make(client, "security_analyst")
    r = client.get("/api/dashboard/top-risks?limit=20", headers=h)
    assert r.status_code == 200, r.text
    for emp in r.json()["employees"]:
        assert "is_insider" not in emp, (
            "top-risks leaked is_insider - the ground-truth answer key is now "
            "readable by any analyst through the dashboard."
        )
        assert "insider_scenario" not in emp
        assert "scenario" not in emp


# --- the admin gate --------------------------------------------------------

def test_audit_log_is_forbidden_to_analysts(client: TestClient) -> None:
    h = _make(client, "security_analyst")
    r = client.get("/api/audit", headers=h)
    assert r.status_code == 403, (
        f"an analyst reached the audit log (got {r.status_code}, expected 403). "
        "The audit trail of the security team is readable by a non-admin."
    )


def test_audit_log_is_forbidden_to_managers(client: TestClient) -> None:
    h = _make(client, "security_manager")
    r = client.get("/api/audit", headers=h)
    assert r.status_code == 403, (
        f"a manager reached the audit log (got {r.status_code}, expected 403)."
    )


def test_audit_log_is_allowed_for_admins(client: TestClient) -> None:
    h = _make(client, "administrator")
    r = client.get("/api/audit", headers=h)
    assert r.status_code == 200, r.text
    body = r.json()
    assert "total" in body
    assert "entries" in body


# --- the endpoints return the shape the charts expect ----------------------

def test_risk_trend_is_densified(client: TestClient) -> None:
    """Every day in the window must appear, including zero days. A chart that skips
    quiet days reads as missing data, not as calm.
    """
    if not _has_alerts():
        pytest.skip("no alerts in the database - run generate_alerts")
    h = _make(client, "security_analyst")
    r = client.get("/api/dashboard/risk-trend?days=30", headers=h)
    assert r.status_code == 200, r.text
    series = r.json()["series"]
    assert len(series) == 30, (
        f"risk-trend returned {len(series)} points for a 30-day window - it is not "
        "densifying, so the chart will have gaps where days had no alerts."
    )
    for point in series:
        for sev in AlertSeverity:
            assert sev.value in point, f"point missing severity {sev.value}: {point}"


def test_anomaly_breakdown_returns_all_five_components(client: TestClient) -> None:
    if not _has_alerts():
        pytest.skip("no alerts in the database - run generate_alerts")
    h = _make(client, "security_analyst")
    r = client.get("/api/dashboard/anomaly-breakdown", headers=h)
    assert r.status_code == 200, r.text
    comps = {c["component"] for c in r.json()["components"]}
    expected = {
        "behavioral_anomalies",
        "privilege_misuse",
        "data_access_violations",
        "access_pattern_deviations",
        "historical_security_events",
    }
    assert comps == expected, f"missing components: {expected - comps}"


def test_top_risks_is_ranked_descending(client: TestClient) -> None:
    if not _has_alerts():
        pytest.skip("no alerts in the database - run generate_alerts")
    h = _make(client, "security_analyst")
    r = client.get("/api/dashboard/top-risks?limit=10", headers=h)
    assert r.status_code == 200, r.text
    scores = [e["peak_risk_score"] for e in r.json()["employees"]]
    assert scores == sorted(scores, reverse=True), (
        "top-risks is not sorted by peak risk descending - the watch-list is out "
        "of order."
    )


def test_dashboard_requires_authentication(client: TestClient) -> None:
    """No token, no dashboard. All three endpoints."""
    for path in (
        "/api/dashboard/risk-trend",
        "/api/dashboard/anomaly-breakdown",
        "/api/dashboard/top-risks",
    ):
        r = client.get(path)
        assert r.status_code == 401, f"{path} served without a token ({r.status_code})"