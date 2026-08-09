# Insider Threat Behavioral Intelligence System

AI-powered platform for continuous employee activity monitoring, behavioral anomaly
detection, insider risk scoring, and threat investigation — built with FastAPI + MySQL.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | Python 3.11 + FastAPI |
| Database | MySQL 8.0 (primary) |
| Cache | Redis 7 |
| ML Models | Isolation Forest, XGBoost, Z-score |
| Auth | JWT (access + refresh tokens) + OAuth2 |
| Deployment | Docker + Docker Compose |

---

## Quick Start

### 1. Clone & configure

```bash
git clone <repo>
cd insider-threat-system
cp .env.example .env
# Edit .env with your MySQL password and secret key
```

### 2. Start with Docker

```bash
docker-compose up -d
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### 3. Or run locally

```bash
# MySQL must be running and configured in .env
pip install -r requirements.txt
python scripts/seed.py          # create tables + demo data
uvicorn app.main:app --reload
```

---

## Default Login Credentials (after seeding)

| Role | Email | Password |
|---|---|---|
| Administrator | admin@company.com | Admin123! |
| Security Manager | manager@company.com | Manager123! |
| Security Analyst | analyst@company.com | Analyst123! |
| SOC Engineer | soc@company.com | SOC123!pwd |

---

## Dataset Setup (CERT Insider Threat Dataset)

> **Recommended over LANL** — CERT r4.2 has pre-labeled insider/benign activities
> across logon, file, device, email, and HTTP logs, matching all 13 system modules.

**Download**: https://kilthub.cmu.edu/articles/dataset/Insider_Threat_Test_Dataset/12841247

**Files needed**: `logon.csv`, `file.csv`, `device.csv`, `email.csv`, `http.csv`

**Upload via API** (after seeding employees):

```bash
# Get a JWT token first
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"analyst@company.com","password":"Analyst123!"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Upload each CERT log file
for log_type in logon file device email http; do
  curl -X POST "http://localhost:8000/api/v1/activities/cert/upload/${log_type}" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@./data/cert/${log_type}.csv"
done
```

**Note**: CERT user IDs (e.g. `AAA0001`) must match `employee_id` in the `employees` table.
Run the seed script first, then map CERT user IDs to your seeded employees.

---

## API Overview

Base URL: `http://localhost:8000/api/v1`

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | /auth/register | Create new analyst account |
| POST | /auth/login | Login → access + refresh tokens |
| POST | /auth/refresh | Refresh access token |
| GET  | /auth/me | Current user profile |
| PUT  | /auth/change-password | Change password |

### Employees
| Method | Endpoint | Description |
|---|---|---|
| POST | /employees | Onboard new employee |
| GET  | /employees | List all employees (paginated) |
| GET  | /employees/{id} | Employee detail + risk summary |
| PUT  | /employees/{id} | Update employee |
| DELETE | /employees/{id} | Terminate employee |
| GET  | /employees/departments | List departments |
| POST | /employees/{id}/devices | Register device |

### Activity Monitoring
| Method | Endpoint | Description |
|---|---|---|
| POST | /activities | Log single activity |
| POST | /activities/bulk | Bulk JSON ingest |
| POST | /activities/cert/upload/{type} | Upload CERT CSV file |
| GET  | /activities | Query activity logs |
| GET  | /activities/stats/summary | Activity statistics |

### Anomaly Detection
| Method | Endpoint | Description |
|---|---|---|
| POST | /anomalies/detect/{employee_id} | Run detection for employee |
| POST | /anomalies/train-model | Train Isolation Forest |
| GET  | /anomalies | List anomalies (filtered) |
| PUT  | /anomalies/{id}/review | Mark confirmed/false positive |

### Risk Scoring
| Method | Endpoint | Description |
|---|---|---|
| POST | /risk/score/{employee_id} | Calculate risk score |
| POST | /risk/score-all | Batch score all employees |
| GET  | /risk/leaderboard | Top risk employees |
| GET  | /risk/{employee_id}/history | Risk score history |

### Alerts
| Method | Endpoint | Description |
|---|---|---|
| POST | /alerts | Create alert |
| GET  | /alerts | List alerts (filtered) |
| PUT  | /alerts/{id} | Update status / assign |

### Incidents
| Method | Endpoint | Description |
|---|---|---|
| POST | /incidents | Create investigation |
| GET  | /incidents | List incidents |
| GET  | /incidents/{id}/timeline | Activity timeline reconstruction |
| PUT  | /incidents/{id} | Update investigation |

### Dashboards
| Method | Endpoint | Description |
|---|---|---|
| GET | /dashboard/security-analyst | Analyst view |
| GET | /dashboard/soc | SOC operations view |
| GET | /dashboard/manager | Manager/executive view |

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
| 0–24 | Low |
| 25–49 | Medium |
| 50–74 | High |
| 75–100 | Critical |

---

## ML Models

| Model | Purpose | Training |
|---|---|---|
| Isolation Forest | Unsupervised peer deviation detection | `POST /anomalies/train-model` |
| Z-score analysis | Personal baseline deviation | Auto (on profile build) |
| Rule-based | Off-hours, USB, data volume rules | Always-on |

---

## Project Structure

```
insider-threat-system/
├── app/
│   ├── main.py                    # FastAPI app entry point
│   ├── core/
│   │   ├── config.py              # Settings (pydantic-settings)
│   │   ├── database.py            # MySQL engine + session
│   │   └── security.py            # JWT + RBAC
│   ├── models/
│   │   └── __init__.py            # All SQLAlchemy ORM models
│   ├── schemas/
│   │   └── __init__.py            # All Pydantic v2 schemas
│   ├── api/v1/
│   │   ├── __init__.py            # Router aggregation
│   │   └── endpoints/
│   │       ├── auth.py            # Module 1: Authentication
│   │       ├── employees.py       # Module 2: Employee Management
│   │       ├── activities.py      # Module 3: Activity Monitoring + CERT ingest
│   │       └── security.py        # Modules 5–10: Anomaly / Risk / Alerts / Dashboard
│   ├── services/
│   │   └── ml_service.py          # Modules 4–6: Profiling / Detection / Scoring
│   └── ml/models/                 # Trained model files (.pkl)
├── scripts/
│   ├── seed.py                    # Demo data seeder
│   └── init.sql                   # MySQL init script
├── data/cert/                     # Place CERT CSV files here
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## Environment Variables

See `.env.example` for all options. Key variables:

```
DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/insider_threat_db
SECRET_KEY=your-32-char-secret
WEIGHT_BEHAVIORAL_ANOMALIES=0.35
RISK_THRESHOLD_CRITICAL=90
```
