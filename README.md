# Insider Threat Behavioral Intelligence System

An AI-powered Insider Threat Detection System that leverages behavioral analytics and multiple unsupervised machine learning models to identify potentially malicious insider activities using the CERT Insider Threat Dataset.

The project performs end-to-end data engineering, feature engineering, anomaly detection, model evaluation, and employee risk scoring to generate actionable security intelligence.

---

# Project Status

**Current Progress:** ~75%

## Completed

- Dataset Inventory
- Dataset Profiling
- Data Dictionary Generation
- Data Cleaning
- Data Integration
- Feature Engineering
- Multi-Model Training
- Model Evaluation
- Employee Risk Scoring

## Planned

- Explainable AI
- Interactive Dashboard
- Backend APIs
- Deployment

---

# Project Workflow

```
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
Multi-Model Training
            │
            ▼
Model Evaluation
            │
            ▼
Consensus Risk Scoring
            │
            ▼
Employee Risk Reports
```

---

# Project Structure

```
Insider-Threat-Behavioral-Intelligence-System/

│
├── datasets/
├── models/
├── plots/
├── reports/
├── scripts/
│   ├── data_engineering/
│   │   ├── 01_dataset_inventory.py
│   │   ├── 02_dataset_profiler.py
│   │   ├── 03_data_dictionary.py
│   │   ├── 04_data_cleaner.py
│   │   ├── 05_data_integrator.py
│   │   ├── 06_feature_engineering.py
│   │   ├── 07_model_training.py
│   │   ├── 08_model_evaluation.py
│   │   └── 09_risk_scoring.py
│   │
│   └── utilities/
│
├── README.md
├── requirements.txt
└── LICENSE
```

---

# Dataset

This project utilizes the **CERT Insider Threat Dataset (R4.2)**, which contains enterprise behavioral logs including:

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

A total of **22 behavioral features** are generated for each employee.

---

# Machine Learning Pipeline

The system implements seven unsupervised anomaly detection models.

| Model | Purpose |
|--------|----------|
| Isolation Forest | Tree-based anomaly detection |
| One-Class SVM | Boundary-based anomaly detection |
| Local Outlier Factor (LOF) | Density-based anomaly detection |
| Elliptic Envelope | Statistical anomaly detection |
| PCA Reconstruction | Reconstruction-based anomaly detection |
| DBSCAN | Density clustering |
| K-Means | Distance-based anomaly detection |

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

Predictions from all seven models are combined using a consensus-based approach to produce a final employee risk score.

Employees are categorized into four levels:

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

# Current Results

| Metric | Value |
|---------|------:|
| Employees Processed | 1,000 |
| Behavioral Features | 22 |
| Machine Learning Models | 7 |
| Risk Categories | 4 |

---

# Technologies Used

## Programming Language

- Python

## Data Processing

- Pandas
- NumPy
- DuckDB

## Machine Learning

- Scikit-learn

## Data Visualization

- Matplotlib

## Model Serialization

- Joblib

---

# Generated Outputs

### Models

- Isolation Forest
- One-Class SVM
- Local Outlier Factor
- Elliptic Envelope
- PCA
- DBSCAN
- K-Means
- Standard Scaler

### Reports

- Evaluation Summary
- Model Comparison
- Model Statistics
- Consensus Predictions
- Training Time Ranking
- Top Suspicious Employees

### Visualizations

- Model Detection Comparison
- Training Time Comparison
- Consensus Distribution
- Risk Score Distribution
- Feature Correlation Matrix

---

# Future Enhancements

- Explainable AI
- Interactive Dashboard
- Backend APIs
- Automated Alert System
- Real-Time Prediction
- Docker Support
- Cloud Deployment

---

# Contributors

Springboard Mentor Program

**Contributor**

- Nandan Kabra

---

# License

This project is licensed under the MIT License.
