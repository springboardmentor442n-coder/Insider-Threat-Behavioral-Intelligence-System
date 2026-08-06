<div align="center">

# Insider Threat Behavioral Intelligence System

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

---

# 🏭 Data Engineering Pipeline

The project follows a structured enterprise-grade data engineering workflow before applying machine learning models.

Each dataset undergoes multiple preprocessing stages to ensure high-quality behavioral analysis.

---

## 📦 Dataset Inventory

The inventory engine automatically discovers and validates every enterprise dataset.

Features

- Dataset Discovery
- CSV Validation
- Dataset Inventory Generation
- Metadata Collection
- Missing Dataset Detection

Generated Outputs

- dataset_inventory.csv
- dataset_inventory.json
- dataset_inventory.md

---

## 📊 Dataset Profiling

Each dataset is profiled to understand its quality and statistical characteristics.

Generated Information

- Row Count
- Column Count
- Missing Values
- Duplicate Records
- Data Types
- Memory Usage
- Null Percentage
- Unique Values

Outputs

- Dataset Summary
- Profiling Report
- Statistics Report

---

## 📖 Data Dictionary

The system automatically generates documentation for every dataset.

Includes

- Column Name
- Data Type
- Description
- Nullable Status
- Sample Values

Outputs

- data_dictionary.csv
- data_dictionary.json
- data_dictionary.md

---

## 🧹 Data Cleaning

Data preprocessing includes

- Duplicate Removal
- Missing Value Handling
- Timestamp Conversion
- Invalid Record Removal
- Data Normalization
- Standardized Formatting

Supported datasets

- Device Logs
- Email Logs
- File Logs
- HTTP Logs
- Logon Logs
- Psychometric Dataset

---

## 🔗 Data Integration

Enterprise activity logs are merged into a unified behavioral timeline.

Integrated datasets

- Employees
- Email
- HTTP
- File
- Device
- Logon
- Psychometric

Result

One integrated employee behavioral dataset ready for feature engineering.

---

## ⚙ Feature Engineering

Behavioral features are extracted for every employee.

Generated Features

### User Activity

- Total Events
- Active Days
- Average Daily Activity
- Login Frequency
- Logout Frequency

### Device Behaviour

- USB Insertions
- USB Removals
- Device Events

### Email Behaviour

- Emails Sent
- Emails Received
- External Emails
- Attachment Count

### File Behaviour

- File Reads
- File Writes
- File Copies
- Sensitive File Access

### HTTP Behaviour

- Website Visits
- External Domains
- Browsing Frequency

### Time-Based Features

- Weekend Activity
- Night Activity
- After-Hours Access

### Psychometric Features

- Personality Indicators
- Behavioral Scores

A total of **22+ behavioral features** are generated for each employee.

---

# 🤖 Machine Learning Pipeline

The project implements multiple unsupervised anomaly detection models.

Instead of relying on a single model, predictions are combined using a consensus-based strategy.

---

## Implemented Models

| Model | Purpose |
|--------|----------|
| Isolation Forest | Tree-Based Anomaly Detection |
| One-Class SVM | Boundary-Based Detection |
| Local Outlier Factor | Density-Based Detection |
| Elliptic Envelope | Statistical Detection |
| PCA Reconstruction | Reconstruction Error |
| DBSCAN | Density Clustering |
| K-Means | Distance-Based Detection |

---

## Consensus Risk Scoring

Outputs from all seven models are aggregated.

Each employee receives

- Model Votes
- Consensus Percentage
- Final Risk Score
- Threat Severity
- Risk Category

Risk Categories

- 🔴 Critical
- 🟠 High
- 🟡 Medium
- 🟢 Low

---

## Model Evaluation

Performance metrics generated

- Detection Count
- Consensus Analysis
- Risk Distribution
- Feature Statistics
- Training Time
- Model Comparison

---

## Generated Reports

- Evaluation Summary
- Consensus Predictions
- Model Comparison
- Training Time Ranking
- Risk Statistics
- Employee Rankings

---

## Generated Visualizations

- Model Comparison
- Risk Distribution
- Consensus Distribution
- Training Time Analysis
- Correlation Matrix
- Employee Risk Histogram

---

# 🏗 Backend Architecture

The backend follows a modular enterprise architecture using **FastAPI**.

```
                Client
                   │
                   ▼
            FastAPI Gateway
                   │
     ┌─────────────┼──────────────┐
     ▼             ▼              ▼
 Authentication   Dashboard    Threat APIs
     │             │              │
     └─────────────┼──────────────┘
                   ▼
              CRUD Layer
                   │
                   ▼
           SQLAlchemy ORM
                   │
                   ▼
              Database
```

