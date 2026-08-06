# Insider Threat Behavioral Intelligence System

<div align="center">

# 🛡️ Insider Threat Behavioral Intelligence System

### AI-Powered Enterprise Insider Threat Detection & Behavioral Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-Frontend-646CFF.svg)](https://vitejs.dev/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-Styling-38B2AC.svg)](https://tailwindcss.com/)
[![Machine Learning](https://img.shields.io/badge/Machine%20Learning-7%20Models-orange.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

An Enterprise-grade AI-powered Behavioral Intelligence Platform capable of detecting malicious insider activities using behavioral analytics, anomaly detection, machine learning, and interactive security dashboards.

</div>

---

# 📖 Overview

The **Insider Threat Behavioral Intelligence System** is a complete end-to-end cybersecurity platform developed for detecting malicious insider activities within enterprise organizations.

Instead of relying only on signature-based detection, the system analyzes employee behavioral patterns from multiple enterprise logs to identify suspicious users using unsupervised machine learning techniques.

The platform combines:

- Behavioral Analytics
- Machine Learning
- Enterprise Security Dashboard
- Threat Management
- Employee Risk Scoring
- Interactive Investigation Tools
- FastAPI REST APIs
- Modern React Frontend

The project uses the **CERT Insider Threat Dataset (R4.2)** as its primary dataset.

---

# 🎯 Objectives

The primary objective of this project is to build an intelligent insider threat detection platform capable of

- Detecting suspicious employee behavior
- Calculating employee risk scores
- Ranking high-risk employees
- Providing AI-assisted threat investigation
- Visualizing enterprise security metrics
- Supporting cybersecurity analysts during investigations

---

# 🚀 Current Project Progress

**Overall Progress:** **~88%**

---

## ✅ Completed

### 📂 Data Engineering

- Dataset Inventory
- Dataset Profiling
- Data Dictionary Generation
- Data Cleaning Pipeline
- Dataset Integration
- Feature Engineering
- Data Validation
- Data Quality Reports

---

### 🤖 Machine Learning

- Isolation Forest
- One-Class SVM
- Local Outlier Factor
- Elliptic Envelope
- PCA Reconstruction
- DBSCAN
- K-Means

Additional completed work

- Consensus Risk Scoring
- Employee Risk Ranking
- Model Comparison
- Model Evaluation
- Risk Distribution
- Employee Risk Reports

---

### ⚙ Backend

Completed backend modules

- FastAPI Backend
- JWT Authentication
- Role-Based Authorization
- Employee CRUD APIs
- Dashboard APIs
- Threat APIs
- Activity APIs
- Analytics APIs
- Report APIs
- Authentication APIs

Implemented features

- REST API Architecture
- Modular Backend
- SQLAlchemy ORM
- Pydantic Validation
- LDAP Employee Integration
- Risk Scoring APIs

---

### 💻 Frontend

Completed modules

- Login
- Enterprise Dashboard
- Threat Center
- Employee Management
- Protected Routes
- React Query Integration

Completed Dashboard

- Hero Banner
- Animated Metric Cards
- Live Activity Feed
- AI Insights Panel
- Threat Trend Chart
- Investigation Queue
- Top Suspicious Employees
- System Status Panel

Completed Threat Center

- Threat Overview Cards
- Threat Table
- Search
- Filtering
- Sorting
- Threat Details Drawer
- Resolve Threat Dialog
- Delete Threat Dialog

Completed UI

- Enterprise Layout
- Glassmorphism Design
- Animated Sidebar
- Modern Navigation
- Cyber Theme
- Responsive Design
- Framer Motion Animations
- Animated Counters

---

## 🚧 In Progress

- Investigation Module
- Analytics Dashboard
- Reports Module
- Settings Module
- Explainable AI
- Deployment

---

## 📌 Planned

- Docker Deployment
- Kubernetes Deployment
- Cloud Deployment
- Email Notifications
- SIEM Integration
- WebSocket Live Alerts
- SHAP Explainability
- LIME Explainability
- AI Chat Assistant

---

# 🏗 System Workflow

```text
                CERT Insider Threat Dataset
                           │
                           ▼
                 Dataset Inventory Engine
                           │
                           ▼
                   Dataset Profiling Engine
                           │
                           ▼
                 Data Dictionary Generator
                           │
                           ▼
                    Data Cleaning Pipeline
                           │
                           ▼
                  Enterprise Data Integration
                           │
                           ▼
                 Behavioral Feature Engineering
                           │
                           ▼
                 Machine Learning Models (7)
                           │
                           ▼
                Consensus Risk Score Generator
                           │
                           ▼
               Employee Behavioral Intelligence
                           │
                           ▼
                    FastAPI Backend Services
                           │
                           ▼
             Enterprise React Dashboard (Vite)
                           │
                           ▼
              Security Analyst Investigation
```

---

# 📂 Project Structure

```text
Insider-Threat-Behavioral-Intelligence-System
│
├── ai_engine/
│
├── backend/
│   ├── api/
│   ├── core/
│   ├── crud/
│   ├── data/
│   ├── auth_service/
│   ├── activity_service/
│   ├── anomaly_service/
│   ├── api_gateway/
│   ├── app.py
│   ├── settings.py
│   └── __init__.py
│
├── insider-threat-frontend/
│   ├── public/
│   ├── src/
│   │
│   ├── assets/
│   ├── components/
│   │   ├── ai/
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── investigation/
│   │   ├── layout/
│   │   ├── threat/
│   │   └── ui/
│   │
│   ├── features/
│   │   ├── dashboard/
│   │   ├── employees/
│   │   ├── threats/
│   │   ├── reports/
│   │   └── analytics/
│   │
│   ├── hooks/
│   ├── layouts/
│   ├── pages/
│   ├── routes/
│   ├── services/
│   ├── styles/
│   └── utils/
│
├── datasets/
├── models/
├── reports/
├── plots/
├── notebooks/
├── deployment/
├── scripts/
├── tests/
├── README.md
└── requirements.txt
```

---

# 📊 Dataset

The project utilizes the **CERT Insider Threat Dataset (R4.2)**.

The dataset contains multiple enterprise behavioral logs, including:

- Employee Information
- Logon Activities
- Device Usage
- Email Communications
- HTTP Browsing History
- File Access Logs
- USB Activity
- Psychometric Data

> **Note:** Due to the large size of the CERT dataset, raw CSV files are **not included** in this repository. Users should download the dataset separately and place it in the appropriate local data directory before running the project.
> 
