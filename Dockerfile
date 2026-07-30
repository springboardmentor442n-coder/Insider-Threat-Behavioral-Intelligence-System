# ============================================================================
#  Backend image - FastAPI + the ML stack (Module 13, containerization)
# ============================================================================
#  Build context is the REPOSITORY ROOT, not backend/, because the backend
#  needs alembic.ini, migrations/, and scripts/ as well as the backend package.
#
#  The container's job at start-up is deliberately ordered (see entrypoint.sh):
#      wait for the database  ->  run migrations  ->  (optionally seed)  ->  serve
#  The migration step is not optional. The app's start-up refuses to serve
#  against a stale schema, so the container must bring the schema current first.
# ============================================================================
FROM python:3.13-slim

# Keep the image lean and the install I/O-light:
#   PYTHONDONTWRITEBYTECODE - no .pyc files (fewer writes during install)
#   PIP_NO_CACHE_DIR        - don't keep a pip download cache in the layer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1

# System libraries:
#   libgomp1          - OpenMP runtime required by xgboost and lightgbm
#   postgresql-client - gives us pg_isready for the wait-for-db step
#   curl              - used by the container healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
        postgresql-client \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first so this layer is cached across code changes.
# --no-compile skips byte-compilation (fewer disk writes at build time); we then
# drop nvidia-nccl-cu12 - a multi-GPU CUDA library xgboost pulls in on Linux but
# that is never used for CPU inference or training here - and strip caches. This
# trims roughly 300-400 MB off the image.
COPY requirements.txt .
RUN set -eux; \
    pip install --no-cache-dir --no-compile -r requirements.txt; \
    pip uninstall -y nvidia-nccl-cu12 || true; \
    find /usr/local/lib/python3.13/site-packages -name '__pycache__' -type d -prune -exec rm -rf {} + || true; \
    rm -rf /root/.cache

# Application code and everything the migration + seed steps need.
COPY backend/ backend/
COPY migrations/ migrations/
COPY alembic.ini .
COPY scripts/ scripts/

# Trained models are written here at seed time; declared as a volume in compose
# so they survive restarts. Create it now so the path exists even without a volume.
RUN mkdir -p /app/models

# Start-up orchestration.
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

# A simple liveness probe against the app's own health endpoint.
HEALTHCHECK --interval=15s --timeout=5s --start-period=120s --retries=5 \
    CMD curl -fsS http://localhost:8000/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
