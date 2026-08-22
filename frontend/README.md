# ITBIS Frontend — Insider Threat Console

React + Vite + Chart.js dashboard for the Insider Threat Behavioral
Intelligence System. Talks to the FastAPI backend over HTTP.

## Stack
- **React 18** + **Vite 5** — app framework and dev server
- **React Router 6** — routing + role-based redirect
- **Chart.js** (via react-chartjs-2) — the dashboard visualisations
- **Framer Motion** + **GSAP** — page transitions and the login scan animation

## Run it

The frontend needs the backend running. In one terminal, start the backend:

```
cd ..                      # the repo root
python -m uvicorn backend.app.main:app --reload
```

In a second terminal, start the frontend:

```
npm install                # first time only
npm run dev
```

Then open **http://localhost:5173**.

Vite proxies every `/api/*` call to `http://127.0.0.1:8000` (see vite.config.js),
so there is no CORS setup and no hardcoded backend URL in the app — the same code
works in dev and behind a reverse proxy in production.

## Log in

Use any operator account that exists in the backend. If you need one, register
via the API docs (http://127.0.0.1:8000/docs → POST /api/auth/register) with a
role of `security_analyst`, `soc_engineer`, `security_manager`, or
`administrator`.

## What's built

- **Login** — JWT auth with automatic token refresh
- **Analyst dashboard** — four live views:
  - Alert volume over time, by severity (14/30/90-day range)
  - Which risk components are driving alerts
  - Queue composition by severity
  - Employees to watch, ranked by peak risk

SOC / Manager / Admin dashboards route to the analyst view for now and are the
next build.

## Build for production

```
npm run build              # outputs to dist/
npm run preview            # serve the production build locally
```
