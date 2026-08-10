# Insider-Threat-Behavioral-Intelligence-System

# Insider Threat Behavioral Intelligence System

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
| `LDAP/*.csv` | Monthly employee org snapshots | 18 files |
| `answers/insiders.csv` | Ground-truth malicious insiders (multi-release) |

The dataset spans **1,000 users** from **Jan 2010 to May 2011** and includes 3 known insider threat scenarios (in `answers/r4.2-1/`, `r4.2-2/`, `r4.2-3/`).

## What's in this notebook

`data-preprocessing-insider-threat-dectection.ipynb
` performs the EDA phase of Milestone 1:

- Loads all core log files using **Polars' lazy API** (`pl.scan_csv`) for memory-efficient processing on large files (esp. `http.csv` at 28M+ rows)
- Schema inspection, null/duplicate checks, and datetime parsing across all files
- Unique user counts per data source
- Behavioral pattern analysis: logon hour/day-of-week distribution, after-hours and weekend activity flags
- USB device usage patterns, email recipient/attachment analysis, file extension breakdown
- Top domain analysis from HTTP logs
- Merges 18 monthly LDAP snapshots into a unified employee identity table
- Cross-validates activity-log users against LDAP records
- Loads ground-truth insider labels and scenario descriptions for future model evaluation

## Tech Stack

- **Language:** Python 3.12
- **Data processing:** Polars (lazy/streaming engine, chosen for RAM efficiency over pandas)
- **Visualization:** Matplotlib, Seaborn
- **Environment:** Kaggle Notebooks

## What's implemented

### 1. Exploratory Data Analysis (Milestone 1)
- Schema inspection, null/duplicate checks, datetime parsing across all log sources
- Behavioral pattern analysis: logon hour/day-of-week distribution, after-hours/weekend activity
- USB device usage, email recipient/attachment analysis, file extension breakdown, HTTP domain analysis
- Merged 18 LDAP snapshots into a unified employee identity table, cross-validated against activity logs

### 2. Feature Engineering
Per-user-per-day behavioral features aggregated from all 5 log sources:
- **Logon**: login/logoff counts, first/last hour, after-hours event count, distinct PCs used, weekend activity flag
- **Device**: USB connect/disconnect counts
- **Email**: emails sent, total recipients, attachment count, total size
- **File**: file copy count, distinct file types
- **HTTP**: request count, distinct domains visited

**Peer-group (role-normalized) z-scores**: each user's daily behavior compared against others in the same LDAP-derived job role.

**Rolling 7-day baselines**: each user's daily behavior compared against their own recent history — captures gradual behavioral drift.

### 3. Anomaly Detection Model (Milestone 2)
- **Algorithm**: Isolation Forest (`n_estimators=300`, `contamination=0.01`, `random_state=42`) — unsupervised, chosen because only 70 of 1,000 users are known insiders (too few for reliable supervised classification)
- **Output**: anomaly score → normalized 0–100 risk score → Low/Medium/High/Critical risk category

**Validation results** (against ground-truth r4.2 insiders):
| Top K | Precision@K | Recall@K |
|---|---|---|
| Top 20 | 45% | 12.9% |
| Top 50 | 32% | 22.9% |
| Top 100 | — | — |

16 of 70 known insiders ranked in the top 50 flagged users (9 in the top 20) — roughly **4.5x better than random chance** (expected ~3.5 by chance alone).

### 4. Weighted Risk Scoring (Milestone 3, in progress)
Implements the project's weighted formula:
- 35% Behavioral Anomalies (rolling deviation from own baseline)
- 20% Data Access Violations (file copy deviation)
- 10% Access Pattern Deviations (device usage deviation)
- 35% ML anomaly score (proxy for privilege misuse + historical events, pending live RBAC data)

### 5. Threat Investigation Module
`investigate_user(user_id, day)` — pulls a full cross-source activity timeline (logon, device, email, file) for any flagged user/day, for analyst drill-down.

### 6. Inference Pipeline (reusable, no retraining needed)
`predict_from_csv()` / `predict_from_dataframes()`:
- Auto-detects log type (logon/device/email/file/http) from column signatures
- Applies the **saved** trained model and **saved** normalization stats (not recomputed per request — critical for consistent scoring on small/partial inputs)
- Handles missing log types (defaults absent features to 0) and unknown users (not in LDAP → neutral role z-score)
- Returns per-user-day risk scores and categories

### 7. FastAPI Service
- `POST /analyze` — accepts one or more CSV uploads, returns JSON with flagged users and risk scores
- `GET /` — health check
- Interactive docs at `/docs`
- Currently exposed via ngrok tunnel for development/testing (not yet containerized/deployed)

## Tech Stack

- **Language**: Python 3.12
- **Data processing**: Pandas (rewritten from initial Polars prototype for Colab compatibility; mentor originally recommended Polars for memory efficiency)
- **ML**: Scikit-learn (Isolation Forest)
- **API**: FastAPI, Uvicorn
- **Model persistence**: Joblib, Parquet, JSON
- **Environment**: Google Colab (training), Kaggle Notebooks (initial EDA)
- **Tunneling (dev only)**: ngrok

## Known Issues & Fixes Applied

- Corrected `has_attachment` flag miscalculation (was `is_not_null()` on a count column instead of `> 0`)
- Filtered `answers/insiders.csv` to `dataset == 4.2` — the file spans multiple CERT releases (r2–r6.2)
- Resolved Colab RAM crashes by restructuring the pipeline to load/aggregate/discard one log source at a time, with `http.csv` (28M+ rows) processed in 3M-row chunks
- Risk-score normalization now uses **saved training-time min/max**, not per-request min/max — prevents meaningless scores when scoring small/partial CSV uploads

## Known Limitations

- Single-day CSV uploads produce weaker signal (no rolling-baseline history available)
- Missing log types default their corresponding features to 0, reducing detection accuracy for partial uploads
- Users not present in the saved LDAP table receive a neutral (zero) role z-score
- Some insider scenarios (particularly those without after-hours/device anomalies, e.g. gradual data exfiltration) are harder for current features to detect — a known gap for future feature work (e.g., content/topic-based features from email/file/HTTP text)
- API is currently dev-only (Colab + ngrok); not yet containerized or persistently deployed

## How to Run

### Training pipeline
1. Open in Google Colab, attach the [CERT r4.2 dataset](https://www.kaggle.com/datasets/andrihjonior/cert-insider-threat-dataset-r4-2) via `kagglehub`
2. Run cells top to bottom (Colab sessions don't persist variables across restarts)
3. Trained artifacts save to `/content/models/`

### Inference API (same session, after training)
1. Run the API-building cells (writes `inference.py`, `app.py`)
2. Install dependencies: `fastapi uvicorn python-multipart pyngrok`
3. Set an [ngrok authtoken](https://dashboard.ngrok.com/get-started/your-authtoken) and start the server
4. Test via the printed public URL's `/docs` page, or `POST` a CSV to `/analyze`

### Reusing a saved model without retraining
1. Upload a previously downloaded `models_archive.zip` and unzip to `/content/models`
2. Skip the training cells, run only the API-serving cells

