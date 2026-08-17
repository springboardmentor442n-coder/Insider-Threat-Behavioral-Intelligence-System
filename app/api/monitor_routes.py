"""Real-time activity monitoring: SSE stream plus a polling fallback."""

from __future__ import annotations

import json
import time

from flask import Blueprint, Response, current_app, jsonify, request, stream_with_context

from app.auth import require_auth
from app.services.stream import get_streamer

bp = Blueprint("monitor", __name__)

# Cap the stream so an abandoned EventSource cannot pin a worker forever.
MAX_STREAM_SECONDS = 3600


@bp.get("/stream")
@require_auth("viewer")
def stream():
    """Server-Sent Events feed of live activity.

    EventSource cannot send an Authorization header, so the token may also be
    passed as ?token=<jwt> (handled in app.auth._extract_token).
    """
    interval = current_app.config["STREAM_INTERVAL_SECONDS"]
    batch_size = max(1, min(int(request.args.get("batch", 3)), 20))
    streamer = get_streamer()
    streamer.load()

    @stream_with_context
    def generate():
        yield "retry: 3000\n\n"
        started = time.monotonic()
        while time.monotonic() - started < MAX_STREAM_SECONDS:
            batch = streamer.next_batch(batch_size)
            if batch:
                yield f"event: activity\ndata: {json.dumps(batch)}\n\n"
            else:
                # Comment frame keeps proxies from timing the connection out.
                yield ": no-data\n\n"
            time.sleep(interval)

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@bp.get("/api/v1/monitor/recent")
@require_auth("viewer")
def recent():
    """Polling fallback for clients that cannot hold an SSE connection."""
    limit = min(int(request.args.get("limit", 50)), 200)
    streamer = get_streamer()
    if request.args.get("advance", "1") == "1":
        streamer.next_batch(max(1, min(int(request.args.get("batch", 3)), 20)))
    return jsonify({"events": streamer.snapshot(limit)})
