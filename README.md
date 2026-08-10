# 🛡️ Insider Threat Behavioral Intelligence System 🛡️

A Machine Learning-based **Insider Threat Behavioral Intelligence System** designed to analyze employee activities, identify abnormal behavior, calculate risk scores, and support security investigations using the **CERT Insider Threat Dataset (Release 4.2)**.

The system combines behavioral feature engineering, user behavior baseline, anomaly detection, behavior deviation analysis, risk scoring, explainable predictions, threat investigation, live feature processing, and an interactive web dashboard.

---

## 📌 Project Overview & Objectives

Enterprise security traditional perimeter defenses often fail against internal bad actors, compromised credentials, or privilege abuse. This project implements an AI-driven **Insider Threat Behavioral Intelligence System** built on top of multi-source audit logs (CERT v4.2 dataset)

This project analyzes employee behavioral activity and generates a **risk score** based on deviations from normal behavior.

### Key Capabilities
* **Behavioral Baseline Profiling:** Aggregates daily user activity across Logon, Device, File, Email, HTTP, and LDAP organizational context.
* **Hybrid Machine Learning & Anomaly Engine:** Combines supervised classification (XGBoost + SMOTE) with unsupervised anomaly detection (Isolation Forest).
* **Composite Risk Scoring Engine:** Blends ML fraud probabilities with a 5-component weighted UEBA behavioral risk framework to categorize threat severity (Low, Medium, High, Critical).

---

## 🏗️ System Architecture & Workflow

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
|                     ML & UEBA ENGINES                       |
|          XGBoost Classifier & Isolation Forest              |
+-------------------------------------------------------------+
                               │
                               ▼
+-------------------------------------------------------------+
|                COMPOSITE RISK SCORING ENGINE                |
|      Blended Risk Score & Severity Categorization Tiers     |
+-------------------------------------------------------------+
```

---
## 📊 Dataset & Feature Engineering

The system processes multi-source activity logs aggregated at a **User-Day** granularity ($330,452$ records across $1,000$ employees)[cite: 1, 3]:

### 1. Extracted Activity Features
* **Logon Activity:** `logon_count`, `off_hours_logons`, `distinct_pcs`
* **Removable Media (USB):** `usb_connects`, `off_hours_usb`
* **File Operations:** `files_copied_to_usb`, `sensitive_files_to_usb` (`.doc`, `.pdf`, `.zip`)`
* **Email Exfiltration:** `total_emails_sent`, `external_emails_sent`, `total_attachments`, `total_email_size`
* **Web Activity:** `http_requests`, `cloud_job_visits` (Dropbox, Google Drive, Job sites)
* **LDAP Organizational Context:** `role_encoded`, `department_encoded`, `supervisor_encoded`

## 📊 Feature Extraction

Activity logs are aggregated at a daily user level across several key dimensions:

* **Logon Activity:** Monitoring logon frequency, off-hours access, and workstation switches.
* **Device Usage:** Tracking removable media connections and off-hours USB activity.
* **File Operations:** Monitoring file copies and interactions with sensitive document types.
* **Email Communication:** Tracking outbound email volume, external recipients, and attachment sizes.
* **Web Activity:** Monitoring web traffic and visits to cloud storage or job portals.
* **Organizational Data:** Mapping roles, departments, and manager details using LDAP records.

---

## 🤖 Modeling Strategy

* **Supervised Learning:** An XGBoost classification pipeline combined with SMOTE oversampling to identify known insider threat patterns.
* **Unsupervised Anomaly Detection:** An Isolation Forest model running in parallel to catch unexpected behavioral deviations.
* **Leak-Free Pipeline:** Strict separation maintained between data preprocessing, feature scaling, and evaluation sets.

---

## 📈 Risk Scoring & Severity Tiers

The system combines multiple behavioral signals-

```text
Login Behavior
      +
Device Behavior
      +
Email Behavior
      +
File Behavior
      +
HTTP Behavior
      +
Behavior Deviation
      +
Anomaly Detection
      │
      ▼
   Risk Score
      │
      ▼
Risk Classification
      │
      ├── Low
      ├── Medium
      ├── High
      └── Critical
```

---

# 🔍 Explainable Security Analysis

The system is designed to answer two important questions:

### 1. Who is behaving abnormally?

```text
Employee → Anomaly Detection → Risk Score
```

### 2. Why is the employee considered risky?

```text
Risk Score
    │
    ▼
Behavior Deviation
    │
    ▼
Important Behavioral Factors
    │
    ▼
Investigation
```

This makes the project more suitable for practical security monitoring than a simple binary classification model.

---

# 👨‍💻 Author

**Tamanna Rani Choudhury**

**Infosys Springboard Internship – 2026**
