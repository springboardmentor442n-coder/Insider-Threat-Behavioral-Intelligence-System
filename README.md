# Insider Threat Behavioral Intelligence System

SentinelAI is an AI-powered insider threat detection and behavioral intelligence platform designed to analyze employee activities and identify potential malicious behaviors. Built using the CERT Insider Threat Dataset R4.2, the system evaluates multi-source log telemetry to detect behavioral anomalies using unsupervised machine learning models. The platform combines behavioral analytics, 7-model anomaly detection, weighted risk scoring, SHAP-based feature explainability, CERT Layer 2 behavioral verification, threat investigation workflows, and multi-format reporting into a unified web application.

---

## Key Features

- **OAuth2 & JWT Authentication**: Supports JWT bearer tokens and standard OAuth2 password request flows.
- **Role-Based Access Control (RBAC)**: Enforces role permissions for Security Analyst, SOC Engineer, Security Manager, and Administrator users.
- **Employee Behavioral Profiling**: Aggregates historical activity baselines across 1,000 evaluated employees.
- **CERT R4.2 Activity Monitoring**: Ingestion and query APIs for logon, file, email, HTTP web browsing, and removable USB activities.
- **7-Model Unsupervised Ensemble**: Anomaly detection combining Isolation Forest, One-Class SVM, LOF, Elliptic Envelope, PCA, DBSCAN, and K-Means.
- **0–100 Insider Risk Scoring**: Weighted scoring engine evaluating anomalies, privilege misuse, and data exfiltration with model consensus metrics.
- **Threat Center Management**: Interactive security operations hub to filter, search, inspect, and manage active insider threat alerts.
- **Behavioral Explainability**: Feature contribution breakdowns providing SHAP-based behavioral insights for flagged anomalies.
- **CERT Layer 2 Verification**: Population-level baseline validation comparing employee behaviors against statistical P90 thresholds.
- **Incident Investigation Workflow**: Dedicated case file management (`CASE-AJF0370`) supporting timeline tracking, evidence collection, and status escalation.
- **Real-Time Notifications**: Unread stream popover for security alerts, investigation changes, and system updates.
- **Analytics & Model Performance**: Comparative metrics visualizer for anomaly distribution, risk levels, and model performance.
- **Reports & Multi-Format Export**: 19 canonical system intelligence reports supporting live CSV, XLSX, and PDF exports.
- **Role-Aware Dashboards**: Dynamic security dashboard views customized for Analyst, SOC, Manager, and Admin roles.
- **Telemetry & Monitoring**: Structured request logging middleware with correlation IDs (`X-Request-ID`), response timing (`X-Response-Time-Ms`), and health/readiness endpoints (`/health`, `/ready`).

---

## Machine Learning

The system uses a seven-model unsupervised anomaly detection ensemble consisting of Isolation Forest, One-Class SVM, Local Outlier Factor (LOF), Elliptic Envelope, Principal Component Analysis (PCA), DBSCAN, and K-Means. Their outputs are combined to derive model consensus and contribute to a normalized 0–100 insider risk score without requiring historical attack labels.

---

## Behavioral Intelligence

The platform extracts and analyzes behavioral dimensions from CERT R4.2 logs, including:
- **Logon Activity**: Login/logout timestamps, off-hours activity, and midnight access frequency.
- **File System Operations**: File copy frequency, removable drive transfers, and exfiltration indicators.
- **USB & Device Usage**: Removable media connection counts and external drive events.
- **Email Communication**: External recipient volume, off-hours emails, and attachment sizes.
- **Web Browsing**: HTTP request counts, external domain visits, and file download events.
- **Temporal & Baseline Patterns**: Activity variations evaluated against population-level statistical baselines.

---

## System Modules

| Module | Purpose |
|---|---|
| **Dashboard** | Enterprise security posture, risk metrics, and active threats |
| **Threat Center** | Alert triage hub to detect, search, filter, and inspect suspicious employees |
| **Employees** | Employee intelligence profiles, risk scores, and activity indicators |
| **Analytics** | Risk distribution analytics, trend charts, and model comparison metrics |
| **Models** | Machine learning model summaries and performance metrics |
| **Explainability** | SHAP-based feature contribution analysis and behavioral factors |
| **Verification** | Layer 2 CERT pattern validation against population P90 baseline thresholds |
| **Investigation** | Case creation, timeline tracking, evidence collection, and status escalation |
| **Reports** | 19 canonical intelligence reports with multi-format export (CSV, XLSX, PDF) |
| **Settings / Account** | User profile details, session management, and preferences |
| **User Management** | Administrative RBAC management for user roles and account statuses |