---

## Backend Modules

### Authentication

- JWT Login
- Password Hashing
- Role-Based Authorization
- Secure Routes

---

### Dashboard APIs

Provides

- Dashboard Summary
- Risk Statistics
- Threat Distribution
- Model Comparison
- System Statistics
- Top Suspicious Employees

---

### Threat APIs

- List Threats
- Threat Details
- Resolve Threat
- Delete Threat
- Update Threat

---

### Employee APIs

- Employee CRUD
- Employee Details
- Employee Risk Score
- Employee Activity Timeline

---

### Investigation APIs

- Activity Logs
- Email History
- HTTP Activity
- USB Events
- File Events

---

# 🌐 Frontend Architecture

The frontend is developed using **React + Vite** with a modern enterprise architecture.

```
                 React Application
                        │
         ┌──────────────┼──────────────┐
         ▼              ▼              ▼
     Dashboard      Threat Center   Employees
         │              │              │
         └──────────────┼──────────────┘
                        ▼
                 React Query
                        │
                        ▼
                     Axios
                        │
                        ▼
                  FastAPI Backend
```

---

## Frontend Modules

### Dashboard

- Hero Banner
- Metric Cards
- Threat Trends
- AI Insights
- Activity Feed
- Investigation Queue
- System Status
- Suspicious Employees

---

### Threat Center

- Threat Overview
- Search
- Filtering
- Sorting
- Threat Table
- Threat Drawer
- Resolve Dialog
- Delete Dialog

---

### Employee Module

- Employee Directory
- Employee Details
- Search
- Department Filter
- Risk Filter
- Employee Profile

---

### Investigation Module

- Timeline
- Email Activities
- HTTP Activities
- Device Activities
- Risk Timeline
- AI Recommendations

---

### Shared Components

- Glass Cards
- Animated Counters
- Sidebar
- Top Navigation
- Dialogs
- Drawers
- Status Badges
- Risk Indicators

---

# 🔌 REST API Endpoints

## Authentication

```http
POST /auth/login
POST /auth/logout
```

---

## Dashboard

```http
GET /dashboard/summary
GET /dashboard/risk-distribution
GET /dashboard/model-comparison
GET /dashboard/system-statistics
GET /dashboard/top-suspicious
```

---

## Employees

```http
GET /employees
GET /employees/{id}
POST /employees
PUT /employees/{id}
DELETE /employees/{id}
```

---

## Threats

```http
GET /threats
GET /threats/{id}
POST /threats
PUT /threats/{id}
DELETE /threats/{id}
PATCH /threats/{id}/resolve
```

---

# 🛠 Technologies Used

## Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- JWT Authentication
- Uvicorn

---

## Frontend

- React
- Vite
- Tailwind CSS
- React Router
- React Query
- Axios
- Framer Motion
- Lucide React

---

## Data Processing

- Pandas
- NumPy
- DuckDB

---

## Machine Learning

- Scikit-learn
- Joblib

---

## Visualization

- Matplotlib
- Plotly

---

# 📈 Current Results

| Metric | Value |
|---------|-------|
| Employees Processed | 1,000+ |
| Behavioral Features | 22+ |
| ML Models | 7 |
| Risk Categories | 4 |
| Backend APIs | 15+ |
| React Pages | 8 |
| Dashboard Widgets | 10+ |
| Threat Management | Complete |
| Authentication | Complete |
| UI Theme | Enterprise Glassmorphism |

---

# 🎨 Enterprise User Interface

The application is designed with an enterprise-grade cybersecurity theme inspired by modern Security Operations Center (SOC) dashboards.

The frontend emphasizes usability, clarity, and rapid threat investigation through an intuitive interface powered by React, Tailwind CSS, and Framer Motion.

---

## ✨ UI Highlights

- Enterprise Cyber Security Theme
- Glassmorphism Design
- Responsive Layout
- Animated Background
- Neon Glow Effects
- Framer Motion Animations
- Modern Sidebar Navigation
- Interactive Data Tables
- Animated Metric Cards
- Responsive Drawers
- Animated Dialogs
- Loading Animations
- Smooth Page Transitions

---

## 🌌 Glassmorphism Design

The UI adopts a modern glassmorphism approach using

- Frosted Glass Cards
- Transparent Panels
- Backdrop Blur
- Soft Shadows
- Gradient Borders
- Neon Highlights

The objective is to provide a premium enterprise experience while maintaining excellent readability.

---

## 🎞 Animations

Implemented using **Framer Motion**

Features include

- Page Transitions
- Card Hover Effects
- Drawer Animations
- Dialog Animations
- Animated Counters
- Interactive Hover States
- Smooth Fade Effects
- Slide Animations

