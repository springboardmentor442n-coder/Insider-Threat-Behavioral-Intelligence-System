"""Shared pytest configuration.

WHY THIS FILE EXISTS - a real bug, caught by running the tests on a clean
database:

The app creates its tables in FastAPI's `lifespan` handler. But
`TestClient(app)` does NOT fire lifespan events unless it is used as a context
manager (`with TestClient(app) as client:`). So under pytest, the tables were
never created, and every test that touched the database failed with:

    relation "security_users" does not exist

This did not show up during development only because the ingestion script had
already created the tables as a side effect. The tests were quietly depending on
leftover state from a previous command - which is exactly the kind of hidden
coupling that produces "works on my machine".

The fix: create the schema explicitly, in an autouse fixture, before any test
runs. Tests are now self-contained. They pass on a database that has never been
touched, which is the only standard worth holding them to - and it is what CI
does on every push.
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.database import Base, engine
from backend.app.main import app
from backend.app.schema import upgrade_to_head

# Importing models has a side effect that matters: it registers every ORM class
# on Base.metadata. Without this import, create_all() would run against an empty
# registry and cheerfully create nothing at all.
from backend.app import models  # noqa: F401


@pytest.fixture(scope="session", autouse=True)
def create_test_schema() -> None:
    """Create every table once, before the first test.

    scope="session" - run once for the whole test run, not once per test.
    autouse=True    - applies to every test without being requested explicitly.

    create_all() is idempotent: it creates only tables that are missing, so this
    is safe whether the database is brand new or already populated.

    Note we deliberately do NOT drop the tables afterwards. Dropping them would
    wipe the ingested CERT data every time you ran the suite, which would be
    infuriating. A production-grade setup would isolate tests in a dedicated
    test database or roll back each test in a transaction; that is a worthwhile
    hardening step and it is noted here rather than silently skipped.
    """
    # Migrate, don't create_all().
    #
    # The tests must exercise the SAME schema path production uses. If the suite
    # builds its tables with create_all() while the application migrates with
    # Alembic, then a broken migration passes every test and fails on the first
    # real deployment - which is precisely the failure mode tests exist to prevent.
    upgrade_to_head()


@pytest.fixture
def client() -> TestClient:
    """A TestClient for the FastAPI app.

    Shared here rather than redefined in every test module. It was previously
    declared inside test_auth.py, which meant any new test file silently had no
    client at all and every test in it errored at setup - which is exactly what
    happened when test_auth_hardening.py was added.
    """
    return TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def disable_rate_limiting_for_the_suite() -> None:
    """Turn the rate limiter OFF for the whole suite. Automatically.

    THIS IS A FIXTURE, NOT AN ENVIRONMENT VARIABLE, AND THAT IS THE POINT.

    The first version of this relied on RATE_LIMIT_ENABLED=false in .env - which
    worked perfectly on the machine where that line had been added, and failed on
    every other machine, because .env is not in git and nobody thought to mention it.
    Sixteen tests failed with `assert 429 == 201` and a cascade of KeyErrors, none of
    which pointed anywhere near the actual cause.

    A test suite that only passes with the right undocumented local config is not a
    test suite, it is a rumour. So the suite now configures itself.

    The limits are DELIBERATELY not exercised here: forty registrations and sixty
    logins is not the traffic they exist to stop, and a test that fails because it
    ran too soon after the previous one is a test nobody trusts. They ARE tested,
    explicitly and in isolation, in test_ratelimit.py - because switching a security
    control off for the tests and then never testing it is how security controls
    quietly stop working.
    """
    from backend.app.ratelimit import limiter

    limiter.enabled = False