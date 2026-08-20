# 🛡️ Insider Threat Behavioral Intelligence System 🛡️

A Machine Learning-based **Insider Threat Behavioral Intelligence System** designed to analyze employee activities, identify abnormal behavior, calculate risk scores, and support security investigations using the **CERT Insider Threat Dataset (Release 4.2)**.

The system combines behavioral feature engineering, user behavior baseline, anomaly detection, behavior deviation analysis, risk scoring, explainable predictions, threat investigation, live feature processing, and an interactive web dashboard.

---

## 📌 Project Overview & Objectives

Enterprise security traditional perimeter defenses often fail against internal bad actors, compromised credentials, or privilege abuse. This project implements an AI-driven **Insider Threat Behavioral Intelligence System** built on top of multi-source audit logs from the **CERT v4.2 dataset**.

The system analyzes employee behavioral activity and generates a **risk score** based on behavioral patterns and deviations from expected activity.

### Key Capabilities

* **Behavioral Baseline Profiling:** Aggregates daily user activity across Logon, Device, File, Email, HTTP, and LDAP organizational context.

* **Hybrid Machine Learning & Anomaly Detection:** Combines supervised classification using **XGBoost** with **SMOTE** oversampling and unsupervised anomaly detection using **Isolation Forest**.

* **Composite Risk Scoring:** Combines the ML prediction probability with a weighted behavioral risk score to categorize activity into **Low, Medium, High, and Critical** threat levels.

* **Threat Investigation:** Allows analysts to select an employee and session date, review behavioral telemetry, and run a threat assessment.

* **Session Threat Feed:** Provides a filtered and paginated view of evaluated activity records by severity.

* **Behavior Simulator:** Allows analysts to modify selected behavioral activity parameters and evaluate the resulting threat risk.

---

## 🏗️ System Architecture & Workflow

The system follows a multi-stage pipeline that transforms raw CERT Insider Threat activity logs into behavioral features, ML predictions, risk scores, and interactive security analysis.

```text
+-------------------------------------------------------------+
|                 DATA INGESTION & PIPELINE                   |
|   Logon, Device, File, Email, HTTP Logs & LDAP Directory    |
+-------------------------------------------------------------+
                               │
                               ▼
+-------------------------------------------------------------+
|             FEATURE ENGINEERING & BASELINING                |
|   User-Day Aggregation, Categorical Encoding & Proxies      |
+-------------------------------------------------------------+
                               │
                               ▼
+-------------------------------------------------------------+
|                    ML & UEBA ENGINES                        |
|        XGBoost Classifier & Isolation Forest                |
+-------------------------------------------------------------+
                               │
                               ▼
+-------------------------------------------------------------+
|                COMPOSITE RISK SCORING ENGINE                |
|       ML Probability + Behavioral Risk Score                |
+-------------------------------------------------------------+
                               │
                               ▼
+-------------------------------------------------------------+
|                  FASTAPI BACKEND                            |
| Dashboard Stats | Threat Feed | User Logs | Predictions    |
+-------------------------------------------------------------+
                               │
                               ▼
+-------------------------------------------------------------+
|              INTERACTIVE WEB DASHBOARD                      |
| Dashboard | Threat Feed | Investigation | Simulator        |
+-------------------------------------------------------------+
```
---

## 📊 Dataset & Feature Engineering

The system is built using the **CERT Insider Threat Dataset (Release 4.2)**. The activity data is aggregated at a **User-Day** level to create behavioral profiles for employees.

The feature engineering process combines activity from multiple sources, including logon, device, file, email, HTTP, and LDAP organizational data.

### Extracted Activity Features

| Activity Source | Key Features |
|---|---|
| **Logon Activity** | `logon_count`, `off_hours_logons`, `distinct_pcs` |
| **Device / USB Activity** | `usb_connects`, `off_hours_usb` |
| **File Operations** | `files_copied_to_usb`, `sensitive_files_to_usb` |
| **Email Activity** | `total_emails_sent`, `external_emails_sent`, `total_attachments`, `total_email_size` |
| **Web Activity** | `http_requests`, `cloud_job_visits` |
| **Organizational Context** | `role_encoded`, `department_encoded`, `supervisor_encoded` |

### Feature Engineering Process

* **User-Day Aggregation:** Converts raw activity logs into daily behavioral records for each employee.
* **Behavioral Features:** Captures login patterns, workstation usage, USB activity, file transfers, email activity, and web activity.
* **Sensitive File Monitoring:** Tracks files copied to removable media, including sensitive document types.
* **Email Exfiltration Indicators:** Captures external email activity, attachment counts, and outbound email volume.
* **Web Activity Indicators:** Tracks HTTP activity and visits associated with cloud storage and job-related websites.
* **Organizational Context:** Encodes role, department, and supervisor information from LDAP data.

---

## 🤖 Modeling Strategy

The system uses a combination of supervised machine learning, anomaly detection, and behavioral risk analysis to identify potentially risky employee activity.

