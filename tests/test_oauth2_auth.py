import sys
from pathlib import Path
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(r"C:\Users\kabra\OneDrive\Desktop\insider-threat-behavioral-intelligence-system")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app import app
client = TestClient(app)

def test_oauth2_login_flow():
    print("==========================================================================")
    print("TESTING MODULE 1: OAUTH2 AUTHENTICATION & RBAC")
    print("==========================================================================")

    # 1. Valid Login via /token endpoint
    res_login = client.post("/api/v1/auth/token", data={"username": "testanalyst01", "password": "Password123!"})
    assert res_login.status_code == 200, f"Expected 200, got {res_login.status_code}"
    token_data = res_login.json()
    assert "access_token" in token_data, "access_token missing from OAuth2 login response!"
    token = token_data["access_token"]
    print("1. Valid Login via OAuth2 /token endpoint: PASS")

    # 2. Invalid Password
    res_inv = client.post("/api/v1/auth/token", data={"username": "testanalyst01", "password": "WrongPassword"})
    assert res_inv.status_code == 401, f"Expected 401 for wrong password, got {res_inv.status_code}"
    print("2. Invalid Password Error Handling (401): PASS")

    # 3. Authenticated /me endpoint
    headers = {"Authorization": f"Bearer {token}"}
    res_me = client.get("/api/v1/auth/me", headers=headers)
    assert res_me.status_code == 200, f"Expected 200 for /me, got {res_me.status_code}"
    user_info = res_me.json()
    assert user_info["username"] == "testanalyst01"
    print(f"3. Authenticated /me endpoint user info: PASS ({user_info['role']})")

    # 4. Registration
    reg_user = "test_oauth_user_99"
    res_reg = client.post("/api/v1/auth/register", json={"username": reg_user, "password": "Password123!", "role": "SOC Engineer"})
    assert res_reg.status_code in [201, 400], "Unexpected status code for register"
    print("4. User Registration endpoint: PASS")

    print("==========================================================================")
    print("MODULE 1 (OAUTH2 AUTHENTICATION) TESTS PASSED WITH 100% SUCCESS!")
    print("==========================================================================")

if __name__ == "__main__":
    test_oauth2_login_flow()
