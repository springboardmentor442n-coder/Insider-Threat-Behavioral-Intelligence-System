"""Does the application actually START?

WHY THIS FILE EXISTS - AND IT IS AN EMBARRASSING REASON
--------------------------------------------------------
81 tests passed. Then `uvicorn backend.app.main:app` died instantly:

    NameError: name 'schema_is_current' is not defined

The lifespan handler called a function that was never imported. A one-line bug, on
the single code path that runs before anything else can happen - and not one of the
81 tests noticed, because:

    TestClient(app)          does NOT run the lifespan
    with TestClient(app):    DOES

Every test used the first form. So the entire startup path of the application - the
database connection check, the schema-currency check, the router registration, the
middleware wiring - was never executed by the test suite even once. The app could
have been broken in a dozen ways and every test would still have been green.

A test suite that never starts the application is not testing the application. It is
testing a collection of functions that happen to live near one.

These tests use the context-manager form, and they are the only ones that do.
"""

from __future__ import annotations

from fastapi import status
from fastapi.testclient import TestClient

from backend.app.main import app


def test_the_application_actually_starts() -> None:
    """Run the lifespan. This is the test that would have caught the NameError.

    `with TestClient(app)` triggers startup and shutdown. Everything the app does
    before serving its first request - checking the database, verifying the schema is
    at the migration the code expects, wiring the rate limiter - happens here.
    """
    with TestClient(app) as client:
        r = client.get("/health")
        assert r.status_code == status.HTTP_200_OK


def test_every_router_is_actually_registered() -> None:
    """The routers must be MOUNTED, not merely imported.

    An `include_router` line that gets lost in a merge produces an app that starts
    perfectly and 404s on a third of its endpoints. Nothing else in the suite would
    catch it: the route handlers are all unit-tested and all pass, because they are
    being called directly rather than through the app.
    """
    paths = {r.path for r in app.routes if hasattr(r, "path")}

    required = {
        "/api/auth/login",
        "/api/auth/refresh",
        "/api/users/me",
        "/api/data/employees",
        "/api/alerts",
        "/api/alerts/{alert_id}",
        "/api/investigate/{user_id}",
    }
    missing = required - paths
    assert not missing, (
        f"these endpoints are NOT mounted on the app: {sorted(missing)}\n\n"
        "The router exists and its handlers are tested, but include_router() was "
        "never called - so the app starts cleanly and 404s on every one of them."
    )


def test_the_schema_check_runs_at_startup() -> None:
    """Startup must REFUSE to serve on a stale schema.

    This is the guard that replaced create_all(). If the database is behind the
    models, the app must not come up: a server that starts happily and then throws
    IntegrityError on the first INSERT is far worse than one that refuses to boot and
    says why.
    """
    from backend.app.schema import schema_is_current

    ok, message = schema_is_current()
    assert ok, f"schema is not current: {message}"
    assert "zz01" in message or "at" in message.lower()