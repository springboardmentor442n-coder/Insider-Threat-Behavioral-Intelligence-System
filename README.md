# AI Insider Threat Behavioral Intelligence System

## Project Overview

The AI Insider Threat Behavioral Intelligence System is a full-stack cybersecurity application that detects potential insider threats using employee behavioral analytics and machine learning.

The system monitors employee activities such as login frequency, device usage, working hours, and weekend access to identify abnormal behavior that may indicate malicious insider activity.

---

# Objectives

- Detect insider threats using Machine Learning.
- Build employee behavioral profiles.
- Identify anomalous user activities.
- Generate threat predictions.
- Visualize organizational security metrics.
- Maintain prediction history for audit purposes.

---

# Features

## Authentication
- Secure Login
- JWT Authentication
- Role-based Access

## Employee Management
- Add Employees
- View Employees
- Update Employee Details
- Delete Employees

## Threat Prediction
- Predict Insider Threat Risk
- Machine Learning Model
- Confidence Score
- Risk Classification (LOW / HIGH)

## Dashboard
- Total Employees
- Total Predictions
- High Risk Employees
- Low Risk Employees
- Security Statistics

## Prediction History
- Stores every prediction
- Displays previous predictions
- Database integration

---

# Technology Stack

## Frontend
- React
- Vite
- Axios
- React Router

## Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic

## Machine Learning
- Scikit-learn
- Random Forest Classifier
- Pandas
- Joblib

---

# Project Structure

```
AI-Insider-Threat-Behavioral-Intelligence-System

backend/
    routes/
    config.py
    crud.py
    database.py
    models.py
    schemas.py
    security.py
    main.py

frontend/
    src/
    package.json

ml/
    models/
    train_model.py
    predict.py

dataset/
    raw/
    processed/

README.md
```

---

# Machine Learning Workflow

Raw Dataset

↓

Feature Engineering

↓

Behavior Profiling

↓

Random Forest Model

↓

Threat Prediction

↓

Store Prediction

↓

Dashboard Visualization

---

# Prediction Inputs

- Employee ID
- Login Count
- Unique PC Count
- Hour
- Weekend Activity

---

# Prediction Output

- Risk Level
- Confidence Score
- Prediction History

---

# Current Milestone Status

## Milestone 1
- Project Setup
- Database Design
- Authentication
- Employee Management
- Prediction Module
- Frontend Integration

Status:
Completed

## Milestone 2
- Behavioral Analytics
- Threat Detection
- Prediction Reports
- Dashboard Analytics

Status:
In Progress

---

# Future Improvements

- Real-time Log Monitoring
- Email Alerts
- Risk Trend Analysis
- Admin Dashboard
- SIEM Integration
- Explainable AI

---

# Developed By

B.Tech CSE Internship Project

AI Insider Threat Behavioral Intelligence System