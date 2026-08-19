# Insider Threat Behavioral Intelligence System

An AI-powered platform that monitors employee activity, builds behavioral baselines, detects anomalies, and generates risk-scored security alerts to help organizations identify potential insider threats before they escalate into data breaches or security incidents.

## Overview

This project was developed as part of the Infosys Springboard AI Internship program. It combines user behavior analytics (UBA), entity behavior analytics (UEBA), and machine learning-based anomaly detection to continuously assess insider risk across an organization.

## Objective

Traditional security tools focus on external threats. This system focuses on the harder problem — detecting suspicious behavior from within an organization by:

- Continuously monitoring employee digital activity (logins, device usage, file access)
- Building individual behavioral baselines per employee
- Detecting statistically significant deviations from normal behavior
- Scoring and prioritizing insider risk
- Auto-generating alerts and supporting security teams with investigation workflows
- Demonstrating real-time-style prediction on incoming activity data
- Presenting role-appropriate views to different security roles

## Tech Stack

- **Backend:** Python, FastAPI, JWT Authentication (OAuth2 password flow)
- **Database:** SQLite (dev) — see Known Gaps
- **Frontend:** HTML/CSS/JavaScript — role-gated multi-tab dashboard (Predict, Risk Scores, Incidents, Alerts, Employees, Notifications) plus login page
- **Machine Learning:** Scikit-learn (Isolation Forest), Pandas, NumPy, Joblib
- **Deployment:** Docker — containerized and verified end-to-end (see below)
- **Testing:** pytest (17 automated tests)
- **Dev Tools:** Git, GitHub, VS Code

## Project Status

Core system built and verified — authentication, behavioral analytics, anomaly detection, risk scoring, threat investigation, UEBA, alerts, notifications, and Docker containerization are all implemented and tested end-to-end. See **Known Gaps** below for what is explicitly out of scope.

## Docker Deployment

The backend is fully containerized and verified working end-to-end inside a clean Docker container — not just built, actually run and tested:

- ✅ Image builds cleanly from a fresh Dockerfile (`docker build`)
- ✅ Container starts and serves requests (`docker run`)
- ✅ Full flow verified live inside the container: register → login → `/risk-scores/summary` → `/predict`
- ✅ Results from the containerized backend matched the local backend exactly, confirming the image is a faithful, portable package of the app

See **Getting Started → Docker** below to build and run it yourself.

## Features

**Done and verified:**

- ✅ User registration & login (JWT-based authentication, OAuth2 password flow)
- ✅ Role-based access control (`security_analyst`, `security_manager`, `admin`) — tested with real 403/200 responses, enforced on both backend routes and frontend tab visibility
- ✅ Employee profile management (CRUD, role-restricted)
- ✅ Behavioral baseline generation per employee (330k+ user-day profiles from CERT r4.2 logon/device/file data)
- ✅ File-access behavioral signal — `file_count`/`unique_files` integrated from CERT r4.2 `file.csv` (445k events), extending the feature set from 5 to 7 and enabling the Data Access Violations risk category
- ✅ Anomaly detection engine (Isolation Forest, 7 features, 2% flag rate, explainable per-anomaly reasons)
- ✅ Insider risk scoring engine (Behavioral Anomalies + Data Access Violations, 55% of spec weight — see gaps for remaining 3 categories)
- ✅ Risk scores API + role-gated HTML dashboard (summary cards, filterable table)
- ✅ Live prediction endpoint — feed a CSV or manual input, get per-row Insider/Normal predictions in real time, viewable in the dashboard's Predict tab
- ✅ Threat investigation module — incident creation, evidence pulled from real anomaly history, status workflow
- ✅ UEBA module — org-wide percentile comparison and monthly behavioral trend analysis (department-based peer comparison not possible — see gaps)
- ✅ Alert & notification system — auto-generates alerts from High/Critical risk scores, open → acknowledged → resolved workflow, dashboard tab with live counts and per-alert actions
- ✅ Role-based dashboard views — `security_analyst` sees all tabs (Predict, Risk Scores, Incidents, Alerts, Employees); `security_manager` sees Risk Scores + Alerts; `admin` sees everything
- ✅ Employees tab in dashboard with full CRUD (list, create, update, delete) — verified working directory view with department, designation, manager, device info, access level
- ✅ Notifications & Escalation system (Module 11) — auto-generates escalation alerts when open alerts exceed a 24h threshold, dedicated Notifications tab with insider threat alert / escalation alert / investigation notification counts and status tracking
- ✅ Manual prediction audit trail — every manual prediction logged to `manual_predictions_log.csv`
- ✅ Docker containerization — built, run, and verified end-to-end (see Docker Deployment above)
- ✅ Automated test suite — 17 pytest tests covering auth, RBAC, employees, risk scores, prediction, incidents, UEBA

