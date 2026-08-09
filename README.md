# AI Insider Threat Behavioral Intelligence System

A Machine Learning-based **Insider Threat Behavioral Intelligence System** designed to analyze employee activities, identify abnormal behavior, calculate risk scores, and support security investigations using the **CERT Insider Threat Dataset (Release 4.2)**.

The system combines behavioral feature engineering, user behavior baselines, anomaly detection, behavior deviation analysis, risk scoring, explainable predictions, threat investigation, live feature processing, and an interactive web dashboard.

---

## 📌 Project Overview

Insider threats are security risks caused by users who have legitimate access to an organization's systems but may perform unusual or potentially harmful activities.

This project analyzes employee behavioral activity and generates a **risk score** based on deviations from normal behavior.

The system is designed around the following workflow:

```text
CERT Insider Threat Dataset
            │
            ▼
      Data Preparation
            │
            ▼
    Feature Engineering
            │
            ▼
    Behavioral Baseline
            │
            ▼
   Behavior Deviation
            │
            ▼
     Anomaly Detection
            │
            ▼
       Risk Scoring
            │
            ▼
 Explainable Prediction
            │
            ▼
 Threat Investigation
            │
            ▼
 FastAPI Backend
            │
            ▼
 React Dashboard
```

---

# 📂 Dataset

### CERT Insider Threat Dataset – Release 4.2

The project uses the **CERT Insider Threat Dataset Release 4.2** to analyze employee activity patterns.

The dataset contains multiple activity sources, including:

* Logon / Logoff activity
* Device activity
* Email activity
* File activity
* HTTP activity

These activities are transformed into behavioral features that can be used for anomaly detection and risk analysis.

---

# 📁 Complete Project Structure

```text
AI-Insider-Threat-Behavioral-Intelligence-System/
│
├── backend/
│   │
│   ├── app.py
│   ├── dashboard.py
│   ├── Dockerfile
│   ├── requirements.txt
│   │
│   ├── live/
│   │   └── feature_engine.py
│   │
│   ├── sample/
│   │   └── data.py
│   │
│   ├── stream/
│   │   └── processor.py
│   │
│   └── user/
│       └── activity.py
│
├── dataset/
│   │
│   ├── create/
│   │   └── dataset.py
│   │
│   └── train_and_save.py
│
├── frontend/
│   │
│   ├── public/
│   │   └── index.html
│   │
│   ├── src/
│   │   │
│   │   ├── api/
│   │   │   └── axios.js
│   │   │
│   │   ├── components/
│   │   │   ├── AlertPanel.jsx
│   │   │   ├── Chart.jsx
│   │   │   ├── Navbar.jsx
│   │   │   ├── RiskCard.jsx
│   │   │   └── Sidebar.jsx
│   │   │
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   │
│   │   ├── hooks/
│   │   │   └── useFetch.js
│   │   │
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Employees.jsx
│   │   │   ├── Investigation.jsx
│   │   │   ├── Login.jsx
│   │   │   └── Reports.jsx
│   │   │
│   │   ├── styles/
│   │   │   └── index.css
│   │   │
│   │   ├── App.jsx
│   │   └── main.jsx
│   │
│   └── package.json
│
├── ml_model/
│   │
│   ├── anomaly_detection.py
│   ├── behavior_baseline.py
│   ├── behavior_deviation.py
│   ├── explain_prediction.py
│   ├── feature_engineering.py
│   ├── preprocess.py
│   ├── risk_scoring.py
│   ├── threat_investigation.py
│   └── train_and_save.py
│
├── docker-compose.yml
│
└── README.md
```

---

# 🧠 Machine Learning Pipeline

The ML component is divided into independent modules so that preprocessing, feature engineering, anomaly detection, risk scoring, and investigation can be developed and tested separately.

## 1. Data Preprocessing

**File:**

```text
ml_model/preprocess.py
```

Responsible for preparing raw behavioral data for machine learning.

Typical operations include:

* Loading datasets
* Handling missing values
* Cleaning inconsistent records
* Converting timestamps
* Preparing numerical features
* Preparing data for model processing

---

## 2. Feature Engineering

**File:**

```text
ml_model/feature_engineering.py
```

Transforms raw employee activities into behavioral indicators.

Examples include:

* Login frequency
* Night-time activity
* Weekend activity
* Device usage
* File activity
* Email activity
* HTTP activity
* Activity frequency
* Behavioral activity counts

The objective is to convert raw events into meaningful employee-level behavioral features.

---

## 3. Behavioral Baseline

**File:**

```text
ml_model/behavior_baseline.py
```

Creates a representation of an employee's normal behavioral pattern.

The baseline can be used to answer:

```text
What does normal behavior look like for this employee?
```

This provides the reference point for detecting behavioral deviations.

---

## 4. Behavior Deviation

**File:**

```text
ml_model/behavior_deviation.py
```

Compares current employee behavior against the established behavioral baseline.

Conceptually:

```text
Current Behavior
       │
       ▼
Compare With Baseline
       │
       ▼
Behavior Deviation
```

Large deviations can indicate potentially suspicious behavior.

