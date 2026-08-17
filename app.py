# Insider Threat Detection - Main Application
"""
Main application for insider threat detection system.

The Streamlit dashboard UI lives in STREAMLIT/app.py. This file is a thin
entry point so that the app can be launched from the project root with:

    streamlit run app.py

Without this redirect, `streamlit run app.py` would execute this console
script (which has no Streamlit UI) and the browser would show a blank page.
"""
import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(
        str(Path(__file__).resolve().parent / "STREAMLIT" / "app.py"),
        run_name="__main__",
    )
