"""Alert generation and the SOC workflow (spec Modules 7 and 9).

The two that matter here:

  test_rerunning_does_not_destroy_the_analysts_verdict - because DELETE-then-INSERT
  is the obvious implementation and it silently throws away the only ground truth
  that exists in production.

  test_only_a_manager_can_resolve - because "resolve as false positive" means "stop
  looking at this person", which is precisely the button an insider would most like
  to press about themselves.
"""

from __future__ import annotations

import uuid
from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import select

from backend.app.alerts import build_alert_rows, persist_alerts, severity_for
from backend.app.database import SessionLocal
from backend.app.models import Alert, AlertSeverity, AlertStatus, Employee

PW = "Tr0ub4dor-Horse!"


def _op(client: TestClient, role: str = "security_analyst"):
    email = f"u{uuid.uuid4().hex[:8]}@dtaa.com"
    r = client.post("/api/auth/register", json={
        "email": email, "full_name": "Op", "password": PW, "role": role})
    uid = r.json()["id"]
    tok = client.post("/api/auth/login",
                      data={"username": email, "password": PW}).json()
    return {"Authorization": f"Bearer {tok['access_token']}"}, uid


# ===========================================================================
# SEVERITY MAPPING
# ===========================================================================


def test_most_days_produce_no_alert_at_all() -> None:
    """Returning None is the common case, and that is the design working.

    99.7% of user-days deserve no alert. A system that writes a row for every one of
    them has not been thorough - it has produced a second copy of the feature table
    with worse ergonomics, in which an analyst cannot find anything.
    """
    assert severity_for(0.0, in_case_window=False) is None
    assert severity_for(5.0, in_case_window=False) is None
    assert severity_for(19.9, in_case_window=False) is None


def test_the_five_severities_map_as_specified() -> None:
    assert severity_for(95, False) is AlertSeverity.CRITICAL
    assert severity_for(45, False) is AlertSeverity.HIGH
    assert severity_for(25, False) is AlertSeverity.MEDIUM
    # Below MEDIUM, a row only exists as CONTEXT for a nearby real alert.
    assert severity_for(12, True) is AlertSeverity.LOW
    assert severity_for(2, True) is AlertSeverity.INFORMATIONAL
    assert severity_for(12, False) is None


def test_context_rows_are_bounded_to_a_window_not_a_career() -> None:
    """An investigator wants the days AROUND the incident.

    The first version made EVERY day of a flagged user informational, so an employee
    with 500 days of history generated 500 context rows and the table filled with
    thousands of alerts describing ordinary Tuesdays from eight months earlier.
    """
    base = pd.Timestamp("2010-06-01")
    df = pd.DataFrame({
        "user_id": ["A"] * 200,
        "date": pd.date_range(base, periods=200),
    })
    # One genuinely bad day, right in the middle.
    prob = np.zeros(200)
    prob[100] = 0.999

    rows = build_alert_rows(df, prob)
    dates = [r["alert_date"] for r in rows]
    span = (max(dates) - min(dates)).days

    assert span <= 62, (
        f"context rows span {span} days. They should be bounded to a window around "
        "the incident (30 either side), not the user's whole history."
    )
    assert len(rows) < 70, f"{len(rows)} rows from ONE bad day is too many"


# ===========================================================================
# IDEMPOTENCY - the one that would actually hurt
# ===========================================================================


