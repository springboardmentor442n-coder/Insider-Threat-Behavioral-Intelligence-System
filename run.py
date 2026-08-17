#!/usr/bin/env python
"""Development entrypoint for the Insider Threat Behavioral Intelligence System.

    python run.py                # http://localhost:8000

For production use a WSGI server with threads enabled (SSE holds a worker):

    gunicorn --workers 2 --threads 8 --timeout 0 'wsgi:app'
"""

import argparse
import os

from app import create_app

app = create_app()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--host", default=os.getenv("HOST", "127.0.0.1"))
    ap.add_argument("--port", type=int, default=int(os.getenv("PORT", "8000")))
    ap.add_argument("--debug", action="store_true", default=os.getenv("DEBUG") == "1")
    args = ap.parse_args()

    print(f"\n  Security console : http://{args.host}:{args.port}")
    print(f"  Health check     : http://{args.host}:{args.port}/health")
    print("  Default logins   : admin/admin123 · analyst/analyst123 · viewer/viewer123\n")

    # threaded=True is required: the SSE endpoint holds a request open.
    app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)


if __name__ == "__main__":
    main()
