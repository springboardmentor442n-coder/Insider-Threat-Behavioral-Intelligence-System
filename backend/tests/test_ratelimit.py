"""Rate limiting is DISABLED for the rest of the test suite. So it gets tested here.

Turning a security control off so the tests pass, and then never testing it, is
exactly how security controls quietly stop working. The suite disables the limiter
because forty registrations and sixty logins is not the traffic the limits exist to
stop - but the limits themselves have to be proven, or they are decoration.

These tests enable the limiter explicitly and confirm it fires.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi import status
from fastapi.testclient import TestClient

PW = "Tr0ub4dor-Horse!"


@pytest.fixture
def limited_client() -> TestClient:
    """A client with rate limiting ON.

    The limiter is a module-level singleton, so it is toggled directly rather than
    by rebuilding the app - and reset afterwards, or every subsequent test in the
    session would inherit the limits.
    """
    from backend.app.main import app
    from backend.app.ratelimit import limiter

    limiter.enabled = True
    limiter.reset()
    try:
        yield TestClient(app)
    finally:
        limiter.enabled = False
        limiter.reset()


def test_login_is_rate_limited(limited_client: TestClient) -> None:
    """PASSWORD SPRAYING is the attack this stops.

    The account lockout (5 failures, 15 minutes) defends ONE account against a
    thousand password guesses. It does nothing whatsoever against the attack that
    actually works: ONE password - "Autumn2025!" - tried against a THOUSAND accounts.

    Every account sees a single failed login. No lockout fires anywhere. Nothing in
    the logs looks unusual. And in an organisation of any size, somebody is using
    that password.

    Lockout is per-ACCOUNT. Rate limiting is per-IP. They stop different attacks,
    and neither one substitutes for the other.
    """
    limit = 10
    codes = []

    # Spray: a different account each time, so the LOCKOUT never fires.
    for i in range(limit + 3):
        r = limited_client.post(
            "/api/auth/login",
            data={"username": f"victim{i}@dtaa.com", "password": "Autumn2025!"},
        )
        codes.append(r.status_code)

    assert status.HTTP_429_TOO_MANY_REQUESTS in codes, (
        "12 login attempts against 12 DIFFERENT accounts from one IP were all "
        "allowed through. No account lockout fires - each account saw exactly one "
        "failed login. This is password spraying, and it is how organisations "
        "actually get breached."
    )

    # The first `limit` must have been allowed (401 - wrong password), and the
    # spray must have been cut off after that.
    assert codes[0] == status.HTTP_401_UNAUTHORIZED
    assert codes[-1] == status.HTTP_429_TOO_MANY_REQUESTS


def test_registration_is_rate_limited(limited_client: TestClient) -> None:
    """Nobody legitimately creates six operator accounts in an hour.

    An attacker who has compromised one account, and is quietly seeding themselves
    a few backdoor accounts before anyone notices, does.
    """
    codes = []
    for _ in range(7):
        r = limited_client.post(
            "/api/auth/register",
            json={
                "email": f"u{uuid.uuid4().hex[:8]}@dtaa.com",
                "full_name": "Op",
                "password": PW,
                "role": "security_analyst",
            },
        )
        codes.append(r.status_code)

    assert status.HTTP_429_TOO_MANY_REQUESTS in codes, (
        "seven operator accounts were created from one IP without complaint"
    )