# 🛡️ Insider Threat Detection System

## Project Title

**Insider Threat Behavioral Intelligence System**

## Brief One Line Summary

An AI/ML-based cybersecurity system that analyzes user behavior and detects potentially malicious insider activities using machine learning and an interactive Streamlit dashboard.

---

## Overview

The **Insider Threat Detection System** is a machine learning and behavioral analytics project designed to identify suspicious activities performed by users within an organization.

Insider threats can occur when an authorized employee or user misuses legitimate access to steal data, compromise systems, or perform unauthorized activities. Traditional security systems often focus on external attacks, while this project focuses on **user behavior and activity patterns**.

The system processes user activity data, extracts meaningful behavioral features, applies machine learning techniques, and generates predictions indicating whether a user's behavior is **normal or potentially suspicious**.

The project also provides an interactive **Streamlit dashboard** for exploring user activity, viewing model predictions, and understanding suspicious behavior.

---

## Problem Statement

Organizations generate large amounts of user activity data such as:

* Login and logout activity
* File access
* USB/device usage
* Email activity
* Web browsing
* Application usage
* Data access patterns

Manually analyzing this data is difficult and time-consuming.

The objective of this project is to develop a machine learning-based system that can:

1. Analyze user behavioral patterns.
2. Identify unusual or suspicious activities.
3. Detect potential insider threats.
4. Provide risk-based insights.
5. Present results through an interactive dashboard.
6. Help security teams investigate suspicious users.

---

## Dataset

### CERT Insider Threat Dataset

This project uses the **CERT Insider Threat Dataset**, a synthetic cybersecurity dataset developed for insider-threat research.

The dataset contains different types of organizational activity, including:

* Logon activity
* Device/USB activity
* File activity
* HTTP/web activity
* Email activity
* User information
* Psychological/personality-related information in some versions

The raw activity logs are transformed into behavioral features suitable for machine learning.

### Dataset Processing

The general preprocessing pipeline is:

```text
Raw CERT Dataset
       ↓
Data Cleaning
       ↓
Data Integration
       ↓
Feature Extraction
       ↓
Behavioral Feature Engineering
       ↓
Model Training
       ↓
Threat Prediction
```

> **Note:** The CERT dataset is not included in this repository because of its size and dataset distribution considerations. Download the appropriate dataset separately and place the required files in the project's data directory.

---

## Tools and Technologies

### Programming Language

* **Python**

### Machine Learning

* Scikit-learn
* Pandas
* NumPy
* Matplotlib
* Seaborn

### Dashboard

* **Streamlit**

### Development Tools

* Jupyter Notebook / Kaggle Notebook
* VS Code
* Git
* GitHub

### Data Processing

* Pandas
* NumPy
* Feature Engineering
* Data Cleaning
* Data Aggregation

---

## Methods

The project follows a behavioral machine learning pipeline.

### 1. Data Collection

Activity logs are collected from the CERT Insider Threat Dataset.

### 2. Data Preprocessing

The raw data is cleaned and transformed.

Major preprocessing steps include:

* Handling missing values
* Removing duplicate records
* Converting timestamps
* Normalizing data formats
* Filtering irrelevant records
* Combining multiple activity logs

### 3. Feature Engineering

User-level behavioral features are created from activity logs.

Example features include:

| Feature              | Description                           |
| -------------------- | ------------------------------------- |
| Login Frequency      | Number of login events                |
| File Access Count    | Number of files accessed              |
| USB Usage            | Number of removable-device activities |
| Email Activity       | Number of emails/actions              |
| Web Activity         | Number of web interactions            |
| After-Hours Activity | Activity outside normal working hours |
| Unique Files         | Number of unique files accessed       |
| Activity Frequency   | Overall user activity level           |

### 4. Behavioral Analysis

Normal user behavior is compared against unusual patterns.

Potential indicators include:

* Abnormally high activity
* Unusual login times
* Excessive file access
* Suspicious USB usage
* Unusual web activity
* Sudden changes in user behavior

### 5. Machine Learning

Machine learning algorithms can be used to classify or identify suspicious behavior.

Possible models include:

* Logistic Regression
* Decision Tree
* Random Forest
* Gradient Boosting
* Isolation Forest
* Support Vector Machine

The final model can be selected based on evaluation metrics and the characteristics of the dataset.

### 6. Risk Prediction

The model generates a prediction or risk score for user behavior.

Example:

```text
User Activity
      ↓
Feature Extraction
      ↓
ML Model
      ↓
Risk Score
      ↓
Normal / Suspicious
```

