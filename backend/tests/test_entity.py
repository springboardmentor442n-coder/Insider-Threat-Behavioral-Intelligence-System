"""The UEBA entity-analytics endpoint (Module 8).

What must hold:
  - it returns peer-relative standing, drift, and trajectory for a real employee
  - it NEVER exposes the is_insider ground-truth label (safe for every role)
  - it 404s cleanly on an unknown employee
  - it degrades gracefully for an employee with no feature history

These run only when feature data exists (the CI fixture provides it); without
data they skip, like the other pipeline-dependent tests.
"""
from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from backend.app.database import SessionLocal
from backend.app.features_models import DailyFeatures
from backend.app.models import Employee

PW = "Tr0ub4dor-Horse!"


def _auth(client: TestClient, role: str = "security_analyst") -> dict:
    email = f"u{uuid.uuid4().hex[:8]}@dtaa.com"
    client.post("/api/auth/register",
                json={"email": email, "full_name": "Op", "password": PW, "role": role})
    tok = client.post("/api/auth/login",
                      data={"username": email, "password": PW}).json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}


def _a_user_with_features() -> str | None:
    with SessionLocal() as db:
        row = db.query(DailyFeatures.user_id).first()
        return row[0] if row else None


def test_unknown_employee_404s(client: TestClient):
    h = _auth(client)
    r = client.get("/api/entity/NOPE9999", headers=h)
    assert r.status_code == 404


def test_entity_returns_the_three_ueba_blocks(client: TestClient):
    uid = _a_user_with_features()
    if uid is None:
        pytest.skip("no features built - run the pipeline")
    h = _auth(client)
    r = client.get(f"/api/entity/{uid}", headers=h)
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["has_data"] is True
    # the three UEBA views are present
    assert "peer_standing" in d
    assert "drift" in d
    assert "trajectory" in d
    # peer standing entries carry the fields a UI needs, including BOTH the
    # average deviation and the peak (worst-single-day) deviation
    if d["peer_standing"]:
        row = d["peer_standing"][0]
        assert {"feature", "label", "user_mean", "peer_mean",
                "peer_z", "peak_z", "user_peak"} <= set(row)


def test_peak_deviation_is_at_least_as_extreme_as_average(client: TestClient):
    """The peak (worst-day) z must never be LESS extreme than the average z for a
    behaviour the user actually does - a single day can only be >= the mean. This
    is what lets a one-day attack surface where the average buries it."""
    uid = _a_user_with_features()
    if uid is None:
        pytest.skip("no features built")
    h = _auth(client)
    d = client.get(f"/api/entity/{uid}", headers=h).json()
    for r in d["peer_standing"]:
        # for positive deviations, peak should be >= average (the max day is the
        # highest day). We check magnitude on the upper side.
        if r["peer_z"] > 0 and r["peak_z"] is not None:
            assert r["peak_z"] >= r["peer_z"] - 0.01  # tolerance for rounding


def test_entity_never_leaks_is_insider(client: TestClient):
    """The security guard: entity analytics is safe for every role, so the
    ground-truth label must not appear anywhere in the response - not even for an
    analyst querying a known insider."""
    uid = _a_user_with_features()
    if uid is None:
        pytest.skip("no features built")
    h = _auth(client, role="security_analyst")
    r = client.get(f"/api/entity/{uid}", headers=h)
    assert r.status_code == 200
    assert "is_insider" not in r.text


def test_entity_peer_standing_is_ranked_most_anomalous_first(client: TestClient):
    """The list must be ordered most-anomalous-first; that ordering is the value.

    Anomaly is the LARGER of the two signals - average deviation or peak-day
    deviation - so a behaviour that is extreme on only one day still sorts to the
    top. Ranking by the average alone would re-bury the single-day attacker we
    added the peak view specifically to surface.
    """
    uid = _a_user_with_features()
    if uid is None:
        pytest.skip("no features built")
    h = _auth(client)
    d = client.get(f"/api/entity/{uid}", headers=h).json()
    scores = [max(abs(p["peer_z"]), abs(p["peak_z"] or 0)) for p in d["peer_standing"]]
    assert scores == sorted(scores, reverse=True)
