# 🛡️ Insider Threat Behavioral Intelligence System

An AI-powered **Insider Threat Behavioral Intelligence System** designed to analyze user activities, identify suspicious behavioral patterns, calculate risk scores, and detect potentially risky insider behavior using Machine Learning.

The system uses the **CERT Insider Threat Dataset r4.2** and analyzes multiple activity sources including Logon, Device, File, Email, and HTTP activities.

The Machine Learning pipeline has been completed, including data preprocessing, behavioral feature engineering, risk scoring, Gradient Boosting model training, prediction, evaluation, and severity classification.

The frontend application is currently under development, followed by backend and database integration.

---

## 🚀 Project Overview

The proposed system follows an end-to-end insider threat detection workflow:

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
Machine Learning Detection
        ↓
Prediction Probability
        ↓
Final Risk Score
        ↓
Severity Classification
        ↓
Security Dashboard
        ↓
Alerts & Investigation
```

The project combines:

* 🤖 Machine Learning-based threat detection
* 📊 Behavioral feature analysis
* ⚖️ Behavioral risk scoring
* 🚨 Risk severity classification
* 👤 User behavioral monitoring
* 📈 Security analytics
* 🖥️ Enterprise-style security dashboard
* 🔍 Future threat investigation workflow

---

# ✨ Key Features

## 1. 📥 CERT Dataset Processing

The system processes activity information from the CERT Insider Threat Dataset r4.2.

Major activity sources include:

* Logon
* Device
* File
* Email
* HTTP
* LDAP

---

## 2. 🧹 Data Preprocessing

The preprocessing stage includes:

* Dataset loading
* Dataset structure analysis
* Column analysis
* Data type analysis
* Missing-value analysis
* Duplicate analysis
* Date/time conversion
* Activity analysis
* Daily activity aggregation

The behavioral analysis is performed using:

```text
User + Day
```

as the primary behavioral unit.

---

## 3. 📊 Exploratory Data Analysis

Exploratory analysis was performed to understand:

* Activity distributions
* User behavior
* Missing values
* Login activity
* Device activity
* File activity
* Email activity
* HTTP activity
* After-hours activity
* URL statistics
* Attachment statistics

---

# 🧠 Behavioral Feature Engineering

The raw activity logs were transformed into daily user-level behavioral features.

The final behavioral dataset contains:

```text
330,452 user-day records
```

with 21 behavioral columns before adding ML and risk-analysis outputs.

---

## 🔐 Logon Behavioral Features

The system generates:

```text
logon_count
logoff_count
off_hours_logons
unique_pcs
```

These features are used to identify unusual login behavior and after-hours activity.

Current working-hour definition:

```text
08:00 - 18:00
```

---

## 💻 Device Behavioral Features

The system generates:

```text
device_connects
device_disconnects
unique_device_pcs
```

These features help identify unusual device usage patterns.

---

## 📁 File Behavioral Features

The system generates:

```text
file_activity_count
unique_file_pcs
unique_files
sensitive_file_count
```

Sensitive file extensions currently considered include:

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

---

## 📧 Email Behavioral Features

The system generates:

```text
email_count
attachment_count
total_email_size
unique_email_pcs
external_email_count
```

These features are used to analyze email volume, attachment activity, email size, and external communication.

---

## 🌐 HTTP Behavioral Features

The system generates:

```text
http_request_count
unique_http_urls
off_hours_http
```

These features help identify unusual web activity and after-hours browsing.

---

# 🤖 Machine Learning

A **Gradient Boosting Classifier** has been trained using the engineered behavioral features.

The ML pipeline is:

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
```

---

# 🎯 Machine Learning Features

The model currently uses 19 behavioral features:

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

The dataset was divided into training and testing sets using an 80/20 split.

```text
Training records : 264,361
Testing records  : 66,091
```

Configuration:

```text
Test size     : 20%
Random state  : 42
Stratification: Enabled
```

---

# 🎯 Risk Labels

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

A Top-10 behavioral feature importance visualization was generated as part of the ML analysis.

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

The risk indicators are combined to generate a behavioral risk score.

---

# 🧮 Final Risk Scoring

The system combines behavioral risk information with the machine-learning prediction.

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

These values are generated using the current project's risk-scoring methodology.

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

These records can be prioritized for further security investigation.

---

# 💾 Trained ML Artifacts

The completed ML pipeline generated the following model artifacts:

```text
gb.pkl
scaler.pkl
feature_columns.pkl
```

### `gb.pkl`