### Supervised Learning

An **XGBoost classifier** is used to predict the probability of insider threat activity from the engineered behavioral features.

**SMOTE (Synthetic Minority Oversampling Technique)** is used during model development to address class imbalance and improve detection of the minority threat class.

### Anomaly Detection

An **Isolation Forest** model is used separately to identify unusual behavioral patterns within employee activity. Its anomaly score provides an additional signal for security analysis.

### Behavioral Risk Analysis

A separate **behavioral risk scoring engine** evaluates multiple activity indicators, including:

- After-hours logon and USB activity
- USB and sensitive file activity
- External email and attachment activity
- HTTP and cloud/job-site activity
- Historical security events

These behavioral components are normalized and combined using configured weights to produce a behavioral risk score.

### Overall Risk Assessment

The final risk assessment combines the **XGBoost threat probability** with the **behavioral risk score**:

```text
XGBoost Threat Probability
            +
    Behavioral Risk Score
            │
            ▼
    Overall Risk Score
            │
            ▼
   Severity Classification
 Low → Medium → High → Critical
```
---

## 📈 Risk Scoring & Severity Tiers

The system generates an overall risk score by combining the supervised ML prediction with a separate behavioral risk score.

### Behavioral Risk Components

The behavioral risk engine evaluates five major areas:

1. **Behavioral Anomalies**  
   After-hours logon and USB activity.

2. **Privilege Misuse**  
   USB connections, file transfers, and sensitive files copied to USB.

3. **Data Access Violations**  
   Sensitive file activity, external emails, attachments, and outbound email volume.

4. **Access Pattern Deviations**  
   Workstation usage, HTTP requests, and cloud/job-site visits.

5. **Historical Security Events**  
   Historical security event indicators used as an additional behavioral signal.

Each component is normalized and combined using configured weights to produce a behavioral risk score between **0 and 100**.

### Overall Risk Score

The final score combines:

```text
XGBoost Threat Probability
            +
    Behavioral Risk Score
            │
            ▼
     Overall Risk Score
            │
            ▼
     Severity Classification
```

### Severity Classification

| Overall Risk Score | Severity |
|---:|---|
| **0 – <25** | Low |
| **25 – <50** | Medium |
| **50 – <75** | High |
| **75 – 100** | Critical |

---

## 🖥️ Application Features

The system provides an interactive security dashboard with four main workspaces:

### 1. Executive Dashboard

Provides an organization-level view of:

- Monitored employees
- Evaluated sessions
- High and Critical risk flags
- Average organizational risk score
- Risk distribution across evaluated sessions
- Organizational risk trends
- Top evaluated targets

### 2. Session Threat Feed

Provides a continuously replayed view of evaluated activity records with:

- Severity filtering
- Pagination
- Overall risk scores
- Activity indicators
- Direct access to employee investigation

### 3. Threat Analysis

Allows an analyst to:

- Select an employee
- Select a specific session date
- Review behavioral telemetry
- Run a threat assessment
- View the overall risk score and severity

### 4. Behavior Simulator

Allows an analyst to select an employee and modify behavioral activity parameters such as:

- After-hours logins
- USB activity
- File transfers
- Sensitive file transfers
- External emails
- HTTP requests
- Cloud/job-site visits

The modified activity can then be submitted to the prediction API to evaluate the resulting threat risk.

---

## 🔍 Explainable Security Analysis

The system is designed to help analysts understand both **who is showing unusual behavior** and **which behavioral signals contribute to the assessed risk**.

### 1. Who is behaving abnormally?

```text
Employee Activity
        │
        ▼
Anomaly Detection
        │
        ▼
Risk Assessment
        │
        ▼
Threat Severity
```

### 2. Why is the activity considered risky?

```test
Employee Activity
        │
        ▼
Behavioral Indicators
        │
        ├── After-hours activity
        ├── USB / file activity
        ├── External email activity
        ├── Web / cloud activity
        └── Other behavioral signals
                │
                ▼
        Behavioral Risk Score
                │
                ▼
         Overall Risk Score
                │
                ▼
          Investigation
```

---

## 🛠️ Technology Stack

### Machine Learning & Data Processing
- **Python**
- **Pandas** for data processing and feature preparation
- **NumPy** for numerical operations
- **Scikit-learn** for machine learning utilities and anomaly detection
- **XGBoost** for supervised threat classification
- **Imbalanced-learn (SMOTE)** for handling class imbalance

### Backend
- **FastAPI** for building the REST API
- **Uvicorn** for running the FastAPI application
- **Pydantic** for request data validation

### Frontend
- **React** for the interactive web interface
- **Axios** for communication between the frontend and backend
- **Recharts** for dashboard visualizations
- **Lucide React** for interface icons
- **Tailwind CSS** for styling

---

# 👨‍💻 Author

**Tamanna Rani Choudhury**

**Infosys Springboard Internship – 2026**
