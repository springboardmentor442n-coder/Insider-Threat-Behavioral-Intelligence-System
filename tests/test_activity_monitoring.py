import sys
from pathlib import Path
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(r"C:\Users\kabra\OneDrive\Desktop\insider-threat-behavioral-intelligence-system")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app import app
client = TestClient(app)

def test_activity_monitoring_flow():
    print("==========================================================================")
    print("TESTING MODULE 2: ACTIVITY MONITORING SERVICE & APIS")
    print("==========================================================================")

    # 1. Login to get token
    res_login = client.post("/api/v1/auth/login", data={"username": "testanalyst01", "password": "Password123!"})
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Activity Summary
    res_sum = client.get("/api/v1/activity/summary", headers=headers)
    assert res_sum.status_code == 200, f"Expected 200, got {res_sum.status_code}"
    print("1. Activity Summary API: PASS")

    # 3. Activity Types
    res_types = client.get("/api/v1/activity/types", headers=headers)
    assert res_types.status_code == 200, f"Expected 200, got {res_types.status_code}"
    types = res_types.json()
    assert "logon" in types or "device" in types
    print("2. Activity Types API: PASS")

    # 4. Activity Statistics
    res_stats = client.get("/api/v1/activity/statistics", headers=headers)
    assert res_stats.status_code == 200, f"Expected 200, got {res_stats.status_code}"
    print("3. Activity Statistics API: PASS")

    # 5. Activity Timeline
    res_tl = client.get("/api/v1/activity/timeline", headers=headers)
    assert res_tl.status_code == 200, f"Expected 200, got {res_tl.status_code}"
    print("4. Activity Timeline API: PASS")

    # 6. Employee Specific Activity
    res_emp = client.get("/api/v1/activity/employee/AJF0370", headers=headers)
    assert res_emp.status_code == 200, f"Expected 200, got {res_emp.status_code}"
    print("5. Employee Specific Activity API (AJF0370): PASS")

    print("==========================================================================")
    print("MODULE 2 (ACTIVITY MONITORING) TESTS PASSED WITH 100% SUCCESS!")
    print("==========================================================================")

if __name__ == "__main__":
    test_activity_monitoring_flow()