Contains the trained Gradient Boosting classifier.

### `scaler.pkl`

Contains the feature scaling configuration used by the ML pipeline.

### `feature_columns.pkl`

Contains the feature names and expected feature order required by the model.

These artifacts will be used later during backend ML integration.

---

# 🔬 ML Detection Pipeline

The completed ML pipeline currently follows:

```text
CERT r4.2 Dataset
        ↓
Data Preprocessing
        ↓
Daily Behavioral Features
        ↓
Behavioral Risk Indicators
        ↓
Risk Label Generation
        ↓
19 ML Features
        ↓
Train/Test Split
        ↓
Gradient Boosting Training
        ↓
Model Prediction
        ↓
Prediction Probability
        ↓
ML Risk Score
        ↓
Final Risk Score
        ↓
Severity
```

---

# 🖥️ Security Console

## 🚧 Frontend Development In Progress

The frontend application is currently being developed as a professional cybersecurity security console.

The planned interface includes:

### 🔐 Authentication

* Login page
* User login interface
* Secure application entry
* User profile

### 📊 Dashboard

* Total users
* Monitored users
* High-risk users
* Critical alerts
* Suspicious activities
* Average risk score
* Risk trends
* Severity distribution

### 👤 User Monitoring

* User list
* User risk score
* User severity
* User activity
* Behavioral history
* User details

### 🧠 Behavioral Analytics

* Logon analytics
* Device analytics
* File analytics
* Email analytics
* HTTP analytics
* After-hours activity

### 🚨 Threat Detection

* ML prediction
* Prediction probability
* Risk score
* Severity
* Behavioral indicators
* Feature importance

### 🔔 Alerts

* Critical alerts
* High-risk alerts
* Medium-risk alerts
* Alert status
* User information
* Risk indicators

### 🔍 Investigations

* Investigation records
* Risk factors
* Activity timeline
* Analyst notes
* Investigation status

### 📄 Reports

* Risk reports
* User reports
* Threat reports
* Alert reports
* Behavioral analytics reports

### ⚙️ Settings

* Profile settings
* Security settings
* Notification settings
* Appearance
* Dark/light mode

---

# 🏗️ Planned System Architecture

The final application is planned to follow this architecture:

```text
                   👤 Security Analyst
                           │
                           ▼
                 ┌───────────────────┐
                 │ React Frontend    │
                 │ Security Console   │
                 └─────────┬─────────┘
                           │
                           │ REST API
                           ▼
                 ┌───────────────────┐
                 │ Backend API       │
                 │ Authentication    │
                 │ Business Logic    │
                 └─────────┬─────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
         Database      ML Service   Alert Engine
              │            │            │
              │            ▼            │
              │      Gradient Boosting  │
              │          Model           │
              │            │             │
              │            ▼             │
              │       Risk Score         │
              └────────────┼─────────────┘
                           │
                           ▼
                   Security Dashboard
```

---

# 🔄 Planned Application Workflow

```text
Login
  ↓
Security Dashboard
  ↓
User Monitoring
  ↓
Behavioral Analytics
  ↓
Risk Analysis
  ↓
Machine Learning Prediction
  ↓
Final Risk Score
  ↓
Severity Classification
  ↓
Threat Alert
  ↓
Investigation
  ↓
Report
```

---

# 🔌 Backend

## ⏳ Backend Development Pending

The backend has not yet been completed.

The planned backend will provide communication between:

```text
Frontend
    ↕
Backend API
    ↕
Database
    ↕
ML Model
```

Planned backend functionality:

* REST API
* Authentication
* User management
* Database integration
* Behavioral data APIs
* ML model loading
* Risk prediction API
* Threat detection
* Alert management
* Investigation management
* Report generation
* Frontend integration

---

# 🗄️ Database

## ⏳ Database Integration Pending

The database layer will be implemented during backend development.

Planned entities include:

* Users
* User profiles
* Behavioral records
* Risk scores
* Alerts
* Investigations
* Analyst notes
* Reports
* System settings

---

# 🔗 Planned ML Backend Integration

The trained model will later be integrated into the backend.

Planned workflow:

```text
User Activity
      ↓
Feature Extraction
      ↓
Feature Validation
      ↓
Feature Scaling
      ↓
Gradient Boosting Model
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
      ↓
Frontend Dashboard
```

The backend will load:

```text
gb.pkl
scaler.pkl
feature_columns.pkl
```

---

# 📁 Repository Structure

Current/planned project structure:

