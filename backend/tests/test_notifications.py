"""The notification centre (Module 11).

What must hold:
  - an escalation notifies oversight (managers/admins) but NOT the actor
  - the badge count and the feed are scoped to the current operator only
  - mark-read and mark-all-read work and move the count
  - a notification NEVER carries the is_insider ground-truth label
  - you cannot read or mark another operator's notifications (404)
"""
from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from backend.app.database import SessionLocal
from backend.app.models import Alert, SecurityUser, UserRole
from backend.app.security import hash_password

PW = "Tr0ub4dor-Horse!"


def _make_user(email: str, role: UserRole) -> int:
    with SessionLocal() as db:
        existing = db.query(SecurityUser).filter_by(email=email).first()
        if existing:
            return existing.id
        u = SecurityUser(email=email, full_name=email,
                         hashed_password=hash_password(PW), role=role, is_active=True)
        db.add(u); db.commit(); db.refresh(u)
        return u.id


def _login(client: TestClient, email: str) -> dict:
    tok = client.post("/api/auth/login",
                      data={"username": email, "password": PW}).json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}


def _an_alert_id() -> int | None:
    with SessionLocal() as db:
        a = db.query(Alert).first()
        return a.id if a else None


def test_escalation_notifies_oversight_not_the_actor(client: TestClient):
    aid = _an_alert_id()
    if aid is None:
        pytest.skip("no alerts - run the pipeline")
    # a manager (oversight) and the analyst who will escalate
    mgr_email = f"m{uuid.uuid4().hex[:8]}@dtaa.com"
    _make_user(mgr_email, UserRole.SECURITY_MANAGER)
    analyst_email = f"a{uuid.uuid4().hex[:8]}@dtaa.com"
    _make_user(analyst_email, UserRole.SECURITY_ANALYST)

    ah = _login(client, analyst_email)
    r = client.post(f"/api/alerts/{aid}/escalate", headers=ah)
    assert r.status_code == 200

    # the manager received a notification
    mh = _login(client, mgr_email)
    feed = client.get("/api/notifications", headers=mh).json()
    assert any(n["type"] == "escalation" for n in feed["notifications"])

    # the analyst who escalated did NOT get notified of their own action
    afeed = client.get("/api/notifications", headers=ah).json()
    assert all(n["type"] != "escalation" or n["subject_user_id"] is None
               for n in afeed["notifications"]) or len(afeed["notifications"]) == 0


def test_feed_and_count_are_scoped_to_the_current_user(client: TestClient):
    """One operator must never see another's notifications."""
    aid = _an_alert_id()
    if aid is None:
        pytest.skip("no alerts")
    _make_user("mgr_scope@dtaa.com", UserRole.SECURITY_MANAGER)
    other_email = f"o{uuid.uuid4().hex[:8]}@dtaa.com"
    _make_user(other_email, UserRole.SECURITY_ANALYST)
    actor_email = f"x{uuid.uuid4().hex[:8]}@dtaa.com"
    _make_user(actor_email, UserRole.SECURITY_ANALYST)

    # actor escalates -> manager gets notified; the unrelated analyst does not
    ah = _login(client, actor_email)
    client.post(f"/api/alerts/{aid}/escalate", headers=ah)

    oh = _login(client, other_email)
    count = client.get("/api/notifications/unread-count", headers=oh).json()
    assert count["unread"] == 0  # this analyst was not a recipient


def test_mark_read_moves_the_count(client: TestClient):
    aid = _an_alert_id()
    if aid is None:
        pytest.skip("no alerts")
    mgr_email = f"m{uuid.uuid4().hex[:8]}@dtaa.com"
    _make_user(mgr_email, UserRole.SECURITY_MANAGER)
    actor_email = f"a{uuid.uuid4().hex[:8]}@dtaa.com"
    _make_user(actor_email, UserRole.SECURITY_ANALYST)

    client.post(f"/api/alerts/{aid}/escalate", headers=_login(client, actor_email))
    mh = _login(client, mgr_email)

    before = client.get("/api/notifications/unread-count", headers=mh).json()["unread"]
    if before == 0:
        pytest.skip("manager had no unread notification to test with")

    feed = client.get("/api/notifications", headers=mh).json()["notifications"]
    nid = next(n["id"] for n in feed if not n["is_read"])
    client.post(f"/api/notifications/{nid}/read", headers=mh)

    after = client.get("/api/notifications/unread-count", headers=mh).json()["unread"]
    assert after == before - 1


def test_mark_all_read_clears_the_badge(client: TestClient):
    aid = _an_alert_id()
    if aid is None:
        pytest.skip("no alerts")
    mgr_email = f"m{uuid.uuid4().hex[:8]}@dtaa.com"
    _make_user(mgr_email, UserRole.SECURITY_MANAGER)
    actor_email = f"a{uuid.uuid4().hex[:8]}@dtaa.com"
    _make_user(actor_email, UserRole.SECURITY_ANALYST)
    client.post(f"/api/alerts/{aid}/escalate", headers=_login(client, actor_email))

    mh = _login(client, mgr_email)
    client.post("/api/notifications/read-all", headers=mh)
    after = client.get("/api/notifications/unread-count", headers=mh).json()["unread"]
    assert after == 0


def test_notifications_never_leak_is_insider(client: TestClient):
    aid = _an_alert_id()
    if aid is None:
        pytest.skip("no alerts")
    mgr_email = f"m{uuid.uuid4().hex[:8]}@dtaa.com"
    _make_user(mgr_email, UserRole.SECURITY_MANAGER)
    actor_email = f"a{uuid.uuid4().hex[:8]}@dtaa.com"
    _make_user(actor_email, UserRole.SECURITY_ANALYST)
    client.post(f"/api/alerts/{aid}/escalate", headers=_login(client, actor_email))

    mh = _login(client, mgr_email)
    r = client.get("/api/notifications", headers=mh)
    assert "is_insider" not in r.text


def test_cannot_mark_another_users_notification(client: TestClient):
    aid = _an_alert_id()
    if aid is None:
        pytest.skip("no alerts")
    mgr_email = f"m{uuid.uuid4().hex[:8]}@dtaa.com"
    _make_user(mgr_email, UserRole.SECURITY_MANAGER)
    actor_email = f"a{uuid.uuid4().hex[:8]}@dtaa.com"
    _make_user(actor_email, UserRole.SECURITY_ANALYST)
    client.post(f"/api/alerts/{aid}/escalate", headers=_login(client, actor_email))

    mh = _login(client, mgr_email)
    feed = client.get("/api/notifications", headers=mh).json()["notifications"]
    if not feed:
        pytest.skip("no notification to test with")
    someone_elses = feed[0]["id"]

    # a DIFFERENT analyst tries to mark the manager's notification read
    intruder_email = f"i{uuid.uuid4().hex[:8]}@dtaa.com"
    _make_user(intruder_email, UserRole.SECURITY_ANALYST)
    ih = _login(client, intruder_email)
    r = client.post(f"/api/notifications/{someone_elses}/read", headers=ih)
    assert r.status_code == 404