---

## 5. Anomaly Detection

**File:**

```text
ml_model/anomaly_detection.py
```

Identifies unusual behavioral patterns using machine learning/anomaly detection techniques.

The output can be used to identify:

* Normal users
* Unusual users
* Highly abnormal activity
* Potential insider-threat indicators

---

## 6. Risk Scoring

**File:**

```text
ml_model/risk_scoring.py
```

Converts behavioral and anomaly information into a consolidated risk score.

A conceptual output is:

```text
Employee
   │
   ├── Behavioral Score
   ├── Deviation Score
   ├── Anomaly Score
   └── Activity Indicators
            │
            ▼
       Risk Score
```

The resulting score can be used by the dashboard to categorize employee risk.

Example:

```text
0 ─────────────── 100
│                  │
Low              Critical
Risk              Risk
```

---

## 7. Explainable Prediction

**File:**

```text
ml_model/explain_prediction.py
```

Provides explanations for model predictions and risk assessments.

Instead of simply displaying:

```text
Risk Score: 87
```

the system can provide supporting behavioral factors such as:

```text
High Risk

Reasons:
- Unusual login time
- Increased file activity
- Abnormal device usage
- Significant deviation from baseline
```

This makes the system more useful for security analysis and investigation.

---

## 8. Threat Investigation

**File:**

```text
ml_model/threat_investigation.py
```

Provides functionality for analyzing suspicious employee activity in greater detail.

It can be used as a bridge between automated risk detection and manual security investigation.

---

## 9. Model Training

**File:**

```text
ml_model/train_and_save.py
```

Responsible for training the machine learning model and saving the trained model for later prediction.

The dataset preparation workflow is also supported by:

```text
dataset/train_and_save.py
```

---

# ⚡ Backend

The backend provides the interface between the ML system and the frontend dashboard.

```text
backend/
├── app.py
├── dashboard.py
├── Dockerfile
├── requirements.txt
├── live/
├── sample/
├── stream/
└── user/
```

## Backend Components

### `app.py`

Main backend application entry point.

It provides the API layer through which the frontend communicates with the backend services.

### `dashboard.py`

Provides dashboard-related backend functionality and data required by the frontend.

### `live/feature_engine.py`

Handles live behavioral feature processing.

This allows newly received activities to be transformed into features suitable for real-time analysis.

### `stream/processor.py`

Handles activity stream processing.

Conceptually:

```text
Activity Event
      │
      ▼
Stream Processor
      │
      ▼
Feature Extraction
      │
      ▼
Risk Analysis
```

### `user/activity.py`

Handles employee/user activity information.

### `sample/data.py`

Provides sample data for testing and development.

### `requirements.txt`

Contains Python dependencies required by the backend.

### `Dockerfile`

Defines the backend container configuration.

---

# 🌐 Frontend

The frontend is implemented using **React** and provides an interactive security dashboard.

```text
frontend/
├── public/
├── src/
└── package.json
```

## Frontend Architecture

### API Layer

```text
frontend/src/api/axios.js
```

Handles communication between the React application and backend APIs.

---

### Components

```text
frontend/src/components/
```

#### `AlertPanel.jsx`

Displays security alerts and suspicious activity notifications.

#### `Chart.jsx`

Displays behavioral/risk information using charts.

#### `Navbar.jsx`

Provides the main navigation interface.

#### `RiskCard.jsx`

Displays employee risk information and risk scores.

#### `Sidebar.jsx`

Provides dashboard navigation.

---

### Authentication

```text
frontend/src/context/AuthContext.jsx
```

Provides authentication state and access management across the React application.

---

### Custom Hooks

```text
frontend/src/hooks/useFetch.js
```

Provides reusable data-fetching functionality.

---

### Dashboard Pages

```text
frontend/src/pages/
```

#### `Login.jsx`

Authentication/login interface.

#### `Dashboard.jsx`

Main security monitoring dashboard.

#### `Employees.jsx`

Displays employee information and risk status.

#### `Investigation.jsx`

Provides an interface for investigating suspicious employee behavior.

#### `Reports.jsx`

Provides access to security/risk reports.

---

### Styling

```text
frontend/src/styles/index.css
```

Contains the application's global styling.

---

# 🖥️ Dashboard Features

The current frontend architecture supports a security-monitoring interface containing:

* Authentication
* Employee monitoring
* Risk cards
* Behavioral charts
* Security alerts
* Employee investigation
* Reports
* Dashboard navigation
* Backend API communication

---

# 🔄 Live Behavioral Processing

The project also includes modules for processing behavioral activity dynamically.

```text
Employee Activity
       │
       ▼
Stream Processor
       │
       ▼
Live Feature Engine
       │
       ▼
Behavioral Features
       │
       ▼
Anomaly Detection
       │
       ▼
Risk Scoring
       │
       ▼
Dashboard
```

This architecture allows the project to move beyond static dataset analysis toward a behavioral monitoring system.

---

# 🐳 Docker Support

The project includes Docker configuration:

```text
backend/Dockerfile
docker-compose.yml
```

Docker can be used to simplify deployment and provide a consistent execution environment for the application.