---

# 📊 Enterprise Dashboard

The Dashboard provides security analysts with a centralized view of enterprise activity.

---

## Dashboard Components

### 🏠 Hero Banner

Displays

- Welcome Banner
- Security Status
- Animated Background
- Enterprise Branding

---

### 📈 Metric Cards

Interactive cards displaying

- Total Employees
- Total Threats
- High Risk Employees
- Active Alerts
- System Health

Features

- Animated Counters
- Hover Animation
- Glassmorphism Cards
- Color-coded Metrics

---

### 📉 Threat Trend Chart

Displays

- Threat Growth
- Monthly Incidents
- Trend Analysis
- Historical Activity

---

### 🤖 AI Insights Panel

Provides intelligent recommendations based on employee behavior.

Examples

- High-risk employee notifications
- Suspicious activity summaries
- AI-generated investigation suggestions

---

### 📋 Activity Feed

Displays recent enterprise events including

- Employee Activity
- Threat Detection
- Login Events
- File Activities
- Device Activities

---

### 🔍 Investigation Queue

Shows

- Pending Investigations
- Critical Cases
- High Priority Alerts

---

### 👥 Top Suspicious Employees

Displays

- Employee Name
- Department
- Role
- Risk Score
- Threat Severity

Integrated directly with backend APIs.

---

### 🖥 System Status

Displays

- API Status
- Database Status
- ML Engine Status
- Security Status

---

# 🛡 Threat Center

The Threat Center provides centralized threat management capabilities.

---

## Features

### Threat Overview Cards

Displays

- Total Threats
- Critical Threats
- High Threats
- Medium Threats
- Low Threats

---

### Threat Search

Search by

- Employee Name
- Department
- Threat Type

---

### Advanced Filtering

Supports filtering by

- Severity
- Status
- Department

---

### Sorting

Sort threats by

- Highest Risk
- Latest
- Oldest

---

### Threat Table

Displays

- Employee
- Department
- Threat Type
- Risk Score
- Severity
- Status
- Date

Interactive row selection opens detailed investigation.

---

### Threat Details Drawer

Provides detailed information including

- Employee Information
- Department
- Risk Score
- Threat Severity
- Threat Description
- Evidence
- Triggered ML Models
- Investigation Timestamp

---

### Threat Resolution

Security analysts can

- Resolve Threat
- Delete Threat
- Update Investigation Status

All operations communicate directly with backend APIs.

---

# 👨‍💼 Employee Management

The Employee Management module enables analysts to inspect employee information and behavioral risk.

Features

- Employee Directory
- Employee Search
- Department Filter
- Risk Filter
- Employee Profile
- Activity Summary
- Risk Summary
- Timeline
- CRUD Operations

---

# 🔍 Investigation Module

The Investigation module consolidates employee activity into a single investigative view.

Current Features

- Employee Summary
- Risk Timeline
- Email Activity
- HTTP Activity
- File Activity
- USB Activity
- AI Recommendations
- Behavioral Timeline

Designed for security analysts performing insider threat investigations.

---

# 📈 Analytics Module

The Analytics dashboard provides organization-wide security insights.

Planned Visualizations

- Risk Distribution
- Department Comparison
- Employee Ranking
- Threat Timeline
- Model Comparison
- Trend Analysis
- Monthly Reports
- Detection Statistics

---

# 📑 Reports Module

The reporting module enables exporting enterprise reports.

Supported Exports

- CSV
- PDF

Available Reports

- Employee Report
- Threat Report
- Risk Report
- Investigation Report
- Security Summary

---

# ⚙ Settings Module

Provides application configuration options.

Planned Features

- User Profile
- Password Management
- Theme Selection
- Notification Preferences
- API Configuration
- Security Settings

---

# 🤖 Artificial Intelligence Features

Implemented AI capabilities include

- Behavioral Analytics
- Risk Prediction
- Threat Detection
- Employee Ranking
- Consensus Risk Scoring
- AI Recommendations

Planned AI Enhancements

- Explainable AI (SHAP)
- Explainable AI (LIME)
- AI Copilot
- Natural Language Investigation Assistant

---

# 🎯 User Experience

The application focuses on providing an intuitive analyst experience.

Implemented improvements

- Responsive Layout
- Smooth Navigation
- Animated Components
- Professional Typography
- Accessible Color Palette
- Consistent Design Language
- Mobile Compatibility
- Enterprise Visual Identity

---

# 🔒 Security Features

- JWT Authentication
- Protected Routes
- Role-Based Access Control
- Secure REST APIs
- Input Validation
- API Authorization
- Secure Password Handling
- Backend Authentication Middleware
