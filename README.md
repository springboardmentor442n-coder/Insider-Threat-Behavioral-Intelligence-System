Yes. You want **one single copyable block containing the entire README**, with no separate explanations around it.

Copy everything below and paste it directly into your GitHub `README.md`:

````markdown
# 🛡️ Insider Threat Behavioral Intelligence System

## AI-Powered Insider Threat Detection and Behavioral Intelligence Platform

The **Insider Threat Behavioral Intelligence System** is an AI/ML-powered cybersecurity platform designed to analyze employee activities, identify suspicious behavioral patterns, calculate risk scores, detect potential insider threats, and provide security analysts with an integrated threat monitoring and investigation interface.

The system uses the **CERT Insider Threat Dataset r4.2** and analyzes multiple activity sources including:

- Logon
- Device
- File
- Email
- HTTP
- LDAP

The project combines Machine Learning, behavioral analytics, risk scoring, threat detection, employee monitoring, alerts, investigation, and reporting into a single cybersecurity application.

---

# 🚀 Project Overview

The system follows an end-to-end insider threat detection workflow:

```text
CERT Activity Logs
        ↓
Data Preprocessing
        ↓
Exploratory Data Analysis
        ↓
Behavioral Feature Engineering
        ↓
Daily User Behavioral Dataset
        ↓
Behavioral Risk Scoring
        ↓
Risk Label Generation
        ↓
Machine Learning Detection
        ↓
Prediction Probability
        ↓
ML Risk Score
        ↓
Final Risk Score
        ↓
Severity Classification
        ↓
Security Dashboard
        ↓
Threat Alerts
        ↓
Investigation
        ↓
Reports
````

The system provides:

* 🤖 Machine Learning-based threat detection
* 📊 Behavioral feature analysis
* ⚖️ Behavioral risk scoring
* 🚨 Risk severity classification
* 👤 Employee behavioral monitoring
* 📈 Security analytics
* 🖥️ Professional cybersecurity dashboard
* 📤 Data upload and analysis
* 🔍 Threat investigation
* 🔔 Alert management
* 📄 Security reporting

---

# 🎯 Project Objective

The main objective of this project is to develop an intelligent insider threat detection platform capable of analyzing employee behavior and identifying potentially suspicious or risky activities.

The system aims to:

* Monitor employee behavioral activities
* Analyze daily user behavior
* Identify unusual activity patterns
* Detect suspicious behavior
* Calculate behavioral risk
* Apply Machine Learning for threat prediction
* Generate prediction probabilities
* Calculate ML risk scores
* Calculate final risk scores
* Classify threat severity
* Identify high-risk users
* Provide a centralized security dashboard
* Support behavioral data upload and analysis
* Provide threat investigation capabilities
* Generate security reports

---

# 🚨 Problem Statement

Insider threats are cybersecurity incidents caused by users who already have legitimate access to an organization's systems and resources.

Unlike external attacks, insider threats can be difficult to detect because the user may be authorized to access the system.

Suspicious insider behavior may include:

* Logging in outside normal working hours
* Connecting unusual devices
* Accessing large numbers of files
* Accessing sensitive files
* Sending large numbers of external emails
* Sending emails with multiple attachments
* Performing unusual web activity
* Combining multiple suspicious activities

Manually analyzing these activities across large volumes of employee activity data is difficult.

Therefore, this project provides an intelligent behavioral analysis system that combines multiple activity sources, behavioral risk scoring, and Machine Learning to identify potentially risky insider behavior.

---

# 💡 Proposed Solution

The proposed solution processes employee activities from multiple sources and converts them into daily user-level behavioral profiles.

The system then applies behavioral risk rules and a trained Machine Learning model to identify suspicious activity.

```text
Raw Employee Activity
        ↓
Data Cleaning
        ↓
Feature Engineering
        ↓
Daily User Behavioral Profile
        ↓
Behavioral Risk Score
        ↓
Machine Learning Prediction
        ↓
Prediction Probability
        ↓
ML Risk Score
        ↓
Final Risk Score
        ↓
Severity Classification
        ↓
Threat Detection
        ↓
Security Dashboard
        ↓
