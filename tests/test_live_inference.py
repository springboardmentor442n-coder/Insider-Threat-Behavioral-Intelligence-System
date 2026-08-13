import sys
from pathlib import Path
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app import app

client = TestClient(app)


def test_live_inference_flow():
    print("==========================================================================")
    print("TESTING LIVE FEATURE INFERENCE & CUSTOM EMPLOYEE REGISTRATION")
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

    # 2. Test /verification/evaluate-custom (Exfiltration Payload)
    payload_exfil = {
        "user": "EMP_EXFIL_TEST",
        "name": "Marcus Vance",
        "department": "R&D",
        "role": "Architect",
        "after_hours_activity": 120,
        "midnight_activity": 45,
        "weekend_activity": 35,
        "device_events": 45,
        "file_events": 320,
        "unique_files": 190,
        "unique_pcs": 4,
        "web_events": 1900,
        "unique_urls": 220,
        "emails_sent": 200,
        "total_events": 4500,
    }

    res_eval = client.post(
        "/verification/evaluate-custom",
        json=payload_exfil,
        headers=headers,
    )
    assert res_eval.status_code == 200, f"Expected 200, got {res_eval.status_code}"
    data_eval = res_eval.json()

    assert "risk_score" in data_eval
    assert "risk_level" in data_eval
    assert "model_predictions" in data_eval
    assert len(data_eval["model_predictions"]) == 7
    assert data_eval["risk_level"] in ["Critical", "High", "Medium", "Low"]
    assert 0.0 <= data_eval["risk_score"] <= 100.0
    print("1. POST /verification/evaluate-custom Live ML Inference: PASS")
    print(
        f"   -> Risk Score: {data_eval['risk_score']} | Risk Level: {data_eval['risk_level']} | Consensus: {data_eval['consensus_percentage']}%"
    )

    # 3. Test /verification/add-custom
    res_add = client.post(
        "/verification/add-custom",
        json=payload_exfil,
        headers=headers,
    )
    assert res_add.status_code in [200, 201], f"Expected 200/201, got {res_add.status_code}"
    data_add = res_add.json()
    assert data_add["user"] == "EMP_EXFIL_TEST"
    print("2. POST /verification/add-custom Registration: PASS")

    # 4. Verify employee exists in individual evidence lookup
    res_get = client.get(
        "/verification/employee/EMP_EXFIL_TEST",
        headers=headers,
    )
    assert res_get.status_code == 200, f"Expected 200, got {res_get.status_code}"
    print("3. GET /verification/employee/EMP_EXFIL_TEST evidence lookup: PASS")

    print("==========================================================================")
    print("LIVE INFERENCE & CUSTOM EMPLOYEE REGISTRATION TESTS PASSED (100%)")
    print("==========================================================================")


if __name__ == "__main__":
    test_live_inference_flow()
