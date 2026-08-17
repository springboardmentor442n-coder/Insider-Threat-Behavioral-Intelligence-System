"""API contract, authentication and RBAC."""

import pytest

from tests.conftest import needs_model

pytestmark = needs_model


# ── auth ───────────────────────────────────────────────────────────────────
def test_login_returns_a_token_and_profile(client):
    res = client.post("/api/v1/auth/login",
                      json={"username": "analyst", "password": "analyst-pw"})
    body = res.get_json()

    assert res.status_code == 200
    assert body["token_type"] == "bearer"
    assert body["analyst"]["role"] == "analyst"
    assert "password" not in str(body).lower() or "password_hash" not in str(body)


@pytest.mark.parametrize("payload", [
    {"username": "analyst", "password": "wrong"},
    {"username": "nobody", "password": "analyst-pw"},
    {},
])
def test_bad_credentials_are_rejected_identically(client, payload):
    res = client.post("/api/v1/auth/login", json=payload)
    assert res.status_code == 401
    # Same message either way — no user enumeration.
    assert res.get_json()["error"] == "invalid credentials"


def test_protected_endpoints_require_a_token(client):
    assert client.get("/api/v1/dashboard").status_code == 401


def test_a_garbage_token_is_rejected(client):
    res = client.get("/api/v1/dashboard",
                     headers={"Authorization": "Bearer not.a.jwt"})
    assert res.status_code == 401


def test_a_token_signed_with_the_wrong_key_is_rejected(client, app):
    import jwt
    forged = jwt.encode({"sub": "analyst", "role": "admin"}, "wrong-key", algorithm="HS256")
    res = client.get("/api/v1/dashboard", headers={"Authorization": f"Bearer {forged}"})
    assert res.status_code == 401


def test_me_returns_the_current_analyst(client, analyst_headers):
    body = client.get("/api/v1/auth/me", headers=analyst_headers).get_json()
    assert body["username"] == "analyst"
    assert "password_hash" not in body


# ── RBAC ───────────────────────────────────────────────────────────────────
def test_viewer_can_read_but_not_investigate(client, viewer_headers, sample_user):
    assert client.get("/api/v1/dashboard", headers=viewer_headers).status_code == 200

    res = client.get(f"/api/v1/investigate/{sample_user}", headers=viewer_headers)
    assert res.status_code == 403
    assert res.get_json()["required_role"] == "analyst"


def test_analyst_cannot_reach_admin_endpoints(client, analyst_headers):
    assert client.get("/api/v1/auth/audit", headers=analyst_headers).status_code == 403
    assert client.post("/api/v1/model/reload", headers=analyst_headers).status_code == 403


def test_admin_has_full_access(client, admin_headers, sample_user):
    assert client.get("/api/v1/auth/audit", headers=admin_headers).status_code == 200
    assert client.get(f"/api/v1/investigate/{sample_user}",
                      headers=admin_headers).status_code == 200


