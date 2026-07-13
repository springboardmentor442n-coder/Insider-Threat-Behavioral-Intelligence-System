"""Tests for operator profile management (spec Module 2).

The interesting tests here are not "can you change your name". They are the three
privilege guards, each of which would hand an attacker the platform if it were
missing.
"""

from __future__ import annotations

import uuid

from fastapi import status
from fastapi.testclient import TestClient

PW = "Tr0ub4dor-Horse!"


def _make(client: TestClient, role: str = "security_analyst"):
    """Register + log in. Returns (email, auth_headers, user_id).

    The id comes straight from the registration response. An earlier version of
    this helper searched GET /api/users for the new account instead - which broke
    the moment the test database accumulated more than one page of users, because
    the newest account fell off the end of the first 50 rows. Looking a record up
    by scanning a paginated list is a bug waiting for a bigger table.
    """
    email = f"u{uuid.uuid4().hex[:8]}@dtaa.com"
    reg = client.post("/api/auth/register", json={
        "email": email, "full_name": "Op", "password": PW, "role": role,
    })
    assert reg.status_code == 201, reg.text
    user_id = reg.json()["id"]
    tok = client.post("/api/auth/login",
                      data={"username": email, "password": PW}).json()
    return email, {"Authorization": f"Bearer {tok['access_token']}"}, user_id


def test_a_user_can_update_their_own_name(client: TestClient) -> None:
    _, h, _uid = _make(client)
    r = client.patch("/api/users/me", json={"full_name": "Renamed"}, headers=h)
    assert r.status_code == status.HTTP_200_OK
    assert r.json()["full_name"] == "Renamed"


def test_a_user_CANNOT_promote_themselves(client: TestClient) -> None:
    """THE PRIVILEGE ESCALATION TEST.

    If PATCH /me accepted a `role` field, the lowest-privileged account on the
    platform - a Security Analyst - would promote itself to Administrator in one
    request, and every RBAC check in the codebase would become decorative.

    The defence is that UserSelfUpdate HAS NO ROLE FIELD. Pydantic ignores the
    extra key, so the role is untouched. A field that does not exist cannot be
    mis-validated, forgotten about, or re-added by someone who did not know why it
    was missing.
    """
    _, h, _uid = _make(client, role="security_analyst")

    r = client.patch(
        "/api/users/me",
        json={"full_name": "Attacker", "role": "administrator"},
        headers=h,
    )
    assert r.status_code == status.HTTP_200_OK

    # The name changed. THE ROLE DID NOT.
    assert r.json()["full_name"] == "Attacker"
    assert r.json()["role"] == "security_analyst", (
        "A SECURITY ANALYST PROMOTED THEMSELVES TO ADMINISTRATOR through the "
        "profile endpoint. Every RBAC check in this codebase is now theatre."
    )

    # And confirm it against a fresh read, not just the response body.
    me = client.get("/api/auth/me", headers=h).json()
    assert me["role"] == "security_analyst"


def test_a_user_cannot_change_their_password_via_the_profile_endpoint(
    client: TestClient,
) -> None:
    """Password changes must require the CURRENT password.

    Otherwise a stolen fifteen-minute access token becomes a permanent account
    takeover: the attacker simply sets a new password and locks the real user out.
    """
    email, h, _uid = _make(client)
    client.patch("/api/users/me", json={"password": "Hijacked-Pass1!"}, headers=h)

    # The original password must still work.
    r = client.post("/api/auth/login", data={"username": email, "password": PW})
    assert r.status_code == status.HTTP_200_OK, (
        "the password was changed through the PROFILE endpoint, with no knowledge "
        "of the current password. A stolen token is now a permanent takeover."
    )


def test_only_an_administrator_may_list_operators(client: TestClient) -> None:
    """The operator roster is itself sensitive: it tells an attacker exactly which
    accounts to target, and which of them can read the ground-truth insider labels.
    """
    _, analyst, _a = _make(client, role="security_analyst")
    assert client.get("/api/users", headers=analyst).status_code == (
        status.HTTP_403_FORBIDDEN
    )

    _, admin, admin_id = _make(client, role="administrator")
    assert client.get("/api/users", headers=admin).status_code == status.HTTP_200_OK


def test_an_administrator_may_change_someone_elses_role(client: TestClient) -> None:
    _, admin, admin_id = _make(client, role="administrator")
    victim_email, _vh, victim_id = _make(client, role="security_analyst")

    r = client.patch(
        f"/api/users/{victim_id}",
        json={"role": "soc_engineer"},
        headers=admin,
    )
    assert r.status_code == status.HTTP_200_OK
    assert r.json()["role"] == "soc_engineer"


def test_an_administrator_cannot_change_their_OWN_role(client: TestClient) -> None:
    """Even an admin. This is not about trusting admins - it is about limiting what
    a STOLEN admin token can do quietly, and forcing a second human into the loop.
    """
    email, admin, admin_id = _make(client, role="administrator")
    r = client.patch(
        f"/api/users/{admin_id}",
        json={"role": "security_analyst"},
        headers=admin,
    )
    assert r.status_code == status.HTTP_403_FORBIDDEN


def test_an_administrator_cannot_deactivate_themselves(client: TestClient) -> None:
    _, admin, admin_id = _make(client, role="administrator")
    r = client.patch(
        f"/api/users/{admin_id}",
        json={"is_active": False},
        headers=admin,
    )
    assert r.status_code == status.HTTP_403_FORBIDDEN


def test_an_administrator_can_unlock_a_locked_out_account(client: TestClient) -> None:
    """Five typos should not cost fifteen minutes if an admin is sitting right there."""
    _, admin, admin_id = _make(client, role="administrator")
    victim_email, _vh, victim_id = _make(client, role="security_analyst")

    for _ in range(5):
        client.post("/api/auth/login",
                    data={"username": victim_email, "password": "Wrong-Pass1!"})

    # Locked out, even with the right password.
    r = client.post("/api/auth/login", data={"username": victim_email, "password": PW})
    assert r.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    r = client.patch(f"/api/users/{victim_id}", json={"unlock": True}, headers=admin)
    assert r.status_code == status.HTTP_200_OK

    # And now they can get back in.
    r = client.post("/api/auth/login", data={"username": victim_email, "password": PW})
    assert r.status_code == status.HTTP_200_OK