Investigation & Reporting
```

---

# 📚 Dataset

The project uses the:

**CERT Insider Threat Dataset r4.2**

Major activity sources include:

* Logon
* Device
* File
* Email
* HTTP
* LDAP

The raw activity logs are transformed into daily behavioral records using:

```text
User + Day
```

as the primary behavioral unit.

The raw CERT dataset is not included in the repository because of its large size.

---

# 🧹 Data Preprocessing

The preprocessing pipeline includes:

* Dataset loading
* Dataset structure analysis
* Column analysis
* Data type analysis
* Missing-value analysis
* Duplicate analysis
* Date/time conversion
* Activity analysis
* Daily activity aggregation
* Feature engineering
* Missing-value handling

The preprocessing and behavioral feature engineering were implemented using the project notebooks.

---

# 📊 Exploratory Data Analysis

Exploratory analysis was performed to understand:

* Activity distributions
* User behavior
* Login activity
* Device activity
* File activity
* Email activity
* HTTP activity
* After-hours activity
* URL statistics
* Attachment statistics
* Missing values
* Behavioral patterns

The analysis was used to identify meaningful behavioral indicators for the Machine Learning pipeline.

---

# 🧠 Behavioral Feature Engineering

The raw activity logs were transformed into daily user-level behavioral features.

The final behavioral dataset contains:

```text
330,452 user-day records
```

The behavioral features are generated from:

```text
Logon
Device
File
Email
HTTP
```

---

# 🔐 Logon Behavioral Features

The system generates:

```text
logon_count
logoff_count
off_hours_logons
unique_pcs
```

These features help identify unusual login behavior and after-hours activity.

Current working-hour definition:

```text
08:00 - 18:00
```

---

# 💻 Device Behavioral Features

The system generates:

```text
device_connects
device_disconnects
unique_device_pcs
```

These features help identify unusual device usage patterns.

---

# 📁 File Behavioral Features

The system generates:

```text
file_activity_count
unique_file_pcs
unique_files
sensitive_file_count
```

Sensitive file extensions considered include:

```text
.doc
.docx
.pdf
.xls
.xlsx
.ppt
.pptx
.zip
.rar
.csv
```

These features help identify unusual file access and sensitive file activity.

---

# 📧 Email Behavioral Features

The system generates:

```text
email_count
attachment_count
total_email_size
unique_email_pcs
external_email_count
```

These features help analyze:

* Email volume
* Attachment activity
* Total email size
* External communication
* Email behavioral patterns

---

# 🌐 HTTP Behavioral Features

The system generates:

```text
http_request_count
unique_http_urls
off_hours_http
```

These features help identify:

* HTTP activity
* Unique URL access
* After-hours browsing
* Unusual web activity

---

# 🤖 Machine Learning

A **Gradient Boosting Classifier** has been trained using the engineered behavioral features.

The Machine Learning pipeline is:

```text
Behavioral Features
        ↓
Feature Selection
        ↓
Train / Test Split
        ↓
Feature Scaling
        ↓
Gradient Boosting Classifier
        ↓
Prediction
        ↓
Prediction Probability
        ↓
ML Risk Score
        ↓
Final Risk Score
        ↓