```text
Insider-Threat-Behavioral-Intelligence-System/
│
├── backend/
│
├── frontend/
│
├── docs/
│
├── ml/
│   ├── preprocessing.py
│   └── model/
│       ├── gb.pkl
│       ├── scaler.pkl
│       └── feature_columns.pkl
│
├── notebooks/
│   ├── 01_Data_Preprocessing.ipynb
│   └── 02_Model_Training_and_Detection.ipynb
│
├── README.md
└── .gitignore
```

---

# 🧰 Technology Stack

| Layer               | Technology                   |
| ------------------- | ---------------------------- |
| Programming         | Python                       |
| Data Processing     | Pandas, NumPy                |
| Machine Learning    | Scikit-learn                 |
| ML Algorithm        | Gradient Boosting Classifier |
| Visualization       | Matplotlib                   |
| Frontend            | React                        |
| Frontend Language   | TypeScript                   |
| Frontend Build Tool | Vite                         |
| UI                  | Tailwind CSS                 |
| Icons               | Lucide React                 |
| Charts              | Recharts                     |
| Development         | VS Code, Kaggle              |
| Version Control     | Git, GitHub                  |
| Backend             | Planned                      |
| Database            | Planned                      |

---

# 📊 Project Statistics

The completed preprocessing and feature engineering pipeline produced:

```text
330,452
User-Day Behavioral Records
```

Machine learning:

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

---

# 🧪 Completed Work

The following major components have been completed:

```text
✅ Dataset Loading
✅ Dataset Analysis
✅ Missing Value Analysis
✅ Duplicate Analysis
✅ Date/Time Processing
✅ Exploratory Data Analysis
✅ Daily User Aggregation
✅ Logon Feature Engineering
✅ Device Feature Engineering
✅ File Feature Engineering
✅ Email Feature Engineering
✅ HTTP Feature Engineering
✅ Behavioral Dataset Creation
✅ Behavioral Risk Scoring
✅ Risk Label Generation
✅ ML Feature Preparation
✅ Train/Test Split
✅ Gradient Boosting Model Training
✅ Model Prediction
✅ Prediction Probability
✅ Model Evaluation
✅ Feature Importance
✅ ML Risk Score
✅ Final Risk Score
✅ Severity Classification
✅ High-Risk User Detection
✅ Trained Model Artifacts
```

---

# 🚧 Work In Progress

Current development:

```text
🚧 Frontend Security Console
🚧 Login Interface
🚧 Dashboard Interface
🚧 User Monitoring Interface
🚧 Behavioral Analytics Interface
🚧 Threat Detection Interface
🚧 Alerts Interface
🚧 Investigation Interface
🚧 Reports Interface
```

---

# ⏳ Upcoming Work

The following modules are pending:

```text
⏳ Backend API
⏳ Authentication Backend
⏳ Database
⏳ ML Backend Integration
⏳ Risk Prediction API
⏳ Frontend-Backend Integration
⏳ Alert Management Backend
⏳ Investigation Backend
⏳ Report Generation
⏳ End-to-End Testing
⏳ Deployment
```

---

# 🗺️ Development Roadmap

## Phase 1 — Data Preparation

Status: ✅ Completed

* Dataset loading
* Dataset analysis
* Data preprocessing
* Missing value analysis
* Exploratory analysis

---

## Phase 2 — Behavioral Feature Engineering

Status: ✅ Completed

* Logon features
* Device features
* File features
* Email features
* HTTP features
* Daily user-level aggregation

---

## Phase 3 — Machine Learning & Risk Scoring

Status: ✅ Completed

* Risk label generation
* ML feature preparation
* Train/test split
* Gradient Boosting training
* Prediction
* Model evaluation
* Feature importance
* Behavioral risk score
* ML risk score
* Final risk score
* Severity classification

---

## Phase 4 — Frontend Development

Status: 🚧 In Progress

* Login
* Dashboard
* User monitoring
* Behavioral analytics
* Threat detection
* Alerts
* Investigations
* Reports
* Settings
* Responsive design
* Dark/light theme

---

## Phase 5 — Backend Development

Status: ⏳ Pending

* Backend architecture
* REST APIs
* Authentication
* Database
* User management
* Behavioral APIs
* Risk prediction API
* Alert APIs
* Investigation APIs

---

## Phase 6 — ML Integration

Status: ⏳ Pending

* Load trained model
* Load scaler
* Load feature columns
* Create prediction API
* Connect behavioral data
* Generate predictions
* Generate final risk scores

---