---

## Technology Stack

- **Frontend**: React 19, Vite, Tailwind CSS, Framer Motion, Recharts, TanStack React Query, Axios.
- **Backend**: Python 3.11, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy, Alembic, OAuth2/JWT.
- **Data & ML**: Pandas, NumPy, Scikit-learn, PyArrow, Parquet, CERT Insider Threat Dataset R4.2.

---

## Project Structure

```text
Insider-Threat-Behavioral-Intelligence-System/
├── backend/                  # FastAPI REST APIs, authentication, services, ML pipeline, and DB models
├── insider-threat-frontend/  # React + Vite web application and cybersecurity UI components
├── datasets/                 # Processed CERT R4.2 dataset features and Parquet files
├── models/                   # Serialized ML model binaries and scaler artifacts
├── notebooks/                # Feature engineering, model evaluation, and exploratory notebooks
├── scripts/                  # Data cleaning, feature extraction, and pipeline scripts
├── tests/                    # Automated unit, integration, RBAC, and performance test suites
├── docs/                     # Technical documentation and user guides
└── reports/                  # Generated CSV, XLSX, and PDF system intelligence exports
```

---

## Setup & Running

### Single-Script Automated Startup (PowerShell)
```powershell
.\start.ps1
```

### Manual Setup
1. **Backend**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python -m uvicorn backend.app:app --reload --port 8000
   ```
2. **Frontend**:
   ```bash
   cd insider-threat-frontend
   npm install
   npm run dev
   ```

Access web UI at `http://localhost:5173` and API docs at `http://127.0.0.1:8000/docs`.

---

## Testing & Validation

Automated test suites in `tests/` cover:
- **OAuth2 & Authentication**: Login flow, token generation, `/token` endpoint, `/me` profile.
- **Activity Monitoring APIs**: Summary, types, statistics, timeline, and employee logs.
- **Role-Based Access Control**: Server-side RBAC validation and authorization enforcement.
- **API & E2E Workflows**: Route validation across 11 system router modules.
- **Security & Performance**: Error status handling, missing JWT protection, and sub-5ms API latency benchmarks.

Run tests via Python:
```bash
python tests/test_oauth2_auth.py
python tests/test_activity_monitoring.py
python tests/test_role_dashboards.py
python tests/test_system_and_performance.py
```

---

## Documentation

Comprehensive technical specifications and operational guides in `docs/`:

| Document | Description |
|---|---|
| [Architecture](docs/ARCHITECTURE.md) | High-level system architecture and microservices specification |
| [Installation](docs/INSTALLATION.md) | Environment setup, installation, and startup guide |
| [Authentication](docs/AUTHENTICATION.md) | OAuth2 Password Flow and JWT token security details |
| [RBAC](docs/RBAC.md) | Role-Based Access Control matrix and permissions |
| [Activity Monitoring](docs/ACTIVITY_MONITORING.md) | CERT R4.2 activity collection and monitoring APIs |
| [Dashboards](docs/DASHBOARDS.md) | Role-specific dashboard views and capabilities |
| [Investigation](docs/INVESTIGATION.md) | Threat investigation workflows and case management |
| [Reports](docs/REPORTS.md) | 19 canonical intelligence reports and multi-format exports |
| [API Reference](docs/API.md) | Complete REST API endpoint documentation |
| [Testing Guide](docs/TESTING.md) | Automated testing suite and validation procedures |
| [Security](docs/SECURITY.md) | Platform security, zero-log policies, and hardening |
| [Monitoring](docs/MONITORING.md) | Structured request logging middleware and telemetry |
| [User Guide](docs/USER_GUIDE.md) | End-user guide for security analysts and SOC teams |

---

## Project Status

SentinelAI provides a functional insider threat detection platform combining 7-model unsupervised anomaly detection, weighted risk scoring, CERT behavioral verification, case investigation workflows, multi-format reporting, OAuth2/RBAC security, automated test suites, and structured request telemetry.