Severity
```

The trained model is integrated into the application for Machine Learning inference.

---

# 🎯 Machine Learning Features

The model uses 19 behavioral features:

```text
logon_count
logoff_count
off_hours_logons
unique_pcs
device_connects
device_disconnects
unique_device_pcs
file_activity_count
unique_file_pcs
unique_files
sensitive_file_count
email_count
attachment_count
total_email_size
unique_email_pcs
external_email_count
http_request_count
unique_http_urls
off_hours_http
```

---

# 📈 Model Training

The dataset was divided into training and testing datasets using an 80/20 split.

```text
Training records : 264,361
Testing records  : 66,091
```

Configuration:

```text
Test size      : 20%
Random state   : 42
Stratification : Enabled
```

Training label distribution:

```text
Normal      : 243,955
Suspicious  : 20,406
```

Testing label distribution:

```text
Normal      : 60,990
Suspicious  : 5,101
```

---

# 🎯 Risk Label Generation

The current target contains two classes:

```text
0 → Normal
1 → Suspicious
```

Current distribution:

```text
Normal      : 304,945
Suspicious  : 25,507
```

> Note: The current risk labels are generated using the project's behavioral risk-scoring methodology. Therefore, the model evaluation measures how well the Gradient Boosting model reproduces these generated labels rather than providing independent real-world ground-truth validation.

---

# 🏆 Model Performance

The trained Gradient Boosting model was evaluated using:

* Accuracy
* Precision
* Recall
* F1 Score
* Classification Report
* Feature Importance

Current test performance:

| Metric    |  Result |
| --------- | ------: |
| Accuracy  |  99.98% |
| Precision | 100.00% |
| Recall    |  99.78% |
| F1 Score  |  99.89% |

---

# 📊 Feature Importance

Feature importance analysis was performed to identify which behavioral features contributed most strongly to the trained model's predictions.

A **Top 10 Behavioral Features** visualization was generated as part of the Machine Learning analysis.

This provides insight into which behavioral characteristics have greater influence on the model's classification.

---

# ⚖️ Behavioral Risk Scoring

A rule-based behavioral risk scoring mechanism was developed using multiple suspicious activity indicators.

Current risk indicators include:

* After-hours logons
* Device connections
* Sensitive file activity
* Email attachments
* External email activity
* After-hours HTTP activity

These behavioral indicators are combined to generate a behavioral risk score.

---

# 🧮 Final Risk Scoring

The system combines behavioral risk information with Machine Learning prediction results.

The generated outputs include:

```text
risk_score
prediction
prediction_probability
ml_risk_score
behavioral_risk_score
final_risk_score
severity
```

This provides a combined view of behavioral and ML-based risk.

---

# 🚨 Severity Classification

The system classifies final risk into four severity levels:

```text
🔵 Low
🟡 Medium
🟠 High
🔴 Critical
```

Current generated distribution:

| Severity | Records |
| -------- | ------: |
| Low      | 304,945 |
| Medium   |     415 |
| High     |  19,496 |
| Critical |   5,596 |

These values are generated using the project's risk-scoring methodology.

---

# 🔍 High-Risk User-Day Detection

The system identifies user-day records with high final risk scores.

Examples observed during the completed analysis include:

```text
DLM0051
THR0873
GKO0078
JCG0316
```

These records are dynamically identified from the generated risk results and are not hardcoded into the detection logic.

---

# 💾 Trained ML Artifacts

The trained Machine Learning artifacts are stored in:

```text
ML/
└── models/
    ├── gb.pkl
    ├── scaler.pkl
    └── feature_columns.pkl
```

### gb.pkl

Contains the trained Gradient Boosting classifier.

### scaler.pkl

Contains the feature scaling configuration used by the Machine Learning pipeline.

### feature_columns.pkl

Contains the expected Machine Learning feature names and feature order.

The application loads these existing trained artifacts for prediction instead of training a new model during normal application execution.

---

# 📁 Generated Dataset Files

The project contains the generated behavioral datasets:

```text
datasets/
├── daily_behavioral_features.csv
└── final_behavioral_risk_results.csv
```

### daily_behavioral_features.csv

Contains the generated daily behavioral feature dataset.

### final_behavioral_risk_results.csv

Contains the final behavioral and Machine Learning risk analysis results.

---

# 🖥️ Application

The completed application provides a professional cybersecurity interface for monitoring, analyzing, and investigating insider threats.

The application includes:

* Login
* Security Dashboard
* Employee Monitoring
* Behavioral Analytics
* Threat Detection
* Threat Center
* Data Upload
* ML Analysis
* Alerts
* Investigation
* Reports
* Application Settings

The application uses the actual trained Machine Learning artifacts and behavioral datasets rather than random or placeholder threat values.

---

# 🔐 Login

The application provides a dedicated authentication interface.

Workflow:

```text
User
 ↓
Login
 ↓
Authentication
 ↓
Security Dashboard
```

The authentication layer provides controlled access to the security application.

---

# 📊 Security Dashboard

The Security Dashboard provides a centralized overview of insider threat activity.

The dashboard includes:

* Total users
* Monitored users
* High-risk users
* Critical alerts
* Suspicious activities
* Average risk score
* Risk trends
* Severity distribution
* Behavioral statistics
* Threat statistics

The dashboard provides security analysts with a quick overview of the current threat environment.

---

# 👤 Employee Monitoring

The Employee Monitoring module provides a user-level view of behavioral risk.

Information includes:

```text
User ID
Risk Score
Prediction
Prediction Probability
Severity
Activity History
```

Analysts can search, filter, and review employee records based on their behavioral risk.

---

# 🧠 Behavioral Analytics

The application provides behavioral analytics across:

```text
Logon
Device
File
Email
HTTP
```

The analytics allow security analysts to understand employee activity patterns and identify unusual behavior.

---

# 🚨 Threat Detection

The Threat Detection module displays:

* Machine Learning prediction
* Prediction probability
* Behavioral risk score
* ML risk score
* Final risk score
* Severity
* Behavioral indicators
* High-risk user-days

This allows security analysts to identify and prioritize potentially risky behavior.

---

# 🔔 Threat Alerts

The application provides centralized threat alert management.

Alerts can be categorized into:

```text
Critical
High
Medium
Low
```

Alert information includes relevant user and risk information to help analysts prioritize investigations.

---

# 🔍 Investigation

The Investigation module provides a structured workflow for analyzing suspicious users.

Workflow:

```text
Select High-Risk User
        ↓
