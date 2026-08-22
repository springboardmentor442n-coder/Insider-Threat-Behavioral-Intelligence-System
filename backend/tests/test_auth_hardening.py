"""Security tests for the hardened auth layer.

Every one of these is a hole that was OPEN until now. On a product that surveils a
thousand employees and stores the ground-truth list of who the insiders are, an
attacker who compromises a Security Manager account can read every behavioural
profile, see the labels, and - most usefully to them - find out whether they
themselves are being watched. The account is worth attacking. The auth has to be
worth something.
"""

from __future__ import annotations

import uuid

from fastapi import status
from fastapi.testclient import TestClient

GOOD_PASSWORD = "Tr0ub4dor-Horse!"


def _register(client: TestClient, password: str = GOOD_PASSWORD, **kw):
    email = kw.pop("email", f"u{uuid.uuid4().hex[:8]}@dtaa.com")
    return client.post(
        "/api/auth/register",
        json={
            "email": email,
            "full_name": "Test Operator",
            "password": password,
            "role": kw.pop("role", "security_analyst"),
        },
    ), email


def _login(client: TestClient, email: str, password: str):
    return client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
    )


# ===========================================================================
# BRUTE FORCE
# ===========================================================================


def test_account_locks_after_five_failed_logins(client: TestClient) -> None:
    """/login must not be an unlimited password-guessing oracle.

    Without a lockout, an attacker with a wordlist and a weekend gets in - and
    nothing in the logs looks unusual, because every individual request is a
    perfectly ordinary failed login. Five strikes, then fifteen minutes.
    """
    _, email = _register(client)

    for attempt in range(5):
        r = _login(client, email, "WrongPassword123!")
        assert r.status_code == status.HTTP_401_UNAUTHORIZED, (
            f"attempt {attempt + 1} should be 401"
        )

    # The sixth attempt must be REFUSED, not merely wrong.
    r = _login(client, email, "WrongPassword123!")
    assert r.status_code == status.HTTP_429_TOO_MANY_REQUESTS, (
        "the account should be LOCKED after 5 failures, not simply rejected again. "
        "Without a lock, guessing is unlimited."
    )

    # And - critically - the CORRECT password must ALSO be refused while locked.
    # If it were not, the lock would be decorative: an attacker who guessed right on
    # attempt 6 would sail straight in.
    r = _login(client, email, GOOD_PASSWORD)
    assert r.status_code == status.HTTP_429_TOO_MANY_REQUESTS, (
        "a locked account must refuse even the CORRECT password. Otherwise the "
        "lockout does nothing at all."
    )


def test_a_successful_login_clears_the_failure_counter(client: TestClient) -> None:
    """Four mistakes then a success must not leave the user one typo from a lock."""
    _, email = _register(client)

    for _ in range(4):
        _login(client, email, "WrongPassword123!")

    r = _login(client, email, GOOD_PASSWORD)
    assert r.status_code == status.HTTP_200_OK

    # Slate wiped: four more failures must not lock (that would be 4, not 8).
    for _ in range(4):
        r = _login(client, email, "WrongPassword123!")
        assert r.status_code == status.HTTP_401_UNAUTHORIZED


# ===========================================================================
# TOKEN TYPE CONFUSION - the one that would actually hurt
# ===========================================================================


def test_a_refresh_token_cannot_be_used_as_an_access_token(client: TestClient) -> None:
    """THE MOST IMPORTANT TEST IN THIS FILE.

    An access token and a refresh token are both JWTs, signed with the same key,
    structurally identical. The ONLY thing distinguishing them is the `type` claim.

    Without that check, an attacker who steals a refresh token presents it as an
    access token and converts a fifteen-minute window into SEVEN DAYS of full API
    access. It is a devastating bug and it is completely invisible - everything
    works, which is exactly why nobody notices.
    """
    _, email = _register(client)
    tokens = _login(client, email, GOOD_PASSWORD).json()

    refresh = tokens["refresh_token"]
    assert refresh, "login must return a refresh token"

    # Present the REFRESH token where an ACCESS token belongs.
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {refresh}"})
    assert r.status_code == status.HTTP_401_UNAUTHORIZED, (
        "a REFRESH token was accepted as an ACCESS token. An attacker who steals "
        "one now has seven days of API access instead of fifteen minutes."
    )


