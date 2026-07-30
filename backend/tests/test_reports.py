"""Reports & Export (Module 12).

What must hold:
  - every report renders in both formats with valid file bytes (PDF %PDF, xlsx PK)
  - the response is a real download (Content-Disposition attachment, right media type)
  - a report NEVER contains the is_insider ground-truth label
  - the compliance report is administrator-only (analyst -> 403)
  - the catalog is scoped by role (analyst does not see compliance)
  - the investigation report demands a user_id (missing -> 422; unknown -> 404)
  - unknown report / format -> 404
"""
from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from backend.app.database import SessionLocal
from backend.app.models import Alert, SecurityUser, UserRole
from backend.app.security import hash_password

PW = "Tr0ub4dor-Horse!"

# The operational reports any authenticated operator may pull.
_OPERATIONAL = ["insider-threat", "behavioral-analytics", "risk-assessment"]
# Every report, for the admin who can see them all.
_ALL = _OPERATIONAL + ["investigation", "compliance"]


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


def _a_user_with_alert() -> str | None:
    with SessionLocal() as db:
        a = db.query(Alert).first()
        return a.user_id if a else None


def _admin(client):
    e = f"ad{uuid.uuid4().hex[:8]}@dtaa.com"
    _make_user(e, UserRole.ADMINISTRATOR)
    return _login(client, e)


def _analyst(client):
    e = f"an{uuid.uuid4().hex[:8]}@dtaa.com"
    _make_user(e, UserRole.SECURITY_ANALYST)
    return _login(client, e)


# ---------------------------------------------------------------------------
# the file bytes are real
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("slug", _ALL)
def test_pdf_is_a_real_pdf(client: TestClient, slug):
    h = _admin(client)
    params = {}
    if slug == "investigation":
        uid = _a_user_with_alert()
        if uid is None:
            pytest.skip("no alerts - run the pipeline")
        params["user_id"] = uid
    r = client.get(f"/api/reports/{slug}.pdf", headers=h, params=params)
    assert r.status_code == 200, r.text
    assert r.content[:4] == b"%PDF"
    assert r.headers["content-type"] == "application/pdf"
    assert "attachment" in r.headers.get("content-disposition", "")


@pytest.mark.parametrize("slug", _ALL)
def test_xlsx_is_a_real_xlsx(client: TestClient, slug):
    h = _admin(client)
    params = {}
    if slug == "investigation":
        uid = _a_user_with_alert()
        if uid is None:
            pytest.skip("no alerts - run the pipeline")
        params["user_id"] = uid
    r = client.get(f"/api/reports/{slug}.xlsx", headers=h, params=params)
    assert r.status_code == 200, r.text
    assert r.content[:2] == b"PK"  # xlsx is a zip
    assert "spreadsheetml" in r.headers["content-type"]
    assert "attachment" in r.headers.get("content-disposition", "")


# ---------------------------------------------------------------------------
# the ground-truth label never leaks into a report
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("slug", _ALL)
def test_report_never_contains_is_insider(client: TestClient, slug):
    h = _admin(client)
    params = {}
    if slug == "investigation":
        uid = _a_user_with_alert()
        if uid is None:
            pytest.skip("no alerts - run the pipeline")
        params["user_id"] = uid
    for fmt in ("pdf", "xlsx"):
        r = client.get(f"/api/reports/{slug}.{fmt}", headers=h, params=params)
        assert r.status_code == 200
        assert b"is_insider" not in r.content, f"{slug}.{fmt} leaked is_insider"


# ---------------------------------------------------------------------------
# access control
# ---------------------------------------------------------------------------

def test_compliance_report_is_admin_only(client: TestClient):
    h = _analyst(client)
    r = client.get("/api/reports/compliance.pdf", headers=h)
    assert r.status_code == 403


def test_admin_can_pull_compliance(client: TestClient):
    h = _admin(client)
    r = client.get("/api/reports/compliance.pdf", headers=h)
    assert r.status_code == 200
    assert r.content[:4] == b"%PDF"


def test_catalog_is_scoped_by_role(client: TestClient):
    an = _analyst(client)
    ad = _admin(client)
    an_slugs = {x["slug"] for x in client.get("/api/reports/catalog", headers=an).json()["reports"]}
    ad_slugs = {x["slug"] for x in client.get("/api/reports/catalog", headers=ad).json()["reports"]}
    assert "compliance" not in an_slugs
    assert "compliance" in ad_slugs
    # the operational reports are visible to both
    for slug in _OPERATIONAL:
        assert slug in an_slugs and slug in ad_slugs


def test_reports_require_auth(client: TestClient):
    assert client.get("/api/reports/catalog").status_code == 401
    assert client.get("/api/reports/risk-assessment.pdf").status_code == 401


# ---------------------------------------------------------------------------
# validation
# ---------------------------------------------------------------------------

def test_investigation_requires_user_id(client: TestClient):
    h = _admin(client)
    r = client.get("/api/reports/investigation.pdf", headers=h)
    assert r.status_code == 422


def test_investigation_unknown_user_404(client: TestClient):
    h = _admin(client)
    r = client.get("/api/reports/investigation.pdf", headers=h,
                   params={"user_id": "NOPE9999"})
    assert r.status_code == 404


def test_unknown_report_404(client: TestClient):
    h = _admin(client)
    assert client.get("/api/reports/not-a-report.pdf", headers=h).status_code == 404


def test_unknown_format_404(client: TestClient):
    h = _admin(client)
    assert client.get("/api/reports/risk-assessment.docx", headers=h).status_code == 404