Review Behavioral Evidence
        ↓
Review ML Prediction
        ↓
Review Prediction Probability
        ↓
Review Risk Score
        ↓
Review Severity
        ↓
Investigate Activity
        ↓
Update Investigation
```

The investigation workflow helps security analysts move from threat detection to detailed analysis.

---

# 📤 Data Upload and Analysis

The application supports data upload for behavioral analysis.

The workflow is:

```text
Upload Data
     ↓
Validate Data
     ↓
Process Features
     ↓
Load Trained Model
     ↓
Run Prediction
     ↓
Generate Prediction Probability
     ↓
Calculate ML Risk Score
     ↓
Calculate Behavioral Risk Score
     ↓
Calculate Final Risk Score
     ↓
Classify Severity
     ↓
Display Results
```

The application uses the already-trained Machine Learning model rather than generating random predictions.

---

# 🤖 ML Model Integration

The application loads:

```text
gb.pkl
scaler.pkl
feature_columns.pkl
```

The Machine Learning inference pipeline is:

```text
Input Data
    ↓
Feature Validation
    ↓
Feature Selection
    ↓
Feature Ordering
    ↓
Feature Scaling
    ↓
Gradient Boosting Model
    ↓
Prediction
    ↓
Prediction Probability
    ↓
ML Risk Score
    ↓
Behavioral Risk Score
    ↓
Final Risk Score
    ↓
Severity
```

This allows the application to perform inference using the trained model.

---

# 📄 Reports

The application provides reporting functionality for security analysis.

Reports can include:

* Risk summary
* User risk information
* Behavioral activity
* Threat detection results
* Alert information
* Investigation information
* Risk analysis results

---

# 🏗️ System Architecture

```text
                    👤 Security Analyst
                           │
                           ▼
                ┌───────────────────────┐
                │      Frontend         │
                │   Security Console    │
                │                       │
                │ Dashboard             │
                │ Employee Monitoring   │
                │ Threat Center         │
                │ Analytics             │
                │ Upload & Analysis     │
                │ Alerts                │
                │ Investigation         │
                │ Reports               │
                └───────────┬───────────┘
                            │
                         REST API
                            │
                            ▼
                ┌───────────────────────┐
                │       Backend         │
                │                       │
                │ Authentication        │
                │ Business Logic        │
                │ Data Processing       │
                │ Risk Analysis         │
                │ ML Inference          │
                └───────────┬───────────┘
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
        ┌─────────┐    ┌──────────┐   ┌──────────┐
        │Database │    │ML Model  │   │ Datasets │
        └─────────┘    └────┬─────┘   └──────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │   gb.pkl     │
                    │ scaler.pkl   │
                    │feature_cols  │
                    └──────────────┘
```

---

# 🔄 Complete Application Workflow

```text
                         LOGIN
                           │
                           ▼
                      DASHBOARD
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
      Existing Data   Employee Analysis   Upload Data
          │                │                │
          │                │                ▼
          │                │          Data Validation
          │                │                │
          │                │                ▼
          │                │        Feature Processing
          │                │                │
          └────────────────┼────────────────┘
                           │
                           ▼
                    ML MODEL INFERENCE
                           │
                           ▼
                       Prediction
                           │
                           ▼
                 Prediction Probability
                           │
                           ▼
                     Risk Analysis
                           │
                           ▼
                 Severity Classification
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
           Alerts     Investigation   Reports
