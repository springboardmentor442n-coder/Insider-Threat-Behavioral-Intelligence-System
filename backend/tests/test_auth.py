"""Tests for authentication and role-based access control.

These are the tests that matter most in this project. A bug in the risk-scoring
maths produces a wrong number. A bug in here produces an unauthorised person
reading behavioural surveillance data on a thousand employees.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.models import UserRole
from backend.app.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def _unique_email() -> str:
    """Tests must not collide with each other or with previous runs."""
    return f"test_{uuid.uuid4().hex[:12]}@example.com"


def _register(client: TestClient, role: UserRole = UserRole.SECURITY_ANALYST):
    """Register a user and return (email, password, response)."""
    email = _unique_email()
    # Must satisfy the password policy: 12+ chars, upper, lower, digit, symbol,
    # and no common wordlist term. The old fixture ("correct-horse-battery") now
    # fails registration with a 422 - which is the policy doing its job, not a
    # regression.
    password = "Tr0ub4dor-Horse!"  # noqa: S105 - test fixture
    response = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "full_name": "Test Operator",
            "password": password,
            "role": role.value,
        },
    )
    return email, password, response


def _login(client: TestClient, email: str, password: str) -> str | None:
    """Log in and return the bearer token, or None on failure."""
    response = client.post(
        "/api/auth/login",
        data={"username": email, "password": password},  # OAuth2 form encoding
    )
    if response.status_code != 200:
        return None
    return response.json()["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


# ===========================================================================
# Password hashing
# ===========================================================================


def test_password_hash_is_not_the_password() -> None:
    """The stored hash must not be the plaintext, and must verify correctly."""
    password = "my-secret-password"  # noqa: S105
    hashed = hash_password(password)

    assert hashed != password
    assert hashed.startswith("$2b$")  # bcrypt marker
    assert verify_password(password, hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_same_password_produces_different_hashes() -> None:
    """bcrypt salts every hash.

    Two users with the same password must not share a hash - otherwise an
    attacker who cracks one has cracked both, and identical hashes in a leaked
    table reveal which users share a password.
    """
    password = "identical-password"  # noqa: S105
    assert hash_password(password) != hash_password(password)


def test_overlong_password_is_rejected_not_silently_truncated() -> None:
    """bcrypt cannot hash more than 72 bytes; we must raise, not truncate.

    Silent truncation would be a genuine vulnerability: a 200-character
    passphrase would be validated on only its first 72 bytes, and the user would
    believe they had far more entropy than they actually did.
    """
    with pytest.raises(ValueError, match="72"):
        hash_password("x" * 100)


# ===========================================================================
# JWT
# ===========================================================================


def test_jwt_roundtrip_carries_subject_and_role() -> None:
    token = create_access_token(subject="42", role="security_analyst")
    payload = decode_access_token(token)

    assert payload is not None
    assert payload["sub"] == "42"
    assert payload["role"] == "security_analyst"
    assert "exp" in payload


def test_tampered_jwt_is_rejected() -> None:
    """Flipping any byte of the payload must break signature verification.

    This is the whole point of signing. If a modified token still decoded, a
    user could rewrite their own role claim to 'administrator'.
    """
    token = create_access_token(subject="42", role="security_analyst")
    header, payload, signature = token.split(".")
    tampered = f"{header}.{payload[:-4]}XXXX.{signature}"

    assert decode_access_token(tampered) is None


def test_garbage_token_is_rejected() -> None:
    assert decode_access_token("not-a-jwt-at-all") is None
    assert decode_access_token("") is None


# ===========================================================================
# Registration and login
# ===========================================================================


def test_register_then_login(client: TestClient) -> None:
    email, password, response = _register(client)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == email
    assert body["role"] == "security_analyst"
    assert body["is_active"] is True

    # The hash must NEVER appear in an API response.
    assert "hashed_password" not in body
    assert "password" not in body

    token = _login(client, email, password)
    assert token is not None


def test_duplicate_email_is_rejected(client: TestClient) -> None:
    email, password, first = _register(client)
    assert first.status_code == 201

    duplicate = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "full_name": "Someone Else",
            "password": "a-different-password",
            "role": "security_analyst",
        },
    )
    assert duplicate.status_code == 409


def test_login_with_wrong_password_fails(client: TestClient) -> None:
    email, _password, _ = _register(client)
    assert _login(client, email, "definitely-the-wrong-password") is None


def test_login_error_does_not_reveal_whether_the_account_exists(
    client: TestClient,
) -> None:
    """Wrong password and unknown user must be indistinguishable.

    If they differed, an attacker could enumerate valid accounts just by reading
    the error message.
    """
    email, _password, _ = _register(client)

    wrong_password = client.post(
        "/api/auth/login",
        data={"username": email, "password": "wrong"},
    )
    no_such_user = client.post(
        "/api/auth/login",
        data={"username": _unique_email(), "password": "wrong"},
    )

    assert wrong_password.status_code == no_such_user.status_code == 401
    assert wrong_password.json()["detail"] == no_such_user.json()["detail"]


def test_weak_password_is_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/auth/register",
        json={
            "email": _unique_email(),
            "full_name": "Test",
            "password": "short",  # under the 8-char minimum
            "role": "security_analyst",
        },
    )
    assert response.status_code == 422  # pydantic validation


# ===========================================================================
# Authentication enforcement
# ===========================================================================


def test_protected_endpoint_requires_a_token(client: TestClient) -> None:
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/data/employees").status_code == 401
    assert client.get("/api/data/stats").status_code == 401


def test_protected_endpoint_rejects_a_bogus_token(client: TestClient) -> None:
    response = client.get("/api/auth/me", headers=_auth("garbage-token"))
    assert response.status_code == 401


def test_me_returns_the_authenticated_user(client: TestClient) -> None:
    email, password, _ = _register(client)
    token = _login(client, email, password)

    response = client.get("/api/auth/me", headers=_auth(token))
    assert response.status_code == 200
    assert response.json()["email"] == email


# ===========================================================================
# RBAC - the part that actually matters
# ===========================================================================


def test_analyst_cannot_see_ground_truth(client: TestClient) -> None:
    """A Security Analyst must be refused the insider answer key.

    This is the central authorisation rule of the system. An analyst who can
    read `is_insider` is not investigating - and any measurement of how
    effectively analysts find insiders becomes meaningless.
    """
    email, password, _ = _register(client, role=UserRole.SECURITY_ANALYST)
    token = _login(client, email, password)

    response = client.get("/api/data/employees/AAF0535", headers=_auth(token))

    # 403 = "I know who you are, and you may not do this."
    # (404 would also be acceptable if the employee is absent, but the
    #  authorisation check runs FIRST - so 403 is what we must see.)
    assert response.status_code == 403
    assert "not permitted" in response.json()["detail"].lower()


def test_soc_engineer_cannot_see_ground_truth(client: TestClient) -> None:
    email, password, _ = _register(client, role=UserRole.SOC_ENGINEER)
    token = _login(client, email, password)

    response = client.get("/api/data/employees/AAF0535", headers=_auth(token))
    assert response.status_code == 403


def test_manager_may_see_ground_truth(client: TestClient) -> None:
    """A Security Manager IS permitted - so the check is a real rule, not a wall."""
    email, password, _ = _register(client, role=UserRole.SECURITY_MANAGER)
    token = _login(client, email, password)

    response = client.get("/api/data/employees/AAF0535", headers=_auth(token))

    # 403 would mean the rule is wrong. 200 (found) or 404 (not ingested yet)
    # both mean authorisation passed, which is what this test asserts.
    assert response.status_code != 403


def test_administrator_may_see_ground_truth(client: TestClient) -> None:
    email, password, _ = _register(client, role=UserRole.ADMINISTRATOR)
    token = _login(client, email, password)

    response = client.get("/api/data/employees/AAF0535", headers=_auth(token))
    assert response.status_code != 403


def test_any_authenticated_role_may_list_employees(client: TestClient) -> None:
    """The roster itself is not restricted - only the ground-truth labels are."""
    for role in UserRole:
        email, password, _ = _register(client, role=role)
        token = _login(client, email, password)

        response = client.get("/api/data/employees", headers=_auth(token))
        assert response.status_code == 200, f"{role.value} was refused the roster"