---

## Key Insights

The system is designed to provide insights such as:

* Which users demonstrate unusual behavior?
* Which activities contribute most to the threat score?
* Are users accessing files outside normal working hours?
* Is there unusual removable-device activity?
* Are there sudden changes in user activity?
* Which users require further investigation?

### Example Risk Classification

```text
🟢 Low Risk
Normal behavioral pattern

🟡 Medium Risk
Unusual activity detected

🔴 High Risk
Strong behavioral indicators of potential insider threat
```

> A high-risk prediction should be treated as an alert for investigation, not as proof that a person is malicious.

---

## Dashboard / Model / Output

The project uses **Streamlit** to provide an interactive dashboard.

### Dashboard Features

The dashboard can include:

* 📊 User activity statistics
* 👤 User-wise behavioral analysis
* 🚨 Suspicious user identification
* 📈 Activity trends
* 🔍 Threat/risk analysis
* 🤖 ML model predictions
* 📋 Prediction tables
* 📉 Model performance metrics

### Example Dashboard Structure

```text
------------------------------------------------
        INSIDER THREAT DETECTION
------------------------------------------------

Total Users        Suspicious Users
   1,000                 25

------------------------------------------------
             User Activity Overview
------------------------------------------------

[ Activity Chart ]

------------------------------------------------
             Threat Analysis
------------------------------------------------

User ID       Risk Score       Status
USER001          0.12          Normal
USER002          0.87          Suspicious
USER003          0.31          Normal
------------------------------------------------
```

---

## How to Run this Project?

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/insider-threat-detection.git
```

### 2. Navigate to the Project

```bash
cd insider-threat-detection
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

### 4. Activate the Virtual Environment

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

**Windows CMD:**

```cmd
.venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Add the Dataset

Download the required CERT Insider Threat Dataset and place the required files inside the project's data directory.

Example:

```text
insider-threat-detection/
│
├── data/
│   ├── logon.csv
│   ├── device.csv
│   ├── file.csv
│   ├── email.csv
│   ├── http.csv
│   └── user.csv
│
├── notebooks/
├── models/
├── src/
├── app.py
├── requirements.txt
└── README.md
```

### 7. Run the Streamlit Application

```bash
streamlit run app.py
```

If the `streamlit` command is not recognized, use:

```bash
python -m streamlit run app.py
```

### 8. Open the Dashboard

After running the application, Streamlit will provide a local address such as:

```text
http://localhost:8501
```

Open this address in your browser.

---

## Results & Conclusion

The Insider Threat Detection System demonstrates how machine learning and behavioral analytics can be used to analyze large-scale user activity and identify potentially suspicious behavior.

The system provides:

* Automated behavioral analysis
* Suspicious activity detection
* User-level risk assessment
* Interactive visualization
* Machine learning-based predictions
* A foundation for security investigation

The project shows that analyzing **behavioral patterns rather than relying only on individual events** can provide valuable information for detecting potential insider threats.

However, machine learning predictions should support security analysts rather than automatically making decisions about individuals. False positives, changing user behavior, and dataset limitations must be considered.

---

## Future Work

The project can be further improved by adding:

* 🔹 Real-time activity monitoring
* 🔹 Deep learning models
* 🔹 Advanced anomaly detection
* 🔹 User behavior profiling
* 🔹 Explainable AI (XAI)
* 🔹 Automated alert generation
* 🔹 Email/SMS security alerts
* 🔹 Role-based risk analysis
* 🔹 Time-series behavioral modeling
* 🔹 SIEM integration
* 🔹 Cybersecurity threat intelligence integration
* 🔹 Continuous model retraining
* 🔹 Deployment using Docker and cloud platforms

---

## Author & Contact

### **Prem Raj Barnwal**

**B.Tech — Computer Science Engineering**
**Specialization: Artificial Intelligence & Machine Learning**
**LNCT University, Bhopal**

📧 **Email:** [premrajbarnwal9122@gmail.com](mailto:premrajbarnwal9122@gmail.com)

🔗 **LinkedIn:** [linkedin.com/in/Premrajbarnwal](https://www.linkedin.com/in/Premrajbarnwal)

---

## ⭐ Project Highlights

```text
Artificial Intelligence
        +
Machine Learning
        +
Cybersecurity
        +
Behavioral Analytics
        +
Streamlit Dashboard
        ↓
INSIDER THREAT DETECTION SYSTEM
```

If you find this project useful, consider giving the repository a ⭐ on GitHub.