## Scope & Limitations

Documented honestly rather than hidden:

- Risk scoring is scoped to **Behavioral Anomalies + Data Access Violations only** (55% of the spec's weight — 35% + 20%, deliberately not renormalized to 100% so the score never implies coverage the project doesn't have). Privilege Misuse, Access Pattern Deviations, and Historical Security Events (45% remaining) aren't computable — the CERT dataset has no privilege-change log, access-pattern log, or incident history.
- UEBA peer comparison is **org-wide, not department-based** — the dataset has no department/role/org-chart fields, so true peer-group comparison isn't possible. Org-wide percentile comparison is used instead.
- Storage for risk scores, anomalies, alerts, and incidents is **CSV/JSON files, not relational DB tables**, despite the original architecture diagram implying PostgreSQL/MongoDB. Only users and employees are real DB tables.
- No Asset Association — `device_info` is a free-text field, not a structured/queryable asset table.
- Role differentiation is currently **tab-visibility only** (frontend) plus route-level checks (backend) — not fully separate, purpose-built dashboard layouts per role.
- The app runs via Docker; it is not deployed to a public cloud host (AWS/Azure).
- Reports & export (PDF/Excel) were scoped as a stretch item and are not included in this delivery.
- Automated/continuous activity log ingestion pipeline is still a manual script rather than a live pipeline.
- `email.csv`/`http.csv` from the CERT dataset were not used (multi-GB, not worth the time cost for this project) — email/HTTP-based behavioral features remain undone, disclosed rather than fabricated.
- DB schema documentation exists at `docs/DATABASE_SCHEMA.md` and includes these gaps explicitly.

## Project Structure

```
Insider-Threat-Behavioral-Intelligence-System/
├── backend/
│   └── app/
│       ├── auth.py
│       ├── models.py
│       ├── schemas.py
│       ├── rbac.py
│       ├── database.py
│       └── main.py
├── ml/
│   ├── behavioral_analytics.py
│   ├── risk_scoring_engine.py
│   ├── risk_api.py
│   ├── risk_dashboard.py
│   ├── predict_api.py
│   ├── investigation_api.py
│   ├── ueba_api.py
│   ├── alerts_api.py
│   └── manual_predictions_log.csv
├── frontend/
│   ├── index.html
│   ├── dashboard.html
│   ├── predict.html
│   └── risk_scores.html
├── datasets/
├── docs/
│   ├── DATABASE_SCHEMA.md
│   └── wireframes/
├── tests/
│   └── test_api.py
├── docker/
├── Dockerfile
└── README.md
```

## Dataset

This project uses the **CERT Insider Threat Dataset (r4.2)** — logon, device, and file-access activity logs — a widely-used academic dataset for insider threat research. `logon.csv`, `device.csv`, and `file.csv` were used; the full CERT release's ground-truth `answers/` folder (labeled malicious insiders) was not downloaded, so this project uses unsupervised anomaly detection rather than a labeled classifier. `email.csv`/`http.csv` were not downloaded (multi-GB, not worth the time cost for this project).

## Getting Started

### Prerequisites

- Python 3.10+
- Docker (optional, for containerized run)

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

> **Note:** On Windows with Anaconda installed, use the full venv interpreter path if `python`/`uvicorn` resolve to the wrong environment:
> `./venv/Scripts/python.exe -m uvicorn app.main:app --reload`

### Running Tests

```bash
cd backend
python -m pytest ../tests/
```

### Docker

```bash
docker build --no-cache -t insider-threat-api .
docker run -p 8000:8000 insider-threat-api
```

Once running, verify it's live:

```bash
curl http://127.0.0.1:8000/
```

## Author

**Krishna Vamsi Pallapu**
M.Tech AI & Data Science, KL University
AI Intern, Infosys Springboard

- GitHub: [Vamsi12022003](https://github.com/Vamsi12022003)
- LinkedIn: [pallapu-krishna-vamsi](https://linkedin.com/in/pallapu-krishna-vamsi)

## License

This project is developed for educational purposes as part of the Infosys Springboard internship program.