# ── dashboard & profiles ───────────────────────────────────────────────────
def test_dashboard_shape(client, viewer_headers):
    body = client.get("/api/v1/dashboard", headers=viewer_headers).get_json()

    for key in ["total_users", "open_alerts", "severity_distribution",
                "risk_timeline", "top_indicators", "model"]:
        assert key in body
    assert set(body["severity_distribution"]) == {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
    assert body["total_users"] > 0


def test_user_list_paginates_and_filters(client, viewer_headers):
    body = client.get("/api/v1/users?per_page=5", headers=viewer_headers).get_json()
    assert len(body["items"]) <= 5
    assert body["pages"] >= 1

    # Sorted by peak risk, descending.
    peaks = [i["peak_risk"] for i in body["items"]]
    assert peaks == sorted(peaks, reverse=True)

    filtered = client.get("/api/v1/users?severity=CRITICAL",
                          headers=viewer_headers).get_json()
    assert all(i["severity"] == "CRITICAL" for i in filtered["items"])


def test_user_search_matches_the_id(client, viewer_headers, sample_user):
    body = client.get(f"/api/v1/users?search={sample_user}",
                      headers=viewer_headers).get_json()
    assert any(i["user"] == sample_user for i in body["items"])


def test_profile_returns_baseline_and_timeline(client, viewer_headers, sample_user):
    body = client.get(f"/api/v1/users/{sample_user}/profile",
                      headers=viewer_headers).get_json()

    assert body["user"] == sample_user
    assert len(body["baseline"]) == 13          # behavioural features
    assert len(body["timeline"]) == body["active_days"]
    assert 0 <= body["peak_risk"] <= 100


def test_unknown_user_profile_is_404(client, viewer_headers):
    assert client.get("/api/v1/users/NOSUCHUSER/profile",
                      headers=viewer_headers).status_code == 404


# ── alerts & cases ─────────────────────────────────────────────────────────
def test_alerts_respect_the_threshold_and_sort_order(client, viewer_headers):
    body = client.get("/api/v1/alerts?limit=50", headers=viewer_headers).get_json()
    scores = [a["risk_score"] for a in body["items"]]

    assert scores == sorted(scores, reverse=True)
    assert all(s >= body["threshold"] for s in scores)


def test_alert_severity_filter(client, viewer_headers):
    body = client.get("/api/v1/alerts?severity=CRITICAL",
                      headers=viewer_headers).get_json()
    assert all(a["severity"] == "CRITICAL" for a in body["items"])


def test_case_lifecycle(client, analyst_headers, viewer_headers):
    alert = client.get("/api/v1/alerts?limit=1", headers=viewer_headers).get_json()["items"][0]

    created = client.post("/api/v1/alerts/cases", headers=analyst_headers,
                          json={"user": alert["user"], "day": alert["day"],
                                "status": "IN_REVIEW", "notes": "triage"})
    assert created.status_code == 200
    assert created.get_json()["status"] == "IN_REVIEW"

    # Upsert, not duplicate.
    updated = client.post("/api/v1/alerts/cases", headers=analyst_headers,
                          json={"user": alert["user"], "day": alert["day"],
                                "status": "ESCALATED"})
    assert updated.get_json()["id"] == created.get_json()["id"]
    assert updated.get_json()["status"] == "ESCALATED"


def test_case_rejects_an_invalid_status(client, analyst_headers, viewer_headers):
    alert = client.get("/api/v1/alerts?limit=1", headers=viewer_headers).get_json()["items"][0]
    res = client.post("/api/v1/alerts/cases", headers=analyst_headers,
                      json={"user": alert["user"], "day": alert["day"], "status": "NONSENSE"})
    assert res.status_code == 400
    assert "allowed" in res.get_json()


def test_case_rejects_an_unknown_subject_day(client, analyst_headers):
    res = client.post("/api/v1/alerts/cases", headers=analyst_headers,
                      json={"user": "NOSUCHUSER", "day": "2010-01-04"})
    assert res.status_code == 404


# ── investigation & scoring ────────────────────────────────────────────────
def test_investigation_returns_a_complete_case(client, analyst_headers, sample_user):
    body = client.get(f"/api/v1/investigate/{sample_user}",
                      headers=analyst_headers).get_json()

    assert body["user"] == sample_user
    assert len(body["deviations"]) == 13
    assert len(body["risk_contributions"]) == 5      # the five weighted indicators
    assert body["explanation"]["method"] in {"shap", "importance"}
    assert body["explanation"]["features"]
    assert body["severity"] in {"CRITICAL", "HIGH", "MEDIUM", "LOW"}


def test_investigation_honours_an_explicit_day(client, analyst_headers, sample_user):
    peak = client.get(f"/api/v1/investigate/{sample_user}",
                      headers=analyst_headers).get_json()
    other = peak["timeline"][0]["day"]

    body = client.get(f"/api/v1/investigate/{sample_user}?day={other}",
                      headers=analyst_headers).get_json()
    assert body["day"] == other


def test_investigation_of_an_unknown_day_is_404(client, analyst_headers, sample_user):
    res = client.get(f"/api/v1/investigate/{sample_user}?day=1999-01-01",
                     headers=analyst_headers)
    assert res.status_code == 404


def test_score_endpoint_rejects_unknown_features(client, analyst_headers):
    res = client.post("/api/v1/score", headers=analyst_headers,
                      json={"features": {"not_a_feature": 1}})
    assert res.status_code == 400
    assert "not_a_feature" in res.get_json()["unknown"]


def test_score_endpoint_ranks_an_extreme_day_above_a_quiet_one(
    client, analyst_headers, sample_user
):
    quiet = client.post("/api/v1/score", headers=analyst_headers, json={
        "user": sample_user,
        "features": {"files_copied_to_usb": 0, "off_hours_usb": 0,
                     "external_emails_sent": 0, "off_hours_logons": 0,
                     "cloud_job_visits": 0},
    }).get_json()

    extreme = client.post("/api/v1/score", headers=analyst_headers, json={
        "user": sample_user,
        "features": {"files_copied_to_usb": 60, "off_hours_usb": 10,
                     "external_emails_sent": 40, "off_hours_logons": 12,
                     "cloud_job_visits": 50},
    }).get_json()

    assert extreme["risk_score"] > quiet["risk_score"]
    assert extreme["ueba_score"] == pytest.approx(100.0)


def test_features_endpoint_documents_the_contract(client, viewer_headers):
    body = client.get("/api/v1/features", headers=viewer_headers).get_json()
    assert len(body["feature_columns"]) == 16
    assert set(body["risk_weights"]) == {
        "files_copied_to_usb", "off_hours_usb", "external_emails_sent",
        "off_hours_logons", "cloud_job_visits",
    }


# ── exports ────────────────────────────────────────────────────────────────
def test_pdf_export_returns_a_pdf(client, analyst_headers, sample_user):
    res = client.get(f"/api/v1/export/pdf?user={sample_user}", headers=analyst_headers)

    assert res.status_code == 200
    assert res.mimetype == "application/pdf"
    assert res.data.startswith(b"%PDF")
    assert f"Investigation_Report_{sample_user}" in res.headers["Content-Disposition"]


def test_pdf_export_requires_a_user(client, analyst_headers):
    assert client.get("/api/v1/export/pdf", headers=analyst_headers).status_code == 400


def test_pdf_export_is_analyst_only(client, viewer_headers, sample_user):
    res = client.get(f"/api/v1/export/pdf?user={sample_user}", headers=viewer_headers)
    assert res.status_code == 403


def test_excel_export_returns_a_workbook(client, viewer_headers):
    res = client.get("/api/v1/export/excel?min_score=60&limit=100",
                     headers=viewer_headers)

    assert res.status_code == 200
    assert res.data[:2] == b"PK"  # xlsx is a zip container

    import io
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(res.data))
    assert wb.sheetnames == ["Overview", "Risk Summary", "Activity Detail",
                             "Feature Glossary"]


