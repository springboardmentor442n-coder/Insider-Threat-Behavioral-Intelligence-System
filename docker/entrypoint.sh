#!/usr/bin/env bash
# ============================================================================
#  Backend container entrypoint.
#
#  Order matters and is enforced here rather than left to chance:
#    1. Wait until Postgres actually accepts connections (compose "depends_on"
#       only waits for the container to start, not for the database to be ready).
#    2. Apply migrations. The app REFUSES to serve against a stale schema, so
#       this must succeed before uvicorn starts.
#    3. Optionally seed a small demo dataset on an empty database, so a fresh
#       `docker-compose up` yields a UI with data in it rather than empty tables.
#    4. Hand off to the container's command (uvicorn) with exec, so signals
#       (Ctrl-C, docker stop) reach the server directly.
# ============================================================================
set -e

DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-itbis_user}"

# --- 1. wait for the database -------------------------------------------------
echo "[entrypoint] waiting for database at ${DB_HOST}:${DB_PORT} ..."
until pg_isready -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" >/dev/null 2>&1; do
    sleep 1
done
echo "[entrypoint] database is accepting connections."

# --- 2. migrations (mandatory) ------------------------------------------------
echo "[entrypoint] applying migrations (alembic upgrade head) ..."
alembic upgrade head
echo "[entrypoint] schema is current."

# --- 3. optional demo seed ----------------------------------------------------
# Controlled by SEED_DEMO (default 1 in compose). Seeds only when the alerts
# table is empty, so restarts don't re-run the pipeline. The dataset is the tiny
# committed CI fixture unless SEED_DATA_DIR points somewhere else (e.g. a mounted
# volume with the real CERT data).
if [ "${SEED_DEMO:-0}" = "1" ]; then
    ALERTS=$(python -c "from backend.app.database import SessionLocal; from backend.app.models import Alert; s=SessionLocal(); print(s.query(Alert).count()); s.close()" 2>/dev/null || echo "0")
    if [ "${ALERTS}" = "0" ]; then
        export CERT_DATA_DIR="${SEED_DATA_DIR:-backend/tests/fixtures/mini_cert}"
        echo "[entrypoint] empty database - seeding demo dataset from ${CERT_DATA_DIR} ..."
        echo "[entrypoint]   (this runs the full pipeline once and may take a couple of minutes)"
        python -m scripts.ingest_cert
        python -m scripts.build_features
        python -m scripts.ingest_answers
        python -m scripts.train_detect --save
        python -m scripts.generate_alerts
        echo "[entrypoint] demo seed complete."
    else
        echo "[entrypoint] database already has ${ALERTS} alerts - skipping seed."
    fi
else
    echo "[entrypoint] SEED_DEMO is off - starting against the database as-is."
fi

# --- 3b. bootstrap a demo operator account ------------------------------------
# The seed loads employees and alerts but no OPERATOR login, so a fresh stack has
# data yet no way to sign in and see it. This creates one administrator if absent
# (idempotent - it never overwrites an existing account). Controlled by
# BOOTSTRAP_ADMIN; the credentials come from DEMO_ADMIN_EMAIL / DEMO_ADMIN_PASSWORD.
if [ "${BOOTSTRAP_ADMIN:-1}" = "1" ]; then
    if ! python - <<'PY'
import os
from backend.app.database import SessionLocal
from backend.app.models import SecurityUser, UserRole
from backend.app.security import hash_password

email = os.environ.get("DEMO_ADMIN_EMAIL", "admin@dtaa.com")
password = os.environ.get("DEMO_ADMIN_PASSWORD", "Tr0ub4dor-Horse!")
with SessionLocal() as db:
    if db.query(SecurityUser).filter_by(email=email).first():
        print(f"[entrypoint] operator {email} already exists - not recreating.")
    else:
        db.add(SecurityUser(
            email=email,
            full_name="Demo Admin",
            hashed_password=hash_password(password),
            role=UserRole.ADMINISTRATOR,
            is_active=True,
        ))
        db.commit()
        print(f"[entrypoint] created demo operator {email} (administrator)")
PY
    then
        echo "[entrypoint] WARNING: operator bootstrap failed; create one manually to sign in."
    fi
fi

# --- 4. serve -----------------------------------------------------------------
echo "[entrypoint] starting: $*"
exec "$@"