## Phase 7 — Full Application Integration

Status: ⏳ Pending

```text
React Frontend
      ↕
Backend API
      ↕
Database
      ↕
ML Model
```

---

## Phase 8 — Testing & Deployment

Status: ⏳ Pending

* Unit testing
* API testing
* ML testing
* Frontend testing
* Integration testing
* Security testing
* Performance testing
* Deployment

---

# 🔮 Future Enhancements

Future versions may include:

* Real-time activity monitoring
* Advanced anomaly detection
* User behavioral baselines
* Temporal behavioral analysis
* Explainable AI
* Automated investigation recommendations
* Role-based access control
* Automated incident response
* Email notifications
* Advanced security reports
* Cloud deployment
* Docker deployment
* Model monitoring
* Automated model retraining

---

# 🔐 Security Considerations

The project focuses on behavioral security analytics and risk-based user monitoring.

Important considerations include:

* User activity monitoring
* Risk-based detection
* Suspicious activity identification
* Severity classification
* Alert prioritization
* Investigation workflows
* Secure ML model integration
* Authentication and authorization
* Secure API communication

This project is currently a research/academic implementation and requires additional security validation and hardening before production deployment.

---

# 📚 Dataset

This project uses the:

**CERT Insider Threat Dataset r4.2**

The dataset contains simulated employee activity logs across multiple activity categories:

* Logon
* Device
* File
* Email
* HTTP/Web activity
* LDAP

The dataset is used for:

* Behavioral analysis
* Feature engineering
* Machine learning
* Risk scoring
* Insider threat detection

The raw dataset is not included in this repository because of its large size.

---

# 🎯 Project Objectives

The project aims to:

* Monitor user behavioral activities
* Analyze user activity patterns
* Generate behavioral profiles
* Identify suspicious behavior
* Detect potential insider threats
* Calculate behavioral risk scores
* Apply machine learning for threat detection
* Classify threat severity
* Provide a professional security console
* Support future analyst investigation workflows

---

# 🌟 Advantages

* AI-assisted insider threat detection
* Multi-source behavioral analysis
* Behavioral risk scoring
* Machine learning-based classification
* Risk severity classification
* High-risk user identification
* Professional security dashboard
* Modular frontend/backend architecture
* Future ML API integration
* Scalable project structure

---

# 🏁 Current Project Status

```text
┌───────────────────────────────────────────────┐
│       INSIDER THREAT BEHAVIORAL              │
│            INTELLIGENCE SYSTEM               │
├───────────────────────────────────────────────┤
│                                               │
│ Data Processing              ✅ COMPLETED     │
│ Feature Engineering          ✅ COMPLETED     │
│ Risk Scoring                 ✅ COMPLETED     │
│ ML Training                  ✅ COMPLETED     │
│ Model Evaluation             ✅ COMPLETED     │
│ Model Artifacts              ✅ COMPLETED     │
│                                               │
│ Frontend                     🚧 IN PROGRESS   │
│ Backend                      ⏳ PENDING       │
│ Database                     ⏳ PENDING       │
│ ML Integration               ⏳ PENDING       │
│ Full Integration             ⏳ PENDING       │
│ Testing                      ⏳ PENDING       │
│ Deployment                   ⏳ PENDING       │
│                                               │
└───────────────────────────────────────────────┘
```

---

# 🏆 Conclusion

The Insider Threat Behavioral Intelligence System has successfully completed the major Machine Learning and behavioral analytics pipeline.

The completed work includes:

```text
CERT Dataset
      ↓
Data Preprocessing
      ↓
EDA
      ↓
Behavioral Feature Engineering
      ↓
Risk Scoring
      ↓
Gradient Boosting Training
      ↓
Model Evaluation
      ↓
ML Risk Score
      ↓
Final Risk Score
      ↓
Severity Classification
```

The current development focus is the **frontend security console**.

After completing the frontend, the project will proceed to backend development, database integration, ML model integration, frontend-backend communication, testing, and final deployment.

The final goal is to provide an end-to-end cybersecurity platform capable of transforming user activity data into actionable insider-threat intelligence.

---

## ⭐ Project Development Status

**Machine Learning:** ✅ Completed

**Behavioral Analytics:** ✅ Completed

**Risk Scoring:** ✅ Completed

**Model Training:** ✅ Completed

**Frontend:** 🚧 In Progress

**Backend:**  🚧 In Progress

**Database:**  🚧 In Progress

**ML Integration:** ⏳ Pending

**Final Application:** 🚧 Under Development
