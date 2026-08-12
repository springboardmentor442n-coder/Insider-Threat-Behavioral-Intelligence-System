"""Dev-only: drive the console in a headless browser and capture screenshots."""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8010"
OUT = Path("/tmp/itbis-shots")
OUT.mkdir(exist_ok=True)

errors, failed = [], []

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1500, "height": 1000})
    page.on("console", lambda m: errors.append(f"{m.type}: {m.text}") if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
    page.on("requestfailed", lambda r: failed.append(f"{r.url} {r.failure}"))

    page.goto(BASE, wait_until="networkidle")
    page.screenshot(path=OUT / "01-login.png")

    page.fill("#username", "analyst")
    page.fill("#password", "analyst123")
    page.click("#login-btn")
    page.wait_for_selector("#console:not([hidden])", timeout=15000)
    page.wait_for_timeout(2500)
    page.screenshot(path=OUT / "02-dashboard.png", full_page=True)

    # Live monitoring — start the SSE stream and let a few frames land.
    page.click('[data-page="monitoring"]')
    page.click("#stream-toggle")
    page.wait_for_timeout(6000)
    page.screenshot(path=OUT / "03-monitoring.png", full_page=True)
    page.click("#stream-toggle")

    # Behavioural profiling + a user profile drill-down.
    page.click('[data-page="profiling"]')
    page.wait_for_selector("#users-table tbody tr", timeout=10000)
    page.click("#users-table tbody tr:first-child [data-profile]")
    page.wait_for_selector("#profile-detail:not([hidden])", timeout=10000)
    page.wait_for_timeout(1200)
    page.screenshot(path=OUT / "04-profiling.png", full_page=True)

    # Alerts.
    page.click('[data-page="alerts"]')
    page.wait_for_selector("#alerts-table tbody tr", timeout=10000)
    page.wait_for_timeout(800)
    page.screenshot(path=OUT / "05-alerts.png", full_page=True)

    # Investigation, launched from the alert queue.
    page.click("#alerts-table tbody tr:first-child [data-investigate]")
    page.wait_for_selector("#inv-result:not([hidden])", timeout=15000)
    page.wait_for_timeout(1500)
    page.screenshot(path=OUT / "06-investigation.png", full_page=True)

    # Reports.
    page.click('[data-page="reports"]')
    page.wait_for_selector("#report-top tbody tr", timeout=10000)
    page.wait_for_timeout(800)
    page.screenshot(path=OUT / "07-reports.png", full_page=True)

    browser.close()

print("screenshots ->", OUT)
print("console errors:", len(errors))
for e in errors[:20]:
    print("  ", e)
print("failed requests:", len(failed))
for f in failed[:10]:
    print("  ", f)
