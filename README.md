# Insider-Threat-Behavioral-Intelligence-System

# Insider Threat Behavioral Intelligence System

An AI-powered Insider Threat Behavioral Intelligence System that continuously monitors employee activities, analyzes behavioral patterns, detects anomalies, predicts insider risk, and assists security teams in investigating potential insider threats.

The system leverages the CERT R4.2 Insider Threat Dataset, Machine Learning, User and Entity Behavior Analytics (UEBA), FastAPI, React.js, PostgreSQL, and Docker to provide an end-to-end behavioral intelligence platform.

---

# Project Overview

Insider threats are among the most challenging cybersecurity risks because they originate from trusted users within an organization. This project develops an intelligent platform capable of learning normal employee behavior and detecting suspicious activities such as abnormal login patterns, excessive file transfers, unauthorized USB usage, unusual email communication, and privilege misuse.

The platform provides real-time risk assessment, behavioral profiling, anomaly detection, security dashboards, and investigation support for Security Operations Centers (SOC).

---

# Features

- Role-Based Authentication
- Employee Profile Management
- Activity Log Monitoring
- Behavioral Profiling Engine
- User & Entity Behavior Analytics (UEBA)
- Feature Engineering Pipeline
- Machine Learning Risk Prediction
- Insider Risk Scoring
- Threat Alerts
- Investigation Dashboard
- Risk Trend Visualization
- Report Generation
- REST API using FastAPI
- Responsive React Dashboard
- Docker Deployment

---

# Technology Stack

## Frontend

- React.js
- Tailwind CSS
- Chart.js

## Backend

- FastAPI
- Python

## Database

- PostgreSQL

## Machine Learning

- Scikit-Learn
- XGBoost
- Pandas
- NumPy
- Joblib

## Visualization

- Plotly
- Chart.js

## Deployment

- Docker
- Docker Compose

---

# Project Architecture

```
                 CERT R4.2 Dataset
                        │
                        ▼
               Data Preprocessing
                        │
                        ▼
              Feature Engineering
                        │
                        ▼
            Behavioral Feature Dataset
                        │
                        ▼
              Machine Learning Model
                        │
                        ▼
               Insider Risk Prediction
                        │
                        ▼
                FastAPI REST APIs
                        │
         PostgreSQL Database
                        │
                        ▼
                React Dashboard
                        │
                        ▼
       Security Analyst / SOC / Admin
```

---

# Dataset

Dataset Used

- CERT Insider Threat Dataset R4.2

Activity Sources

- Logon Activity
- Device Activity
- Email Activity
- File Activity
- HTTP Activity

---

# Machine Learning Pipeline

```
Raw CERT Dataset

↓

Data Cleaning

↓

Missing Value Handling

↓

Merge Activity Logs

↓

Feature Engineering

↓

Behavioral Indicators

↓

Feature Selection

↓

Model Training

↓

Risk Prediction

↓

Model Serialization (.pkl)
```

---

# Behavioral Features

The feature engineering pipeline extracts behavioral indicators including:

- Total Login Count
- Night Login Count
- Weekend Login Count
- USB Usage
- Email Count
- External Email Count
- File Download Count
- File Upload Count
- Sensitive File Access
- HTTP Requests
- Unique Websites
- Device Usage
- Failed Login Attempts
- Login Duration
- Session Frequency
- Data Transfer Volume

These features are aggregated per employee and used to train the machine learning model.

---

# Risk Categories

The prediction engine classifies employees into four risk levels.

- Low Risk
- Medium Risk
- High Risk
- Critical Risk

---

# Project Structure

```
Insider-Threat-System/

│

├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── backend/
│   ├── app.py
│   ├── routes/
│   ├── services/
│   └── database.py
│
├── dataset/
│   ├── logon.csv
│   ├── email.csv
│   ├── device.csv
│   ├── file.csv
│   └── http.csv
│
├── pipeline/
│   ├── preprocess.py
│   ├── feature_engineering.py
│   ├── train_model.py
│   └── predict.py
│
├── models/
│   └── insider_model.pkl
│
├── reports/
│
├── docker/
│
├── requirements.txt
│
└── README.md
```

---
# Running the Machine Learning Pipeline

Generate behavioral features

```bash
python pipeline/feature_engineering.py
```

Train the model

```bash
python pipeline/train_model.py
```

Predict insider risk

```bash
python pipeline/predict.py
```

---

# Running the Backend

```bash
uvicorn app:app --reload
```

---

# Running the Frontend

```bash
npm install
npm start
```

---

# Dashboard Modules

### Administrator

- User Management
- Employee Profiles
- System Configuration
- Audit Logs

### Security Analyst

- Threat Alerts
- Risk Scores
- Behavioral Analysis
- Investigation Queue

### SOC Engineer

- Live Security Events
- Activity Timeline
- Event Correlation
- Incident Management

### Security Manager

- Organization Risk Overview
- Risk Trends
- Compliance Reports
- Executive Dashboard

---

# Future Enhancements

- Real-Time Log Streaming
- Explainable AI (XAI)
- Deep Learning-Based UEBA
- SIEM Integration
- Multi-Tenant Support
- Cloud Deployment
- Real-Time Alert Notifications
- Automated Threat Response

---

# Performance Metrics

- Accuracy
- Precision
- Recall
- F1 Score
- ROC-AUC
- False Positive Rate
- Mean Time to Detect (MTTD)
- Mean Time to Investigate (MTTI)
- Mean Time to Respond (MTTR)

---

# Contributors

- G. Udaya Kumar

---

# License

This project is developed for educational and research purposes. The CERT Insider Threat Dataset is used strictly in accordance with its licensing and research guidelines.

---

# Acknowledgements

- Carnegie Mellon University CERT Division
- CERT Insider Threat Dataset
- FastAPI
- React.js
- Scikit-Learn
- XGBoost
- PostgreSQL
- Docker