```

---

# 🧰 Technology Stack

## Machine Learning

```text
Python
Pandas
NumPy
Scikit-learn
Matplotlib
```

## Machine Learning Algorithm

```text
Gradient Boosting Classifier
```

## Frontend

```text
React
TypeScript
Vite
Tailwind CSS
Lucide React
Recharts
```

## Backend

```text
Python
REST API
```

## Database

```text
SQLite
```

## Development Tools

```text
Kaggle
VS Code
Git
GitHub
```

---

# 📁 Project Structure

```text
Insider-Threat-Behavioral-Intelligence-System/
│
├── backend/
│   ├── app/
│   ├── main.py
│   └── ...
│
├── frontend/
│   ├── src/
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
├── datasets/
│   ├── daily_behavioral_features.csv
│   ├── final_behavioral_risk_results.csv
│   └── .gitkeep
│
├── ML/
│   └── models/
│       ├── gb.pkl
│       ├── scaler.pkl
│       └── feature_columns.pkl
│
├── notebooks/
│   ├── 01_Data_Preprocessing.ipynb
│   ├── 02-model-training-and-detection.ipynb
│   └── ...
│
├── scripts/
│
├── tests/
│
├── README.md
└── .gitignore
```

---

# 📊 Project Statistics

The completed Machine Learning and behavioral analysis pipeline produced:

```text
330,452
User-Day Behavioral Records
```

Machine Learning:

```text
19
Behavioral Features
```

Training dataset:

```text
264,361 records
```

Testing dataset:

```text
66,091 records
```

Risk labels:

```text
Normal      : 304,945
Suspicious  : 25,507
```

---

# 🏆 Final Machine Learning Results

```text
Accuracy  : 99.98%
Precision : 100.00%
Recall    : 99.78%
F1 Score  : 99.89%
```

Severity distribution:

```text
Low       : 304,945
Medium    : 415
High      : 19,496
Critical  : 5,596
```

---

# 🧪 Testing

The completed project includes testing and validation of the major components.

Testing areas include:

```text
Data Processing
Feature Engineering
Model Loading
Model Prediction
Risk Calculation
CSV Processing
Backend APIs
Frontend Components
Application Integration
```

The Machine Learning model was evaluated using the held-out testing dataset.

---

# 🔐 Security Considerations

The system focuses on behavioral security analytics and insider threat detection.

Important security considerations include:

* User authentication
* Access control
* Secure password handling
* API validation
* File upload validation
* CSV validation
* Database protection
* ML model protection
* Error handling
* Secure configuration
* Audit information
* Risk-based threat prioritization

This project is developed as an academic/research implementation and should undergo additional security hardening and validation before production deployment.

---

# 🎯 Project Objectives Achieved

The project successfully implements:

* Employee behavioral monitoring
* Multi-source activity analysis
* Daily behavioral profiling
* Suspicious behavior identification
* Behavioral risk scoring
* Machine Learning-based threat detection
* Prediction probability analysis
* ML risk scoring
* Final risk scoring
* Threat severity classification
* High-risk user identification
* Security dashboard
* Employee monitoring
* Threat alerts
* Investigation workflow
* Data upload and analysis
* Security reporting
* Full application integration

---

# 🌟 Advantages

* AI-assisted insider threat detection
* Multi-source behavioral analysis
* Behavioral risk scoring
* Machine Learning-based classification
* Prediction probability analysis
* Final risk scoring
* Threat severity classification
* High-risk user identification
* Professional security dashboard
* Employee behavioral monitoring
* Data upload and analysis
* Threat alerts
* Investigation workflow
* Security reporting
* Integrated ML inference
* Modular application architecture

---

# 🗺️ Development Status

## Phase 1 — Data Preparation

**Status: ✅ Completed**

* Dataset loading
* Dataset analysis
* Data preprocessing
* Missing-value analysis
* Duplicate analysis
* Exploratory analysis

## Phase 2 — Behavioral Feature Engineering

**Status: ✅ Completed**

* Logon features
* Device features
* File features
* Email features
* HTTP features
* Daily user-level aggregation

## Phase 3 — Machine Learning & Risk Scoring

**Status: ✅ Completed**

* Risk label generation
* ML feature preparation
* Train/test split
* Gradient Boosting training
* Prediction
* Prediction probability
* Model evaluation
* Feature importance
* Behavioral risk score
* ML risk score
* Final risk score
* Severity classification

## Phase 4 — Frontend Application

**Status: ✅ Completed**

* Login
* Security Dashboard
* Employee Monitoring
* Behavioral Analytics
* Threat Detection
* Threat Center
* Data Upload
* Alerts
* Investigation
* Reports
* Application navigation
* Security-focused UI

## Phase 5 — Backend Application

**Status: ✅ Completed**

* Backend architecture
* REST APIs
* Application logic
* Data processing
* Risk analysis
* ML inference
* Database connectivity
* Application services

## Phase 6 — ML Integration

**Status: ✅ Completed**

* Trained model loading
* Scaler loading
* Feature configuration loading
* Prediction pipeline
* Prediction probability
* ML risk score
* Behavioral risk score
* Final risk score
* Severity classification

## Phase 7 — Full Application Integration

**Status: ✅ Completed**

```text
React Frontend
      ↕
Backend API
      ↕
Database
      ↕
ML Model
      ↕
Behavioral Data
```

## Phase 8 — Testing

**Status: ✅ Completed**

* ML testing
* Data processing testing
* Backend testing
* Frontend testing
* Integration testing
* Prediction validation

---

# 🔮 Future Enhancements

Future versions can include:

* Real-time activity monitoring
* Advanced anomaly detection
* User behavioral baselines
* Temporal behavioral analysis
* Explainable AI
* SHAP-based model explanations
* Automated investigation recommendations
* Advanced role-based access control
* Automated incident response
* Email notifications
* SIEM integration
* Cloud deployment
* Docker deployment
* Model monitoring
* Automated model retraining
* Real-time streaming activity analysis

---

# 🏁 Conclusion

The **Insider Threat Behavioral Intelligence System** provides an end-to-end platform for detecting and analyzing potentially suspicious insider behavior.

The system combines:

```text
Behavioral Analytics
        +
Rule-Based Risk Scoring
        +
Machine Learning
        +
Prediction Probability
        +
ML Risk Scoring
        +
Final Risk Scoring
        +
Severity Classification
        +
Security Dashboard
        +
Threat Alerts
        +
Investigation
        +
Reporting
```

The system processes employee activities from multiple sources, creates daily behavioral profiles, identifies suspicious patterns, and applies a trained Gradient Boosting model to classify potential insider threats.

The completed application provides security analysts with a centralized platform to:

* Monitor employee behavior
* Identify high-risk users
* Analyze suspicious activity
* Upload behavioral data
* Run Machine Learning predictions
* Review risk scores
* Monitor alerts
* Investigate threats
* Generate reports

---

# 🏆 Final Project Status

```text
┌───────────────────────────────────────────────┐
│     INSIDER THREAT BEHAVIORAL INTELLIGENCE    │
│                   SYSTEM                      │
├───────────────────────────────────────────────┤
│                                               │
│ Data Processing              ✅ COMPLETED     │
│ Feature Engineering          ✅ COMPLETED     │
│ Risk Scoring                 ✅ COMPLETED     │
│ ML Training                  ✅ COMPLETED     │
│ Model Evaluation             ✅ COMPLETED     │
│ Model Artifacts              ✅ COMPLETED     │
│                                               │
│ Frontend                     ✅ COMPLETED     │
│ Backend                      ✅ COMPLETED     │
│ Database                     ✅ COMPLETED     │
│ ML Integration               ✅ COMPLETED     │
│ Dashboard                    ✅ COMPLETED     │
│ Threat Center                ✅ COMPLETED     │
│ Employee Monitoring          ✅ COMPLETED     │
│ Behavioral Analytics         ✅ COMPLETED     │
│ Data Upload & Analysis       ✅ COMPLETED     │
│ Alerts                       ✅ COMPLETED     │
│ Investigation                ✅ COMPLETED     │
│ Reports                      ✅ COMPLETED     │
│ Full Integration             ✅ COMPLETED     │
│ Testing                      ✅ COMPLETED     │
│                                               │
│              PROJECT COMPLETED                │
└───────────────────────────────────────────────┘
```

---

# 🙌 Acknowledgements

* CERT Insider Threat Dataset
* Kaggle
* Python
* Pandas
* NumPy
* Scikit-learn
* Matplotlib
* React
* TypeScript
* Vite
* Tailwind CSS
* Recharts
* Lucide React
* Open-source cybersecurity and Machine Learning community

---

# 📜 License

This project is developed for educational and research purposes as part of an Insider Threat Behavioral Intelligence project.

```
```
