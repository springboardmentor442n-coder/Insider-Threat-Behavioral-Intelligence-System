import sys
from pathlib import Path
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app import app
from backend.services.live_threat_analyzer_service import calculate_risk_score_and_level

client = TestClient(app)


def test_live_inference_flow():
    print("==========================================================================")
    print("TESTING LIVE FEATURE INFERENCE & CUSTOM EMPLOYEE THREAT ANALYZER")
    print("==========================================================================")

    # 1. Register and login with a unique test account
    test_user = "live_test_user_2026"
    test_pass = "Password123!"
    client.post(
        "/auth/register",
        json={"username": test_user, "password": test_pass, "role": "SOC Analyst"},
    )
    res_login = client.post(
        "/auth/token",
        data={"username": test_user, "password": test_pass},
    )
    assert res_login.status_code == 200, f"Login failed: {res_login.status_code} - {res_login.text}"
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Test /threat-analysis/analyze Endpoint
    payload_exfil = {
        "employee_id": "CUSTOM-EXFIL-001",
        "employee_name": "Marcus Vance",
        "department": "R&D Engineering",
        "role": "Architect",
        "features": {
            "total_events": 4500,
            "active_days": 220,
            "unique_pcs": 4,
            "unique_sources": 3,
            "total_logins": 500,
            "midnight_activity": 45,
            "after_hours_activity": 120,
            "weekend_activity": 35,
            "device_events": 45,
            "file_events": 320,
            "unique_files": 190,
            "emails_sent": 200,
            "web_events": 1900,
            "unique_urls": 220,
            "average_hour": 14.2,
            "earliest_hour": 5.5,
            "latest_hour": 23.0,
            "openness": 35,
            "conscientiousness": 25,
            "extraversion": 30,
            "agreeableness": 28,
            "neuroticism": 32,
        },
    }

    res_eval = client.post(
        "/threat-analysis/analyze",
        json=payload_exfil,
        headers=headers,
    )
    assert res_eval.status_code == 200, f"Expected 200, got {res_eval.status_code}"
    data_eval = res_eval.json()

    assert data_eval["inference_status"] == "success"
    assert "risk_score" in data_eval
    assert "risk_level" in data_eval
    assert data_eval["models_evaluated"] == 7
    assert len(data_eval["model_results"]) == 7
    assert "vector_percentiles" in data_eval["layer2_verification"]
    print("1. POST /threat-analysis/analyze Live ML Inference: PASS")
    print(
        f"   -> Risk Score: {data_eval['risk_score']} | Risk Level: {data_eval['risk_level']} | Triggered: {data_eval['models_triggered']}/7"
    )

    # 3. Test Invalid Input Validation (Extra Unknown Feature)
    bad_payload = {
        "employee_id": "CUSTOM-BAD",
        "features": {
            "after_hours_activity": 100,
            "invalid_unknown_feature": 9999,
        },
    }
    res_bad = client.post("/threat-analysis/analyze", json=bad_payload, headers=headers)
    assert res_bad.status_code == 400, f"Expected 400 for unknown feature, got {res_bad.status_code}"
    print("2. Invalid Feature Schema Validation Error (400): PASS")

    # 4. Test Risk Boundary Scoring (Section 14 H)
    s_low, l_low = calculate_risk_score_and_level(0.0, 0)
    assert l_low == "LOW"

    s_med, l_med = calculate_risk_score_and_level(50.0, 0)
    assert l_med == "MEDIUM"

    s_high, l_high = calculate_risk_score_and_level(50.0, 3)
    assert l_high == "HIGH"

    s_crit, l_crit = calculate_risk_score_and_level(100.0, 6)
    assert l_crit == "CRITICAL"
    print("3. Authoritative Risk Level Boundaries (LOW, MEDIUM, HIGH, CRITICAL): PASS")

    # 5. Test AJF0370 Regression
    res_ajf = client.get("/verification/employee/AJF0370", headers=headers)
    assert res_ajf.status_code == 200, f"Expected 200 for AJF0370, got {res_ajf.status_code}"
    ajf_data = res_ajf.json()
    assert ajf_data["risk_score"] == 100.0
    assert ajf_data["risk_level"].upper() == "CRITICAL"
    assert ajf_data["suspicious_model_count"] == 7
    assert ajf_data["consensus_percentage"] == 100.0
    print("4. AJF0370 Regression Test (100.0 / CRITICAL / 7 of 7 / 100.0%): PASS")

    print("==========================================================================")
    print("ALL LIVE THREAT ANALYZER & REGRESSION TESTS PASSED (100%)")
    print("==========================================================================")


if __name__ == "__main__":
    test_live_inference_flow()