def test_an_access_token_cannot_be_used_to_refresh(client: TestClient) -> None:
    """The check must run in both directions."""
    _, email = _register(client)
    tokens = _login(client, email, GOOD_PASSWORD).json()

    r = client.post(
        "/api/auth/refresh",
        json={"refresh_token": tokens["access_token"]},
    )
    assert r.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_issues_a_working_access_token(client: TestClient) -> None:
    """The whole point: renew the session without re-entering a password."""
    _, email = _register(client)
    tokens = _login(client, email, GOOD_PASSWORD).json()

    r = client.post(
        "/api/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert r.status_code == status.HTTP_200_OK

    new_access = r.json()["access_token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {new_access}"})
    assert me.status_code == status.HTTP_200_OK
    assert me.json()["email"] == email


# ===========================================================================
# REVOCATION - "log out" must actually mean something
# ===========================================================================


def test_logout_actually_revokes_the_token(client: TestClient) -> None:
    """Before this existed, logging out was a LIE.

    A JWT is self-validating: the server checks the signature and the expiry and
    asks nobody's permission. So "log out" meant "delete the token from your own
    browser" - and a token that had already been copied stayed perfectly valid for
    its full lifetime. There was no way to stop it.
    """
    _, email = _register(client)
    tokens = _login(client, email, GOOD_PASSWORD).json()
    access = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access}"}

    # It works before logout.
    assert client.get("/api/auth/me", headers=headers).status_code == 200

    r = client.post(
        "/api/auth/logout",
        json={"refresh_token": tokens["refresh_token"]},
        headers=headers,
    )
    assert r.status_code == status.HTTP_204_NO_CONTENT

    # THE SAME TOKEN MUST NOW FAIL.
    r = client.get("/api/auth/me", headers=headers)
    assert r.status_code == status.HTTP_401_UNAUTHORIZED, (
        "the access token still works after logout. Logging out did nothing - "
        "an attacker holding a copy of that token keeps their access."
    )

    # And the refresh token must not resurrect it.
    r = client.post(
        "/api/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert r.status_code == status.HTTP_401_UNAUTHORIZED, (
        "the REFRESH token survived logout. The attacker just mints a new access "
        "token and carries on for seven days."
    )


# ===========================================================================
# PASSWORD POLICY
# ===========================================================================


def test_registration_rejects_weak_passwords(client: TestClient) -> None:
    """Before this, register() accepted "a"."""
    for weak, why in [
        ("a", "far too short"),
        ("password", "no digit, no symbol, no uppercase, and it is 'password'"),
        ("Password1", "no symbol, too short, contains 'password'"),
        ("aaaaaaaaaaaa", "twelve chars but no uppercase/digit/symbol"),
        ("Passw0rd123!", "long and complex - and in every wordlist on earth"),
    ]:
        r, _ = _register(client, password=weak)
        assert r.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, (
            f"the password {weak!r} was ACCEPTED. It is {why}."
        )


def test_registration_accepts_a_strong_password(client: TestClient) -> None:
    r, _ = _register(client, password="Tr0ub4dor-Horse!")
    assert r.status_code == status.HTTP_201_CREATED


def test_change_password_requires_the_current_one(client: TestClient) -> None:
    """Otherwise a stolen 15-minute token becomes a permanent account takeover.

    An attacker with a leaked access token would simply change the victim's
    password, locking the real user out of their own account for good.
    """
    _, email = _register(client)
    tokens = _login(client, email, GOOD_PASSWORD).json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    r = client.post(
        "/api/auth/change-password",
        json={"current_password": "not-the-password", "new_password": "N3w-Passphrase!"},
        headers=headers,
    )
    assert r.status_code == status.HTTP_401_UNAUTHORIZED, (
        "the password was changed WITHOUT knowing the current one. A stolen "
        "fifteen-minute token is now a permanent account takeover."
    )


def test_change_password_works_and_the_old_one_stops(client: TestClient) -> None:
    _, email = _register(client)
    tokens = _login(client, email, GOOD_PASSWORD).json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    new_pw = "C0rrect-Battery-Staple!"
    r = client.post(
        "/api/auth/change-password",
        json={"current_password": GOOD_PASSWORD, "new_password": new_pw},
        headers=headers,
    )
    assert r.status_code == status.HTTP_204_NO_CONTENT

    assert _login(client, email, GOOD_PASSWORD).status_code == 401
    assert _login(client, email, new_pw).status_code == 200


def test_change_password_enforces_the_policy(client: TestClient) -> None:
    _, email = _register(client)
    tokens = _login(client, email, GOOD_PASSWORD).json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    r = client.post(
        "/api/auth/change-password",
        json={"current_password": GOOD_PASSWORD, "new_password": "weak"},
        headers=headers,
    )
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY