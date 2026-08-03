# Insider Threat Behavioral Intelligence System

An AI-powered **Insider Threat Detection System** that leverages behavioral analytics and multiple unsupervised machine learning models to identify potentially malicious insider activities using the **CERT Insider Threat Dataset (R4.2)**.

The project performs **end-to-end data engineering, feature engineering, anomaly detection, model evaluation, employee risk scoring, backend API development, and an interactive React dashboard** to generate actionable security intelligence.

---

# Project Status

**Current Progress:** **~70%**

## ✅ Completed

### Data Engineering
- Dataset Inventory
- Dataset Profiling
- Data Dictionary Generation
- Data Cleaning
- Data Integration
- Feature Engineering

### Machine Learning
- Multi-Model Training
- Model Evaluation
- Consensus Risk Scoring
- Employee Risk Scoring

### Backend
- FastAPI Backend
- JWT Authentication
- Employee CRUD APIs
- Dashboard APIs
- Employee Activity APIs

### Frontend
- React + Vite Dashboard
- Employee Management Module
- Search & Filtering
- Employee Profile Drawer
- Employee Activity Timeline
- Risk Summary Cards
- CSV Export
- React Query Integration
- Responsive UI

---

## 🚧 In Progress

- Threat Center
- Analytics Module
- Reports Module
- Settings Module

---

## 📌 Planned

- Explainable AI (XAI)
- Automated Alert System
- Real-Time Prediction
- Docker Deployment
- Cloud Deployment

---

# Project Workflow

```text
CERT Insider Threat Dataset
            │
            ▼
Dataset Inventory
            │
            ▼
Dataset Profiling
            │
            ▼
Data Dictionary
            │
            ▼
Data Cleaning
            │
            ▼
Data Integration
            │
            ▼
Feature Engineering
            │
            ▼
Machine Learning Models
            │
            ▼
Consensus Risk Scoring
            │
            ▼
Employee Risk Database
            │
            ▼
FastAPI Backend
            │
            ▼
React Dashboard
            │
            ▼
Behavioral Intelligence Platform
```

---

# Project Structure

```text
Insider-Threat-Behavioral-Intelligence-System/

│
├── ai_engine/
├── backend/
│   ├── api/
│   ├── core/
│   ├── database/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   └── app.py
│
├── insider-threat-frontend/
│   ├── src/
│   ├── public/
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   └── services/
│
├── datasets/
├── models/
├── reports/
├── plots/
├── scripts/
│   ├── data_engineering/
│   └── utilities/
│
├── notebooks/
├── deployment/
├── tests/
├── README.md
├── requirements.txt
└── LICENSE
```

---

# Dataset

This project utilizes the **CERT Insider Threat Dataset (R4.2)** containing enterprise behavioral logs such as:

- Employee Logon Records
- Device Usage
- Email Communications
- HTTP Browsing Activity
- File Access Events
- Psychometric Data
- Employee Information

---

# Data Engineering Pipeline

The raw enterprise datasets undergo multiple preprocessing stages before machine learning.

### Dataset Inventory

- Dataset discovery
- File validation
- Dataset inventory generation

### Dataset Profiling

- Missing value analysis
- Duplicate detection
- Statistical profiling
- Data quality assessment

### Data Dictionary

- Metadata generation
- Schema documentation
- Column descriptions

### Data Cleaning

- Missing value handling
- Duplicate removal
- Timestamp standardization
- Data normalization

### Data Integration

Multiple enterprise logs are merged into a unified employee activity timeline.

### Feature Engineering

Behavioral features extracted include:

- Total Events
- Active Days
- Device Activity
- Web Activity
- Email Activity
- File Activity
- Weekend Activity
- After-Hours Activity
- Psychometric Features

A total of **22 behavioral features** are generated for every employee.

---

# Machine Learning Pipeline

The system implements **seven unsupervised anomaly detection models**.

| Model | Purpose |
|--------|----------|
| Isolation Forest | Tree-based anomaly detection |
| One-Class SVM | Boundary-based anomaly detection |
| Local Outlier Factor (LOF) | Density-based anomaly detection |
| Elliptic Envelope | Statistical anomaly detection |
| PCA Reconstruction | Reconstruction-based anomaly detection |
| DBSCAN | Density clustering |
| K-Means | Distance-based anomaly detection |

Predictions from all seven models are aggregated using a **consensus-based scoring strategy** to generate the final employee risk score.

---

# Model Evaluation

The trained models are evaluated using:

- Model Comparison
- Training Time Analysis
- Detection Comparison
- Consensus Analysis
- Risk Distribution
- Feature Statistics

Generated reports include:

- Evaluation Summary
- Model Comparison
- Training Time Ranking
- Consensus Predictions
- Model Statistics
- Top Suspicious Employees

Generated visualizations include:

- Model Detection Comparison
- Training Time Comparison
- Consensus Distribution
- Risk Score Distribution
- Feature Correlation Matrix

---

# Employee Risk Scoring

Employees are categorized into four risk levels:

- Critical
- High
- Medium
- Low

Generated outputs include:

- Employee Risk Report
- Dashboard Dataset
- Top 100 High-Risk Employees
- Critical Employee Report

---

# Backend APIs

The backend is built using **FastAPI** and exposes secure REST APIs.

## Authentication

- JWT Login
- Role-Based Authorization

## Employee APIs

- Get Employees
- Get Employee Details
- Create Employee
- Update Employee
- Delete Employee

## Dashboard APIs

- Dashboard Summary
- Risk Distribution
- Top Suspicious Employees

## Activity APIs

- Employee Activity Timeline

---

# Frontend

The frontend is developed using **React**, **Vite**, **Tailwind CSS**, **React Query**, and **Axios**.

Implemented features include:

- Interactive Dashboard
- Employee Management
- Search Employees
- Department Filter
- Risk Filter
- Employee Profile Drawer
- Activity Timeline
- Risk Summary Cards
- CSV Export
- Responsive Design
- Protected Routes

---

# Current Results

| Metric | Value |
|---------|------:|
| Employees Processed | 1,000 |
| Behavioral Features | 22 |
| Machine Learning Models | 7 |
| Risk Categories | 4 |
| Backend APIs | 10+ |
| Employee CRUD | Complete |
| Frontend Framework | React + Vite |

---

# Technologies Used

## Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- JWT Authentication

## Frontend

- React
- Vite
- Tailwind CSS
- React Query
- Axios
- Framer Motion
- Lucide React

## Data Processing

- Pandas
- NumPy
- DuckDB

## Machine Learning

- Scikit-learn
- Joblib

## Visualization

- Matplotlib

---

# Generated Outputs

## Models

- Isolation Forest
- One-Class SVM
- Local Outlier Factor
- Elliptic Envelope
- PCA
- DBSCAN
- K-Means
- Standard Scaler

## Reports

- Evaluation Summary
- Model Comparison
- Model Statistics
- Consensus Predictions
- Training Time Ranking
- Top Suspicious Employees

## Visualizations

- Model Detection Comparison
- Training Time Comparison
- Consensus Distribution
- Risk Score Distribution
- Feature Correlation Matrix

---

# Future Enhancements

- Explainable AI (SHAP/LIME)
- Threat Center
- Advanced Analytics
- Automated Alert System
- Email Notifications
- Real-Time Prediction
- Docker Deployment
- Kubernetes Deployment
- Cloud Deployment
- SIEM Integration

---

# Contributors

Springboard Mentor Program

## Contributor

- **Nandan Kabra**

---

# License

This project is licensed under the **MIT License**.