---

# 🛠️ Technology Stack

| Category             | Technology                              |
| -------------------- | --------------------------------------- |
| Programming Language | Python                                  |
| Data Processing      | Pandas, NumPy                           |
| Machine Learning     | Scikit-learn                            |
| Visualization        | Matplotlib                              |
| Backend              | FastAPI                                 |
| Frontend             | React                                   |
| API Communication    | Axios                                   |
| Authentication       | React Authentication Context            |
| Database             | Project-dependent / backend integration |
| Containerization     | Docker                                  |
| Dataset              | CERT Insider Threat Dataset Release 4.2 |

---

# 📊 Project Modules

| Module                   |     Status    |
| ------------------------ | :-----------: |
| Dataset Research         |  ✅ Completed  |
| Dataset Creation         |  ✅ Completed  |
| Data Preprocessing       |  ✅ Completed  |
| Feature Engineering      |  ✅ Completed  |
| Behavioral Baseline      |  ✅ Completed  |
| Behavior Deviation       |  ✅ Completed  |
| Anomaly Detection        |  ✅ Completed  |
| Risk Scoring             |  ✅ Completed  |
| Model Training           |  ✅ Completed  |
| Prediction Explanation   |  ✅ Completed  |
| Threat Investigation     |  ✅ Completed  |
| Live Feature Engineering |  ✅ Completed  |
| Stream Processing        |  ✅ Completed  |
| Backend API              | ✅ Implemented |
| Dashboard Backend        | ✅ Implemented |
| React Frontend           | ✅ Implemented |
| Authentication Context   | ✅ Implemented |
| Employee Dashboard       | ✅ Implemented |
| Investigation Interface  | ✅ Implemented |
| Reports Interface        | ✅ Implemented |
| Docker Configuration     | ✅ Implemented |

---

# 🎯 Current Project Workflow

The implemented project can be represented as:

```text
                    ┌──────────────────────┐
                    │ CERT Dataset 4.2     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Dataset Creation     │
                    │ & Preparation        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Preprocessing        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Feature Engineering  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Behavior Baseline    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Behavior Deviation   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Anomaly Detection    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Risk Scoring         │
                    └──────────┬───────────┘
                               │
                     ┌─────────┴─────────┐
                     ▼                   ▼
          ┌──────────────────┐   ┌──────────────────┐
          │ Explainability   │   │ Investigation    │
          └────────┬─────────┘   └────────┬─────────┘
                   │                      │
                   └──────────┬───────────┘
                              ▼
                    ┌──────────────────────┐
                    │ Backend / API        │
                    └──────────┬───────────┘
                               │
                              API
                               │
                               ▼
                    ┌──────────────────────┐
                    │ React Dashboard      │
                    └──────────────────────┘
```

---

# 📈 Risk Analysis

The system combines multiple behavioral signals rather than relying on a single activity.

```text
Login Behavior
      +
Device Behavior
      +
Email Behavior
      +
File Behavior
      +
HTTP Behavior
      +
Behavior Deviation
      +
Anomaly Detection
      │
      ▼
   Risk Score
      │
      ▼
Risk Classification
      │
      ├── Low
      ├── Medium
      ├── High
      └── Critical
```

---

# 🔍 Explainable Security Analysis

The system is designed to answer two important questions:

### 1. Who is behaving abnormally?

```text
Employee → Anomaly Detection → Risk Score
```

### 2. Why is the employee considered risky?

```text
Risk Score
    │
    ▼
Behavior Deviation
    │
    ▼
Important Behavioral Factors
    │
    ▼
Investigation
```

This makes the project more suitable for practical security monitoring than a simple binary classification model.

---

# 🚀 Future Improvements

Although the core architecture is implemented, the project can be further improved with:

* Real-time WebSocket-based monitoring
* More advanced anomaly detection models
* SHAP-based model explanations
* Automated email/security alerts
* Persistent database integration
* Role-based access control
* Advanced investigation timelines
* PDF report generation
* Model performance monitoring
* Automated retraining
* Production deployment
* Containerized frontend deployment
* Cloud deployment

---

# 📌 Project Status

**Overall Status: 🚀 Advanced Development / Integrated Prototype**

The project has progressed from basic dataset analysis to an integrated **ML + behavioral intelligence + backend + React dashboard + Docker** architecture.

The major components for:

* Data preparation
* Behavioral feature engineering
* Baseline analysis
* Deviation detection
* Anomaly detection
* Risk scoring
* Prediction explanation
* Threat investigation
* Backend processing
* Live feature processing
* Stream processing
* React dashboard
* Authentication
* Docker configuration

are now implemented in the project structure.

---

# 👨‍💻 Author

**Mohammad Yusuf**

B.Tech – Computer Science & Engineering
Pranveer Singh Institute of Technology (PSIT), Kanpur
**Infosys Springboard Internship – 2026**

---

## 📄 Project Purpose

This project is developed as an academic and internship-oriented implementation for studying **Machine Learning, behavioral analytics, anomaly detection, and insider-threat detection** using the CERT Insider Threat Dataset.