def test_rerunning_does_not_destroy_the_analysts_verdict() -> None:
    """THE MOST IMPORTANT TEST IN THIS FILE.

    Batch jobs get re-run - after a retrain, after a bug fix, after somebody
    fat-fingers a date range. The obvious implementation, DELETE-then-INSERT, would
    silently wipe every verdict an analyst ever recorded.

    Those verdicts are the ONLY ground truth that exists in production. CERT ships an
    answer key; reality does not. They are how precision gets measured on live
    traffic, how you notice the model rotting, and the training signal for the next
    one. Destroying them to save a line of SQL would be the most expensive shortcut
    in the codebase.
    """
    with SessionLocal() as db:
        emp = db.scalar(select(Employee).limit(1))
        if emp is None:
            pytest.skip("no employees ingested")

        d = date(2010, 7, 15)
        db.query(Alert).filter(Alert.user_id == emp.user_id,
                               Alert.alert_date == d).delete()
        db.commit()

        row = {
            "user_id": emp.user_id, "alert_date": d,
            "severity": AlertSeverity.HIGH, "risk_score": 45.0,
            "ml_probability": 0.9, "components": {}, "top_features": [],
        }
        persist_alerts(db, [row])

        # An analyst works it.
        a = db.scalar(select(Alert).where(Alert.user_id == emp.user_id,
                                          Alert.alert_date == d))
        a.status = AlertStatus.RESOLVED_FALSE_POSITIVE
        a.resolution_note = "Heavy USB user. No exfiltration signal. Closed."
        alert_id = a.id
        db.commit()

        # The batch job runs again, with a DIFFERENT score (the model was retrained).
        row["risk_score"] = 51.0
        row["severity"] = AlertSeverity.CRITICAL
        persist_alerts(db, [row])

        db.expire_all()
        after = db.get(Alert, alert_id)

        assert after is not None, "the re-run DELETED the alert"
        assert after.risk_score == 51.0, "the score should have been refreshed"

        assert after.status is AlertStatus.RESOLVED_FALSE_POSITIVE, (
            "THE RE-RUN WIPED THE ANALYST'S VERDICT. Every human judgement in the "
            "system is now gone - the only ground truth that exists in production, "
            "and the training signal for the next model."
        )
        assert after.resolution_note is not None, "the re-run wiped the analyst's note"

        # And it must not have duplicated.
        n = db.scalar(
            select(Alert).where(Alert.user_id == emp.user_id, Alert.alert_date == d)
        )
        dupes = db.query(Alert).filter(
            Alert.user_id == emp.user_id, Alert.alert_date == d
        ).count()
        assert dupes == 1, f"the re-run created {dupes} copies of the same alert"


# ===========================================================================
# THE WORKFLOW
# ===========================================================================


@pytest.fixture
def an_alert(client: TestClient) -> int:
    with SessionLocal() as db:
        emp = db.scalar(select(Employee).limit(1))
        if emp is None:
            pytest.skip("no employees ingested")
        d = date(2011, 1, 1) + timedelta(days=int(uuid.uuid4().int % 300))
        db.query(Alert).filter(Alert.user_id == emp.user_id,
                               Alert.alert_date == d).delete()
        db.commit()
        a = Alert(
            user_id=emp.user_id, alert_date=d, severity=AlertSeverity.HIGH,
            risk_score=44.0, ml_probability=0.88, components={}, top_features=[],
        )
        db.add(a)
        db.commit()
        return a.id


def test_the_queue_needs_authentication(client: TestClient) -> None:
    assert client.get("/api/alerts").status_code == status.HTTP_401_UNAUTHORIZED


def test_an_analyst_can_acknowledge_and_investigate(
    client: TestClient, an_alert: int
) -> None:
    h, _ = _op(client)

    r = client.post(f"/api/alerts/{an_alert}/acknowledge", headers=h)
    assert r.status_code == 200
    assert r.json()["status"] == "acknowledged"

    r = client.post(f"/api/alerts/{an_alert}/investigate", headers=h)
    assert r.status_code == 200
    assert r.json()["status"] == "investigating"
    # You touched it, you own it.
    assert r.json()["assigned_to_id"] is not None


def test_acknowledge_is_idempotent(client: TestClient, an_alert: int) -> None:
    """A double-click must not be an error.

    An API that 409s because somebody clicked twice is an API that teaches people to
    stop clicking.
    """
    h, _ = _op(client)
    assert client.post(f"/api/alerts/{an_alert}/acknowledge", headers=h).status_code == 200
    assert client.post(f"/api/alerts/{an_alert}/acknowledge", headers=h).status_code == 200


