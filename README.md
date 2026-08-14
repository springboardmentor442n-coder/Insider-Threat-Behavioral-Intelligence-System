# Insider Threat Behavioral Intelligence System

AI-powered platform for continuous employee activity monitoring, behavioral anomaly
detection, insider risk scoring, real-time enterprise simulation, and ML threat prediction — built with FastAPI, PyTorch/RandomForest, React, and MySQL.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend App | React 18 + Tailwind CSS + Lucide Icons + Recharts |
| Backend API | Python 3.11 + FastAPI + WebSockets |
| Database | MySQL 8.0 (primary) |
| Cache & Streaming | Redis 7 |
| ML Models | RandomForestClassifier (200 trees, 5-class), Isolation Forest, SHAP Explainable AI |
| Auth | JWT (access + refresh tokens) + OAuth2 + RBAC |
| Deployment | Docker + Docker Compose |

---

## Quick Start (How to Run)

### Option 1: Run Locally (Recommended for Development)

#### 1. Setup Backend (FastAPI)

```bash
# 1. Clone repository & configure environment
cp .env.example .env
# Edit .env with your MySQL credentials (DATABASE_URL)

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Seed 300 Synthetic Employees & Generate 50-Row Test CSVs
python scripts/seed_synthetic_300.py
python scripts/generate_synthetic_csvs.py

# 4. Start Backend API Server
uvicorn app.main:app --reload --port 8000
```
- **Backend API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

#### 2. Setup Frontend (React)

```bash
# 1. Open a new terminal and navigate to frontend
cd frontend

# 2. Install dependencies & start dev server
npm install
npm start
```
- **Web App**: http://localhost:3000

---

### Option 2: Run with Docker Compose

```bash
docker-compose up -d --build
# Backend API: http://localhost:8000
# Web Interface: http://localhost:3000
```

---

## Default Login Credentials

| Role | Email | Password |
|---|---|---|
| Administrator | admin@company.com | Admin123! |
| Security Manager | manager@company.com | Manager123! |
| Security Analyst | analyst@company.com | Analyst123! |
| SOC Engineer | soc@company.com | SOC123!pwd |

---

## Key Features & How to Use

### 1. 300 Synthetic Employee Dataset
- Database is cleanly populated with **300 synthetic employees** (`SYN-001` through `SYN-300`).
- Balanced risk distribution across all 4 criteria:
  - **Low Risk**: ~110 employees (~37%)
  - **Medium Risk**: ~90 employees (~30%)
  - **High Risk**: ~60 employees (~20%)
  - **Critical Risk**: ~40 employees (~13%)

### 2. Live Simulation & Dynamic Risk Ticker
- Toggle **SIMULATION: RUNNING** on the SOC Dashboard or via API (`POST /api/v1/simulation/toggle`).
- Background worker continuously streams employee activities and updates risk scores **one by one** over WebSockets with audio & voice alerts.

### 3. Prediction Lab (ML Pipeline & CSV Upload)
Navigate to **Prediction Lab** (`/predict`):
- **ML Pipeline Scan**: Run a live threat sweep across the 300 synthetic cohort.
- **CSV Upload Predict**: Drag & drop a 50-row synthetic CSV file (`data/synthetic_csvs/synthetic_features_50.csv`) to predict risk levels, class probabilities, and SHAP explanations for all 50 rows instantly. Click **Download Sample 50-Row CSV** inside the UI for a ready-to-test CSV.
- **Manual Vector Test**: Interactive feature sliders to test custom behavioral scenarios.

---

## Synthetic CSV Dataset & API Endpoints

Sample synthetic CSVs are generated in `data/synthetic_csvs/`:
- `synthetic_features_50.csv`: 50 rows of feature vectors containing Low, Medium, High, and Critical criteria.

### ML & Prediction Endpoints
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/ml/status` | ML Model status & feature architecture |
| GET | `/api/v1/ml/pipeline/scan` | Live ML scan across 300 synthetic employees |
| POST | `/api/v1/ml/predict/csv` | Upload 50-row synthetic CSV for batch predictions |
| GET | `/api/v1/ml/download-sample-csv` | Download 50-row sample synthetic CSV file |
| POST | `/api/v1/ml/seed-synthetic-300` | Re-seed database with 300 synthetic employees |
| POST | `/api/v1/ml/predict/manual` | Run single feature vector inference |
| POST | `/api/v1/ml/predict/{employee_id}` | Single employee behavioral threat prediction |

---

## Risk Scoring Formula

```
Insider Risk Score =
  Behavioral Anomalies       × 35%
  Privilege Misuse           × 25%
  Data Access Violations     × 20%
  Access Pattern Deviations  × 10%
  Historical Security Events × 10%
```

| Score Range | Risk Category |
|---|---|
| 0–24 | Low Risk |
| 25–49 | Medium Risk |
| 50–74 | High Risk |
| 75–100 | Critical Risk |

---

## Project Structure

```
insider-threat-system/
├── app/
│   ├── main.py                    # FastAPI app entry point (auto-seeds 300 cohort)
│   ├── core/
│   │   ├── config.py              # System settings & configuration
│   │   ├── database.py            # MySQL engine & session
│   │   └── security.py            # JWT + RBAC authorization
│   ├── models/
│   │   └── __init__.py            # SQLAlchemy ORM data models
│   ├── api/v1/
│   │   └── endpoints/
│   │       ├── ml_endpoints.py    # ML inference, CSV upload & pipeline scan
│   │       ├── simulation.py      # Real-time WebSocket simulation controller
│   │       ├── employees.py       # Employee management
│   │       └── security.py        # Anomalies, Risk, Alerts & Dashboards
│   ├── services/
│   │   ├── simulation.py          # Background worker streaming live risk ticks
│   │   └── streaming_service.py   # Dynamic Redis feature state prediction engine
│   └── ml/
│       ├── feature_engineering.py # 20-feature vector extraction
│       ├── inference.py          # ML Inference & SHAP Explainable AI
│       └── models/                # Trained .pkl & .pth model weights
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── ml/PredictionPlaygroundPage.js # ML Pipeline, CSV Upload & Manual Test
│   │   │   └── dashboard/DashboardPage.js     # Real-time SOC dashboard
│   │   └── utils/store.js         # Zustand store & WebSocket live feed
├── scripts/
│   ├── seed_synthetic_300.py      # 300 synthetic cohort employee dataset seeder
│   └── generate_synthetic_csvs.py # 50-row synthetic test CSV generator
├── data/synthetic_csvs/           # Pre-generated 50-row test CSV files
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```
