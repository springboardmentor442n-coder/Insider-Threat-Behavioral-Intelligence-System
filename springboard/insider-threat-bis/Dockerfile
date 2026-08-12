FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies first so the layer caches across source edits.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Build the synthetic corpus, engineer features and train the model at image
# build time so the container starts ready to serve. Mount a real CERT r4.2
# drop at /data and set CERT_RAW_DIR to use the genuine dataset instead.
RUN python scripts/bootstrap.py --users 160 --days 160

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status==200 else 1)"

# Threads matter: the SSE endpoint holds a worker for the life of the stream.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "8", \
     "--timeout", "0", "--access-logfile", "-", "wsgi:app"]