def test_only_a_manager_can_resolve(client: TestClient, an_alert: int) -> None:
    """Resolving as a false positive means STOP LOOKING AT THIS PERSON.

    On a platform that surveils a thousand employees, that is precisely the button an
    insider would most like to press about themselves. So it takes a Manager, and it
    lands in the audit log with a name on it.
    """
    analyst, _ = _op(client, "security_analyst")
    r = client.post(
        f"/api/alerts/{an_alert}/resolve",
        json={"true_positive": False, "note": "nothing to see here"},
        headers=analyst,
    )
    assert r.status_code == status.HTTP_403_FORBIDDEN, (
        "a SECURITY ANALYST closed an alert as a false positive. Anyone who "
        "compromises the lowest-privileged account can now switch off surveillance "
        "of themselves, one alert at a time."
    )

    manager, _ = _op(client, "security_manager")
    r = client.post(
        f"/api/alerts/{an_alert}/resolve",
        json={"true_positive": True, "note": "Confirmed exfiltration."},
        headers=manager,
    )
    assert r.status_code == 200
    assert r.json()["status"] == "resolved_true_positive"


def test_the_verdict_distinguishes_true_from_false_positive(
    client: TestClient, an_alert: int
) -> None:
    """A single 'closed' state would throw away the analyst's judgement - the only
    ground truth that exists once you leave the CERT dataset behind."""
    manager, _ = _op(client, "security_manager")

    r = client.post(f"/api/alerts/{an_alert}/resolve",
                    json={"true_positive": False}, headers=manager)
    assert r.json()["status"] == "resolved_false_positive"

    r = client.get(f"/api/alerts/{an_alert}", headers=manager)
    assert r.json()["status"] == "resolved_false_positive"


def test_notes_are_recorded_against_the_alert(
    client: TestClient, an_alert: int
) -> None:
    h, uid = _op(client)
    r = client.post(f"/api/alerts/{an_alert}/notes",
                    json={"body": "Checked the file server logs. Nothing moved."},
                    headers=h)
    assert r.status_code == status.HTTP_201_CREATED
    assert r.json()["author_id"] == uid

    detail = client.get(f"/api/alerts/{an_alert}", headers=h).json()
    assert len(detail["notes"]) == 1
    assert "file server" in detail["notes"][0]["body"]


def test_an_escalated_alert_can_be_reopened(client: TestClient, an_alert: int) -> None:
    """New evidence arrives after a case is closed. Re-opening must be possible, and
    it must be VISIBLE that somebody did it."""
    manager, _ = _op(client, "security_manager")
    client.post(f"/api/alerts/{an_alert}/resolve",
                json={"true_positive": False}, headers=manager)

    r = client.post(f"/api/alerts/{an_alert}/escalate", headers=manager)
    assert r.status_code == 200
    assert r.json()["status"] == "escalated"


def test_the_summary_counts_the_queue(client: TestClient, an_alert: int) -> None:
    h, _ = _op(client)
    r = client.get("/api/alerts/summary", headers=h)
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1
    assert "by_severity" in body and "by_status" in body


def test_investigation_returns_a_timeline_and_a_baseline(
    client: TestClient, an_alert: int
) -> None:
    """The baseline is the point of the whole system.

    "Eight USB connections" is not evidence of anything. "Eight, against a personal
    baseline of zero" is the entire case - and it is the difference between UEBA and
    a threshold alert.
    """
    h, _ = _op(client)
    with SessionLocal() as db:
        a = db.get(Alert, an_alert)
        uid = a.user_id

    r = client.get(f"/api/investigate/{uid}", headers=h)
    assert r.status_code == 200
    body = r.json()

    assert body["employee"]["user_id"] == uid
    assert "timeline" in body
    assert "evidence" in body
    assert "baseline" in body

    # AND THE ANSWER KEY MUST NOT BE IN IT.
    assert "is_insider" not in body["employee"], (
        "the investigation view is leaking the CERT ground-truth label. An "
        "investigation is the process of forming a judgement; showing the analyst "
        "the answer first makes the whole exercise theatre. In production there is "
        "no answer key."
    )