def test_excel_export_of_an_unknown_user_is_404(client, viewer_headers):
    assert client.get("/api/v1/export/excel?user=NOSUCHUSER",
                      headers=viewer_headers).status_code == 404


# ── monitoring ─────────────────────────────────────────────────────────────
def test_recent_activity_is_annotated_with_risk(client, viewer_headers):
    body = client.get("/api/v1/monitor/recent?limit=5", headers=viewer_headers).get_json()
    assert "events" in body
    for event in body["events"]:
        assert {"timestamp", "user", "source", "severity"} <= set(event)


def test_stream_requires_authentication(client):
    assert client.get("/stream").status_code == 401


# ── misc ───────────────────────────────────────────────────────────────────
def test_health_is_public(client):
    body = client.get("/health").get_json()
    assert body["status"] in {"ok", "degraded"}


def test_console_page_is_served(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"Insider Threat" in res.data


def test_audit_log_records_analyst_actions(client, admin_headers, analyst_headers,
                                           sample_user):
    client.get(f"/api/v1/investigate/{sample_user}", headers=analyst_headers)
    entries = client.get("/api/v1/auth/audit", headers=admin_headers).get_json()["entries"]

    assert any(e["action"] == "INVESTIGATE" and e["target"] == sample_user
               for e in entries)
