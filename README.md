# 🛡️ AI Insider Threat Behavioral Intelligence System

An Artificial Intelligence based behavioral analytics system designed to detect potential insider threats by analyzing employee activity patterns extracted from the CERT Insider Threat Dataset (Version 4.2).

The system combines Machine Learning, Behavioral Feature Engineering, FastAPI, PostgreSQL, and React to identify employees exhibiting suspicious behavior and present risk insights through an interactive dashboard.

---

# 📖 Project Overview

Insider threats pose significant cybersecurity risks because malicious or negligent employees already have authorized access to organizational resources.

This project analyzes employee behavior across multiple enterprise activities and predicts whether an employee represents a potential insider threat.

The system performs:

- Behavioral Feature Engineering
- Dynamic Risk Score Generation
- Machine Learning Classification
- Prediction Confidence Calculation
- Explainable Risk Analysis
- Interactive Dashboard Visualization

---

# 🚀 Features

### Machine Learning

- Behavioral feature extraction
- Dynamic risk threshold calculation
- Risk score generation
- Random Forest based classification
- Prediction confidence using probabilities
- Feature importance analysis

### Behavioral Analysis

Employee behavior is analyzed using:

- Login Activity
- HTTP Browsing Activity
- Email Communication
- File Access Activity
- Device Usage Activity

### Backend

- FastAPI REST APIs
- PostgreSQL database
- Automated prediction pipeline
- Model loading using Joblib

### Frontend

- Secure Login
- Executive Dashboard
- Employee Risk Analysis
- Threat Predictions
- Analytics Dashboard
- Pipeline Status Monitoring

---

# 🏗️ System Architecture

```

                CERT Dataset
                      │
                      ▼
          Data Preprocessing Pipeline
                      │
                      ▼
          Behavioral Feature Engineering
                      │
                      ▼
            behavior_features.csv
                      │
                      ▼
           Random Forest Training
                      │
                      ▼
          Trained ML Model (.pkl)
                      │
                      ▼
            Prediction Pipeline
                      │
                      ▼
              PostgreSQL Database
                      │
                      ▼
                FastAPI Backend
                      │
                      ▼
               React Dashboard

```

---

# 🗂️ Project Structure

```

AI-Insider-Threat-System/

│

├── backend/
│   ├── api/
│   ├── database/
│   ├── models/
│   ├── services/
│   ├── pipeline/
│   ├── model/
│   └── main.py
│
├── frontend/
│   ├── src/
│   ├── pages/
│   ├── components/
│   └── assets/
│
├── dataset/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│
├── model/
│   ├── random_forest_model.pkl
│   ├── feature_columns.pkl
│   ├── feature_importance.csv
│   ├── training_metrics.csv
│   └── confusion_matrix.csv
│
├── README.md
└── requirements.txt

```

---

# 📊 Dataset

**Dataset Used**

CERT Insider Threat Dataset Version 4.2

The dataset contains simulated enterprise activity logs including:

- Logon Records
- HTTP Activity
- Email Records
- File Access Logs
- Device Logs
- LDAP Employee Information

These logs are transformed into behavioral features for machine learning.

---

# ⚙️ Behavioral Feature Engineering

Behavioral features are extracted from multiple employee activities.

### Login Features

- Login Count
- Weekend Logins
- After-hours Logins
- Unique PCs

### HTTP Features

- Website Visits
- Unique Websites
- Weekend HTTP Activity
- After-hours HTTP Activity

### Email Features

- Emails Sent
- External Emails
- After-hours Emails

### File Features

- File Access Count
- Unique Files
- Weekend File Access

### Device Features

- Device Usage Count
- Connect Events
- Disconnect Events
- Weekend Device Usage

---

# 🧠 Machine Learning Model

Algorithm Used:

**Random Forest Classifier**

### Why Random Forest?

- Handles structured tabular data effectively
- Reduces overfitting
- High classification performance
- Provides feature importance
- Supports prediction probabilities
- Robust against noisy data

---

# 🎯 Risk Label Generation

The CERT dataset does not contain predefined insider threat labels for this implementation.

Risk labels are generated using behavioral indicators such as:

- Excessive after-hours logins
- Frequent weekend logins
- High HTTP activity
- External email communication
- High device usage
- Excessive file access

Employees exceeding the defined behavioral threshold are labeled as:

- **Low Risk (0)**
- **High Risk (1)**

---

# 📈 Machine Learning Workflow

1. Load Behavioral Dataset
2. Handle Missing Values
3. Calculate Dynamic Thresholds
4. Generate Risk Score
5. Create Target Labels
6. Select Behavioral Features
7. Split Dataset
8. Train Random Forest Model
9. Generate Predictions
10. Calculate Confidence Scores
11. Evaluate Model
12. Save Trained Model

---

# 📊 Model Evaluation

The trained model is evaluated using:

- Accuracy
- Precision
- Recall
- F1-Score
- Classification Report
- Confusion Matrix
- Feature Importance

---

# 💻 Technologies Used

### Frontend

- React
- Vite
- Tailwind CSS
- Framer Motion

### Backend

- FastAPI
- Python

### Machine Learning

- Scikit-learn
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Joblib

### Database

- PostgreSQL

### Development Tools

- VS Code
- Git
- GitHub

---

# ⚡ Installation

## Clone Repository

```bash
git clone <repository-url>

cd AI-Insider-Threat-System
```

---

## Create Virtual Environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Database

Update the PostgreSQL connection settings in the backend configuration.

---

## Train the Model

```bash
python train_model.py
```

---

## Run Prediction Pipeline

```bash
python prediction_pipeline.py
```

---

## Start Backend

```bash
uvicorn main:app --reload
```

---

## Start Frontend

```bash
npm install

npm run dev
```

---

# 🌐 API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | /login | User Authentication |
| GET | /dashboard | Dashboard Summary |
| GET | /employees | Employee Information |
| GET | /predictions | Prediction Results |
| GET | /analytics | Analytics Data |
| GET | /pipeline | Pipeline Status |

---

# 📸 Dashboard Modules

The dashboard includes:

- Login Page
- Executive Dashboard
- Employee Details
- Threat Predictions
- Analytics Dashboard
- Pipeline Monitoring

---

# 🔍 Explainable AI

The prediction pipeline provides:

- Predicted Risk
- Confidence Score
- Behavioral Risk Reasons

This helps security analysts understand why an employee was classified as high risk.

---

# 🔒 Future Enhancements

Possible improvements include:

- Real-time activity monitoring
- Streaming data analysis
- Deep Learning based anomaly detection
- LSTM and Transformer models
- Graph Neural Networks
- Explainable AI visualizations
- SIEM Integration
- Continuous model retraining

---

# 🙏 Acknowledgements

- Carnegie Mellon University CERT Division
- CERT Insider Threat Dataset Version 4.2
- Scikit-learn
- FastAPI
- React
- PostgreSQL

---

# 📄 License

This project is developed for educational and research purposes.

The CERT dataset is subject to its respective licensing and usage terms.

---

# 👨‍💻 Author

Developed as part of an AI-based Insider Threat Detection project using Machine Learning and Behavioral Analytics.