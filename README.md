# Insider Threat Behavioral Intelligence System

An AI-powered system that detects insider threats by analyzing employee activity logs, building behavioral baselines, scoring anomalies, and serving predictions through a web interface — built on the CERT r4.2 Insider Threat Dataset.

## Overview

This project ingests raw employee activity logs (logon, USB device usage, email, file transfers, web browsing) and identifies users whose behavior deviates significantly from normal patterns — a proxy for detecting insider threats such as data exfiltration, privilege misuse, and pre-departure data theft. It combines unsupervised machine learning with peer-group and historical behavioral baselining, exposed through a FastAPI backend and Streamlit frontend so any new CSV of activity logs can be uploaded and scored.

## Dataset

**CERT r4.2 Insider Threat Dataset** ([Kaggle](https://www.kaggle.com/datasets/andrihjonior/cert-insider-threat-dataset-r4-2))

| File | Description | Rows |
|---|---|---|
| `logon.csv` | Logon/logoff events | ~855K |
| `device.csv` | USB connect/disconnect events | ~405K |
| `http.csv` | Web browsing activity | ~28.4M |
| `email.csv` | Email metadata and content | ~2.6M |
| `file.csv` | File copies to removable media | ~446K |
| `psychometric.csv` | Big-5 personality scores per employee | 1,000 |
| `LDAP/*.csv` | 18 monthly employee org snapshots | — |
| `answers/insiders.csv` | Ground-truth malicious insiders (multi-release; filtered to r4.2) | — |

Spans **1,000 users**, **Jan 2010 – May 2011**, with **70 known r4.2 insiders** across 3 attack scenario instances (`answers/r4.2-1/`, `r4.2-2/`, `r4.2-3/`).

> **Note:** `insiders.csv` contains ground truth spanning multiple CERT dataset releases (r2 through r6.2), not just r4.2. It must be filtered with `dataset == 4.2` before use — this was a real bug caught and fixed during development.

## ArchitectureRaw 
CSVs (5 log sources)
↓
Feature Engineering (per-user-per-day aggregation)
↓
Peer-Group Z-Scores (role-normalized, from LDAP) + Rolling 7-Day Baselines
↓
Isolation Forest (unsupervised anomaly detection)
↓
Risk Scoring (0–100) → Low / Medium / High / Critical
↓
Saved Model Artifacts (joblib, JSON, Parquet)
↓
FastAPI Backend (/analyze endpoint) ←→ Streamlit Frontend (file upload UI)


## What was built

### 1. Exploratory Data Analysis
- Loaded all 5 log sources plus LDAP and ground-truth files from Kaggle
- Verified schema, date ranges, null counts, unique users per source
- Merged 18 monthly LDAP snapshots into one employee identity table (role, department per user)
- Cross-validated that all activity-log users exist in the LDAP table (0 mismatches)

**Bugs found and fixed during EDA:**
- `has_attachment` flag was checking `is_not_null()` on a numeric attachment-count column (always true) — fixed to `> 0`
- `insiders.csv` ground truth wasn't filtered to the correct dataset release — fixed with `dataset == 4.2`

### 2. Feature Engineering
Per-user-per-day behavioral features aggregated from raw events:

| Source | Features |
|---|---|
| Logon | n_logons, n_logoffs, first_hour, last_hour, after_hours_events, n_pcs, is_weekend_activity |
| Device | n_device_connects, n_device_disconnects |
| Email | n_emails_sent, total_recipients, n_emails_with_attachment, total_email_size |
| File | n_file_copies, n_distinct_file_types |
| HTTP | n_http_requests, n_distinct_domains |

**Peer-group normalization:** each user's daily feature values converted to a z-score relative to their LDAP-derived job role's mean/std, so role-typical behavior (e.g., IT admins working late) isn't flagged the same way as an anomaly for a role where that's unusual.

**Rolling 7-day baseline:** each user's daily values compared against their own trailing 7-day average, producing deviation features that capture sudden behavioral shifts rather than just cross-sectional outliers.

### 3. Anomaly Detection Model
- **Algorithm:** Isolation Forest (scikit-learn), `n_estimators=300`, `contamination=0.01`, `random_state=42`
- **Why unsupervised:** only 70 of 1,000 users are known insiders — far too few positive examples to train a reliable supervised classifier; Isolation Forest requires no labels and isolates rare/unusual data points by construction
- **Output:** raw anomaly score → normalized 0–100 risk score → Low/Medium/High/Critical category

### 4. Model Validation (against CERT r4.2 ground truth)
Ranking all 1,000 users by max daily risk score and checking how many of the 70 known insiders appear near the top:

| Metric | Result |
|---|---|
| Known insiders in top 20 flagged users | 9 / 70 |
| Known insiders in top 50 flagged users | 16 / 70 |

For reference, random chance would predict roughly 3.5 insiders in a top-50 selection — the model performs meaningfully above chance, though with a long tail of insiders that rank poorly (likely scenarios without strong after-hours/device signals, e.g. gradual/subtle exfiltration).

### 5. Weighted Risk Scoring
Implements the project's target weighting scheme by mapping engineered features to categories:
- 35% Behavioral Anomalies (mean absolute rolling deviation across logon/device/email/file features)
- 20% Data Access Violations (file-copy deviation)
- 10% Access Pattern Deviations (device-usage deviation)
- 35% ML anomaly score (stands in for Privilege Misuse + Historical Security Events, pending live RBAC/audit data in a future iteration)

### 6. Threat Investigation Function
`investigate_user(user_id, day)` — given a flagged user and day, pulls the full raw activity timeline (logon, device, email, file events) for that day across all log sources, for analyst-style drill-down.

### 7. Inference Pipeline (reusable, no retraining required)
`predict_from_dataframes()` / `predict_from_csv()`:
- Auto-detects log type (logon/device/email/file/http) from a CSV's column signature
- Rebuilds the exact same features used in training
- Applies the **saved** trained model and **saved** training-time normalization stats (not recomputed per request) — this keeps risk scores consistent and comparable across different uploads, including small or partial ones
- Handles missing log types (absent features default to 0) and users with no LDAP match (role z-score defaults to 0)

### 8. Model Artifacts (persisted, no retraining needed to reuse)
| File | Contents |
|---|---|
| `isolation_forest.joblib` | Trained model |
| `feature_columns.json` | Exact feature list/order used in training |
| `normalization_stats.json` | Training-time anomaly score min/max for consistent scoring |
| `role_stats.parquet` | Per-role mean/std for peer-group z-scores |
| `ldap_latest.parquet` | Each user's most recent known role/department |

### 9. FastAPI Backend
- `GET /` — health check
- `POST /analyze` — accepts one or more CSV file uploads, auto-detects log types, engineers features, applies the saved model, returns JSON with per-user-day risk scores and categories
- CORS enabled to allow requests from the Streamlit frontend running on a different port

### 10. Streamlit Frontend
- Multi-file CSV upload widget
- Calls the FastAPI `/analyze` endpoint on demand
- Displays results as a color-coded table (green=Low, yellow=Medium, orange=High, red=Critical), summary metrics, a risk-category bar chart, and a CSV download button for the full report

### 11. Synthetic Test Dataset (for demo/validation without the full CERT dataset)
Generated a 6-user, 30-day synthetic dataset (`sample_logon.csv`, `sample_device.csv`, `sample_email.csv`, `sample_file.csv`, `sample_http.csv`) with:
- 5 normal users: consistent weekday 9-to-5 logins, no weekend activity, minimal USB/file use, work-related browsing
- 1 planted insider (`XYZ9999`): behaves normally for days 1–20, then from day 21 onward shows after-hours logins (1–3am), repeated USB connect/disconnect cycles, large email attachments sent to a personal address, suspicious file types (`.zip`/`.rar`/`.exe`), and browsing to data-leak/job-search sites — modeled on CERT's documented scenario patterns

**Result when uploaded through the full pipeline:** all of the insider's top-ranked risk days correctly correspond to the planted anomalous period (days 21–30) — no normal user's activity outranked the inserted anomaly. Scores capped in the "Medium" category rather than "High/Critical" because the risk-score scale is calibrated against the original 1,000-user CERT training population's anomaly-score range, not the small synthetic batch — this is expected behavior of using a fixed, pre-trained normalization scale rather than a limitation of the detection itself.

## Tech Stack

- **Language:** Python 3.12/3.13
- **Data processing:** Pandas (initial prototyping used Polars for memory efficiency per mentor's recommendation; switched to Pandas for broader environment compatibility across Kaggle/Colab/local)
- **ML:** Scikit-learn (Isolation Forest)
- **Backend API:** FastAPI, Uvicorn
- **Frontend:** Streamlit
- **Model persistence:** Joblib, PyArrow (Parquet), JSON
- **Dataset access:** Kaggle API via `kagglehub`
- **Development environments:** Kaggle Notebooks (initial EDA), Google Colab (full training pipeline), local machine via Antigravity IDE (backend/frontend serving)

## Known Issues & Fixes Applied

- `has_attachment` bug in EDA (checked `is_not_null()` instead of `> 0`) — fixed
- `insiders.csv` spans multiple CERT dataset releases — fixed by filtering `dataset == 4.2`
- Colab RAM crashes when loading all 5 log files simultaneously (especially 28M-row `http.csv`) — fixed by restructuring the pipeline to load → aggregate → delete → garbage-collect one source at a time, with `http.csv` processed in 3M-row chunks
- Risk-score normalization initially recomputed min/max per request, producing meaningless scores on small inputs — fixed by saving and reusing training-time normalization stats
- Windows PowerShell `uvicorn`/`streamlit` "not recognized" errors caused by PATH/virtual environment issues — resolved by running via `python -m uvicorn` / `python -m streamlit` inside a properly activated virtual environment

## Known Limitations

- Single-day or short-window CSV uploads produce weaker signal, since rolling 7-day deviation features have no history to compare against
- Missing log types default their corresponding features to 0, reducing detection accuracy for partial uploads
- Users not present in the saved LDAP table receive a neutral (zero) role z-score
- Absolute risk categories (Low/Medium/High/Critical) are calibrated to the original CERT training population's score distribution — small or unusual-population uploads may compress toward the middle of that scale even when the *relative* ranking within the upload is correct
- Some real insider scenarios (particularly those without strong after-hours or device-usage signals) rank poorly with current features — a known gap for future improvement (e.g., content/topic-based features from email, file, and HTTP text fields, currently unused)
- No authentication, RBAC, or persistent deployment yet — backend and frontend currently run locally, not containerized or hosted

## How to Run

### Prerequisites
- Python 3.12+
- A trained model in `models/` (produced by the training pipeline, or provided directly)

### Backend
```bash
cd backend
pip install -r ../requirements.txt
python -m uvicorn app:app --reload --port 8000
```
Health check: `GET http://localhost:8000/`

### Frontend
```bash
cd frontend
python -m streamlit run streamlit_app.py
```
Opens at `http://localhost:8501`, communicates with the backend at `http://localhost:8000`.

### Retraining the model (Google Colab)
1. Mount the CERT r4.2 dataset via `kagglehub.dataset_download(...)`
2. Run the full training pipeline: LDAP + ground-truth loading → per-source feature engineering (one source at a time, with cleanup) → merge → role z-scores + rolling baselines → Isolation Forest training → risk scoring → validation against ground truth → save artifacts to `models/`
3. Download the `models/` folder and place it alongside `backend/` and `frontend/`

## Project Structure
insider-threat-app/
├── models/
│ ├── isolation_forest.joblib
│ ├── feature_columns.json
│ ├── normalization_stats.json
│ ├── role_stats.parquet
│ └── ldap_latest.parquet
├── backend/
│ ├── inference.py # feature engineering + prediction logic
│ └── app.py # FastAPI service
├── frontend/
│ └── streamlit_app.py # Streamlit UI
└── requirements.txt



