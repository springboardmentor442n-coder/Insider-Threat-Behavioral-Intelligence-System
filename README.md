# AI-Powered Insider Threat Detection & Behavioral Intelligence System

An AI-powered cybersecurity web application that detects potential insider threats by analyzing employee behavioral patterns using Machine Learning and behavioral risk analysis.

The system provides a Flask-based Security Operations Center (SOC)-style platform for security analysts to authenticate, analyze employees, perform individual or bulk predictions, assess risk, and review prediction history.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [Objectives](#objectives)
- [Key Features](#key-features)
- [System Workflow](#system-workflow)
- [Machine Learning Workflow](#machine-learning-workflow)
- [Behavioral Features](#behavioral-features)
- [Risk Assessment](#risk-assessment)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Database Design](#database-design)
- [Application Pages](#application-pages)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [First-Time Setup](#first-time-setup)
- [How to Use](#how-to-use)
- [Individual Threat Analysis](#individual-threat-analysis)
- [Bulk CSV Analysis](#bulk-csv-analysis)
- [CSV Format](#csv-format)
- [Understanding Results](#understanding-results)
- [Reports](#reports)
- [Database](#database)
- [Machine Learning Models](#machine-learning-models)
- [Model Evaluation](#model-evaluation)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Project Demonstration](#project-demonstration)
- [Future Enhancements](#future-enhancements)
- [Limitations](#limitations)
- [Privacy and Security](#privacy-and-security)
- [Author](#author)

---

## Project Overview

Insider threats are security incidents caused by individuals who have legitimate access to an organization's systems, applications, devices, files, emails, or other resources.

Unlike external attacks, insider threats can be difficult to detect because the user may already have authorized access.

This project analyzes employee behavioral information and uses Machine Learning together with behavioral risk analysis to identify potentially risky employee activity.

### End-to-End Pipeline

```text
Employee Behavioral Data
          |
          v
Data Preprocessing
          |
          v
Feature Engineering
          |
          v
Machine Learning Model
          |
          v
Threat Probability
          |
          v
Behavioral Risk Analysis
          |
          v
Overall Risk Assessment
          |
          v
Security Status / Recommendation
          |
          v
Flask Web Application
          |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
      Dashboard        Bulk CSV Analysis       Reports
```

---

## Problem Statement

Organizations generate large amounts of employee activity data through:

- Login systems
- Computers and devices
- USB devices
- File systems
- Email systems
- Web activity
- Network and directory services

Manually monitoring this information is difficult and time-consuming.

The objective of this project is to develop an intelligent system that analyzes employee behavioral patterns and identifies employees who may represent an insider security risk.

---

## Objectives

The major objectives of the project are:

1. Develop an AI/ML-based insider threat detection system.
2. Analyze employee behavioral characteristics.
3. Predict whether an employee is `NORMAL` or `THREAT`.
4. Calculate threat probability.
5. Calculate a behavioral risk score.
6. Determine an ML-based risk level.
7. Determine an overall risk level.
8. Generate a security-oriented final status/recommendation.
9. Provide individual employee threat analysis.
10. Support bulk analysis using CSV files.
11. Store employee and prediction information in SQLite.
12. Provide historical prediction reports.
13. Provide a centralized security dashboard.

---

## Key Features

### Authentication

- Login system for security analysts.
- Protected application routes using Flask-Login.
- Passwords stored using password hashing.

### Security Dashboard

Provides an overview of the application and security information.

### Employee Management

Stores employee information and behavioral features.

### Individual Threat Analysis

Analyzes one employee and generates:

- ML prediction
- Threat probability
- ML risk level
- Behavioral risk score
- Overall risk
- Final status
- Security recommendation

### Bulk CSV Analysis

Allows multiple employee records to be uploaded and analyzed in one operation.

The bulk analysis page displays:

- Total employees
- Successful predictions
- Failed predictions
- Threat predictions
- Critical-risk employees
- Individual employee results

### Prediction Reports

The Reports page provides prediction history and summary statistics.

### Database Storage

SQLite stores:

- Users
- Employees
- Predictions
- Risk indicators

---

## System Workflow

### Individual Analysis

```text
1. User opens application
          |
2. User logs in
          |
3. Dashboard
          |
4. Threat Analysis
          |
5. Employee behavioral data
          |
6. Data validation/preprocessing
          |
7. Machine Learning prediction
          |
8. Threat probability
          |
9. Behavioral risk analysis
          |
10. Overall risk assessment
          |
11. Final security status
          |
12. Result stored in database
          |
13. Result displayed to analyst
```

### Bulk Analysis

```text
CSV File
   |
   v
CSV Validation
   |
   v
Read Employee Records
   |
   v
Process Each Employee
   |
   v
Machine Learning Prediction
   |
   v
Behavioral Risk Analysis
   |
   v
Overall Risk
   |
   v
Bulk Results Table
```

---

## Machine Learning Workflow

The Machine Learning pipeline consists of:

```text
Raw Dataset
    |
    v
Data Cleaning
    |
    v
Data Preprocessing
    |
    v
Feature Engineering
    |
    v
Feature Preparation
    |
    v
Model Training
    |
    v
Model Evaluation
    |
    v
Model Serialization
    |
    v
Flask Prediction Pipeline
```

The deployed application loads the trained model rather than retraining the model every time a prediction is requested.

---

## Primary Machine Learning Model

The primary prediction model used by the application is:

**Random Forest Classifier**

The trained model is stored under:

```text
ml/models/random_forest.pkl
```

Other model artifacts are also included in the project for model comparison and experimentation.

---

## Behavioral Features

The project uses employee behavioral features from multiple activity categories.

### Login and Device Behavior

```text
login_count
logoff_count
night_login_count
weekend_login_count
unique_pc_count
night_login_ratio
weekend_login_ratio
pc_switching_frequency
```

### USB Activity

```text
usb_connect_count
usb_disconnect_count
usb_total_activity
usb_connect_ratio
```

### File Activity

```text
file_copy_count
avg_daily_file_copy
max_daily_file_copy
```

### Email Activity

```text
email_sent_count
external_email_count
avg_attachment_count
avg_email_size
external_email_ratio
```

### Web Activity

```text
website_visit_count
unique_domain_count
avg_daily_web_activity
```

### Personality Features

```text
O
C
E
A
N
```

These numerical features are part of the behavioral data used by the prediction pipeline.

---

## Risk Assessment

The application separates Machine Learning prediction from the final security assessment.

### ML Prediction

The Machine Learning model produces:

```text
NORMAL
```

or

```text
THREAT
```

### Threat Probability

The model provides a probability associated with the threat class.

Example:

```text
Threat Probability: 65.39%
```

### ML Risk

The threat probability is interpreted into an ML risk level such as:

```text
LOW
MEDIUM
HIGH
```

### Behavioral Risk Score

The behavioral analysis generates a score from:

```text
0 to 100
```

A higher score represents greater behavioral risk.

### Overall Risk

The application combines the relevant ML and behavioral risk information to determine an overall risk level:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

### Final Status

The application can convert the overall assessment into an operational status such as:

```text
SAFE
MONITOR
ACTION REQUIRED
```

Therefore:

```text
ML Prediction != Final Security Risk
```

For example, an employee can have:

```text
ML Prediction: NORMAL
Behavioral Score: 78/100
Overall Risk: CRITICAL
Final Status: ACTION REQUIRED
```

This allows the analyst to consider both the Machine Learning result and behavioral risk.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Flask | Web application framework |
| Flask-Login | Authentication |
| SQLAlchemy | Database ORM |
| SQLite | Database |
| Scikit-learn | Machine Learning |
| Random Forest | Primary classification model |
| Pandas | Data processing |
| NumPy | Numerical processing |
| HTML | Web page structure |
| CSS | Styling |
| Bootstrap | UI components |
| Git | Version control |
| GitHub | Source code repository |

---

## Project Structure

```text
AI_Insider_Threat_Detection_System/
|
├── app/
|   |
|   ├── routes/
|   |   ├── __init__.py
|   |   ├── auth.py
|   |   ├── dashboard.py
|   |   ├── employee.py
|   |   ├── prediction.py
|   |   ├── bulk_prediction.py
|   |   └── reports.py
|   |
|   ├── templates/
|   |   ├── login.html
|   |   ├── dashboard.html
|   |   ├── employees.html
|   |   ├── prediction_result.html
|   |   ├── bulk_analysis.html
|   |   └── reports.html
|   |
|   ├── config.py
|   ├── extensions.py
|   ├── models.py
|   └── __init__.py
|
├── dataset/
|   └── processed/
|       └── employee_features.csv
|
├── ml/
|   |
|   ├── models/
|   |   ├── random_forest.pkl
|   |   ├── xgboost.pkl
|   |   ├── isolation_forest.pkl
|   |   ├── preprocessor.pkl
|   |   ├── feature_columns.pkl
|   |   └── ...
|   |
|   ├── evaluation/
|   |   ├── confusion_matrix.png
|   |   ├── roc_curve.png
|   |   ├── precision_recall_curve.png
|   |   ├── learning_curve.png
|   |   ├── evaluation_report.csv
|   |   └── ...
|   |
|   ├── predict.py
|   ├── model_loader.py
|   ├── train_model.py
|   └── evaluate.py
|
├── preprocessing/
|   ├── aggregator.py
|   ├── check_dataset.py
|   ├── dataset_config.py
|   ├── device_processor.py
|   ├── email_processor.py
|   ├── file_processor.py
|   ├── http_processor.py
|   ├── ldap_processor.py
|   ├── login_processor.py
|   ├── preprocess.py
|   └── psychometric_processor.py
|
├── instance/
|   └── insider_threat.db
|
├── uploads/
|
├── logs/
|
├── app.py
├── create_admin.py
├── dataset_info.py
├── one_time_script.py
├── requirements.txt
├── run.py
├── .gitignore
├── LICENSE
└── README.md
```

---

## Database Design

The application uses SQLite with SQLAlchemy.

Database file:

```text
instance/insider_threat.db
```

### Main Tables

```text
users
employees
predictions
risk_indicators
```

### User

Stores application users.

Important fields:

```text
id
username
email
password_hash
role
created_at
```

### Employee

Stores employee details and behavioral features.

Examples:

```text
employee_id
department
role
business_unit
login_count
logoff_count
night_login_count
weekend_login_count
unique_pc_count
USB activity
file activity
email activity
web activity
personality features
```

### Prediction

Stores prediction results.

Examples:

```text
prediction
status
threat_probability
normal_probability
ml_risk_level
behavioral_risk_score
overall_risk_level
recommendation
model_name
created_at
```

### RiskIndicator

Stores risk indicators associated with a prediction.

Examples:

```text
feature
value
points
severity
reason
```

### Database Relationship

```text
User

Employee
   |
   | 1 : Many
   v
Prediction
   |
   | 1 : Many
   v
RiskIndicator
```

---

## Application Pages

### Login

```text
/auth/login
```

Used to authenticate the security analyst.

### Dashboard

Provides the main security overview.

### Employees

Displays employee records and behavioral information.

### Threat Analysis

Performs individual employee analysis.

### Bulk CSV Analysis

```text
/bulk-analysis/
```

Uploads and analyzes multiple employee records.

### Reports

```text
/reports/
```

Displays historical prediction results and risk statistics.

---

# Installation

## 1. Install Python

Install Python 3.x.

Verify the installation:

```bash
python --version
```

or on Windows:

```bash
py --version
```

---

## 2. Clone the Repository

```bash
git clone https://github.com/springboardmentor442n-coder/Insider-Threat-Behavioral-Intelligence-System.git
```

Move into the project:

```bash
cd Insider-Threat-Behavioral-Intelligence-System
```

---

## 3. Create a Virtual Environment

### Windows

```bash
python -m venv environment
```

### Linux/macOS

```bash
python3 -m venv environment
```

---

## 4. Activate the Virtual Environment

### Windows CMD

```bash
environment\Scripts\activate
```

### Windows PowerShell

```powershell
environment\Scripts\Activate.ps1
```

### Linux/macOS

```bash
source environment/bin/activate
```

After activation, the terminal should show:

```text
(environment)
```

---

## 5. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Running the Application

After activating the virtual environment:

```bash
python run.py
```

On Windows, this can also be:

```bash
py run.py
```

The Flask development server should start.

Example:

```text
Running on http://127.0.0.1:5000
```

---

# Open the Application

Open a browser and visit:

```text
http://127.0.0.1:5000/
```

The application should take you to the login page when authentication is required.

If necessary, the login page can be opened directly:

```text
http://127.0.0.1:5000/auth/login
```

---

# First-Time Setup

If an administrator account needs to be created, run:

```bash
python create_admin.py
```

Follow the prompts.

Then:

1. Start the application.
2. Open the browser.
3. Open the login page.
4. Enter the created credentials.
5. Open the Dashboard.

Do not commit real passwords or production credentials to GitHub.

---

# How to Use

## Step 1 - Start the application

```bash
python run.py
```

## Step 2 - Open the browser

```text
http://127.0.0.1:5000/
```

## Step 3 - Login

Enter your application credentials.

## Step 4 - Open Dashboard

Review the main security information.

## Step 5 - Individual Threat Analysis

Open **Threat Analysis** and provide the required employee behavioral information.

## Step 6 - View Prediction

The result displays:

- Employee
- Department
- ML Prediction
- Threat Probability
- ML Risk
- Behavioral Score
- Overall Risk
- Final Status
- Model

## Step 7 - Bulk CSV Analysis

Open **Bulk CSV Analysis**.

Select a CSV file and click:

```text
Analyze CSV
```

## Step 8 - View Bulk Results

The system displays the results for all employee records.

## Step 9 - Open Reports

Open **Reports** to view prediction history and summary statistics.

---

# Individual Threat Analysis

The individual analysis workflow is:

```text
Employee Input
      |
      v
Feature Processing
      |
      v
Random Forest Prediction
      |
      v
Threat Probability
      |
      v
Behavioral Risk Calculation
      |
      v
Overall Risk
      |
      v
Final Status
      |
      v
Database Storage
```

---

# Bulk CSV Analysis

The application supports batch analysis of multiple employees.

Navigate to:

```text
/bulk-analysis/
```

Upload the employee CSV.

The system processes each row independently.

The results include:

```text
CSV Row
Employee
Department
ML Prediction
Threat Probability
ML Risk
Behavioral Score
Overall Risk
Final Status
Model
Status
```

The summary section displays:

```text
Total Employees
Successful
Failed
Threat Predictions
Critical Risk
```

---

# CSV Format

The uploaded CSV should contain the employee behavioral features expected by the Machine Learning pipeline.

Expected feature fields include:

```text
employee_id
department
role
business_unit
login_count
logoff_count
night_login_count
weekend_login_count
unique_pc_count
night_login_ratio
weekend_login_ratio
pc_switching_frequency
usb_connect_count
usb_disconnect_count
usb_total_activity
usb_connect_ratio
file_copy_count
avg_daily_file_copy
max_daily_file_copy
email_sent_count
external_email_count
avg_attachment_count
avg_email_size
external_email_ratio
website_visit_count
unique_domain_count
avg_daily_web_activity
O
C
E
A
N
```

## Important CSV Rules

### Do

- Use the expected column names.
- Use numeric values for numerical features.
- Include employee identifiers.
- Keep the feature structure expected by the model.
- Use the CSV template provided by the application.

### Do Not

- Add the prediction result manually.
- Add `NORMAL` or `THREAT` as an input prediction.
- Add the overall risk manually.
- Add the behavioral score manually.
- Change required feature names.
- Upload unrelated data.

The application generates the prediction and risk results automatically.

---

# Understanding Results

Example:

```text
Employee: EMP1004
ML Prediction: THREAT
Threat Probability: 31.8%
ML Risk: MEDIUM
Behavioral Score: 78/100
Overall Risk: CRITICAL
Final Status: ACTION REQUIRED
Model: Random Forest
```

Another employee may have:

```text
Employee: EMP1002
ML Prediction: NORMAL
Threat Probability: 27.49%
ML Risk: LOW
Behavioral Score: 0/100
Overall Risk: LOW
Final Status: SAFE
Model: Random Forest
```

The final security status considers the overall assessment rather than simply displaying the Machine Learning class.

---

# Reports

The Reports page provides prediction history.

It includes information such as:

```text
Employee
Department
Prediction
Threat Probability
ML Risk
Risk Score
Overall Risk
Model
Date
```

It also provides summary statistics such as:

```text
Total Predictions
Threat Predictions
Normal Predictions
Critical Risk
```

This allows a security analyst to review previously generated predictions.

---

# Database

The application uses SQLite.

Database location:

```text
instance/insider_threat.db
```

You can inspect the database using:

- DB Browser for SQLite
- SQLite command line
- A SQLite extension in VS Code

Main tables:

```text
users
employees
predictions
risk_indicators
```

For security and repository cleanliness, runtime database files should normally be excluded from Git using `.gitignore`.

---

# Machine Learning Models

The project contains trained Machine Learning artifacts under:

```text
ml/models/
```

Important files include:

```text
random_forest.pkl
xgboost.pkl
isolation_forest.pkl
preprocessor.pkl
feature_columns.pkl
feature_importance.pkl
```

The deployed application uses the trained Random Forest model for the primary prediction workflow.

---

# Model Evaluation

The project contains model evaluation artifacts, including:

```text
Confusion Matrix
ROC Curve
Precision-Recall Curve
Learning Curve
Feature Importance
Evaluation Report
Model Comparison
```

These files are available under the ML evaluation/model directories and can be used to analyze model performance.

---

# Testing

## Test 1 - Login

Open:

```text
http://127.0.0.1:5000/
```

Verify that authentication is displayed.

## Test 2 - Dashboard

Login and verify that the Dashboard loads.

## Test 3 - Individual Prediction

Open **Threat Analysis**.

Enter valid employee data.

Verify that the prediction result contains:

```text
Prediction
Threat Probability
ML Risk
Behavioral Score
Overall Risk
Final Status
```

## Test 4 - Bulk CSV

Open **Bulk CSV Analysis**.

Upload a valid CSV.

Verify:

```text
Total Employees
Successful
Failed
Threat Predictions
Critical Risk
```

## Test 5 - Reports

Open **Reports**.

Verify that prediction history is displayed.

## Test 6 - Database

Open the SQLite database using a database viewer and verify that application records are stored.

---

# Troubleshooting

## `ModuleNotFoundError`

Example:

```text
ModuleNotFoundError: No module named 'flask'
```

Activate the virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

---

## Flask Does Not Start

Make sure the virtual environment is active.

Windows:

```bash
environment\Scripts\activate
```

Then:

```bash
python run.py
```

---

## Model Not Found

If an error refers to a model file such as:

```text
random_forest.pkl
```

verify that the required ML files exist under:

```text
ml/models/
```

---

## CSV Prediction Fails

Check:

1. Column names.
2. Missing values.
3. Numeric data types.
4. Required features.
5. CSV structure.

Use the CSV template provided by the application.

---

## Login Page

The application can normally be opened at:

```text
http://127.0.0.1:5000/
```

If direct access is needed:

```text
http://127.0.0.1:5000/auth/login
```

---

# Project Demonstration

For a college/project demonstration, the recommended sequence is:

### 1. Start the application

```bash
python run.py
```

### 2. Open the browser

```text
http://127.0.0.1:5000/
```

### 3. Login

Show the authentication page.

### 4. Dashboard

Explain that the Dashboard provides the main security overview.

### 5. Threat Analysis

Demonstrate an individual employee prediction.

Explain:

> Employee behavioral features are processed and passed to the trained Machine Learning model. The system then combines the ML result with behavioral risk analysis to produce an overall security assessment.

### 6. Bulk CSV Analysis

Open the Bulk CSV Analysis page.

Upload the prepared CSV.

Click **Analyze CSV**.

### 7. Bulk Results

Show:

- Total Employees
- Successful
- Failed
- Threat Predictions
- Critical Risk
- Individual employee results

### 8. Reports

Open the Reports page and demonstrate the prediction history.

### 9. Database

Show the SQLite database and its tables if required.

---

# Suggested Screenshots

For a professional GitHub repository, screenshots can be placed in:

```text
screenshots/
├── login.png
├── dashboard.png
├── threat-analysis.png
├── prediction-result.png
├── bulk-upload.png
├── bulk-results.png
└── reports.png
```

Then they can be displayed in this README using:

```markdown
## Login

![Login](screenshots/login.png)

## Dashboard

![Dashboard](screenshots/dashboard.png)

## Threat Analysis

![Threat Analysis](screenshots/threat-analysis.png)

## Bulk CSV Analysis

![Bulk Analysis](screenshots/bulk-results.png)

## Reports

![Reports](screenshots/reports.png)
```

---

# Security and Privacy

This project is intended for academic, educational, and research purposes.

Do not upload confidential employee information to a public GitHub repository.

Never commit:

```text
Passwords
API keys
Private credentials
Confidential employee information
Production database files
Private company data
```

Use synthetic or anonymized data for demonstrations.

The local SQLite database and runtime files should normally be excluded using `.gitignore`.

---

# Future Enhancements

Possible future improvements include:

- Real-time employee monitoring
- SIEM integration
- Real-time anomaly detection
- Security alert notifications
- Email alerts
- SMS alerts
- Advanced anomaly detection
- Deep Learning models
- PostgreSQL/MySQL support
- Cloud deployment
- Docker deployment
- Role-based access control
- Real-time event streaming
- Automated incident response
- Security alert prioritization
- Production WSGI deployment

---

# Limitations

### 1. Dataset Dependency

Prediction quality depends on the quality and representativeness of the available employee behavioral data.

### 2. Trained Model

The deployed application uses a previously trained Machine Learning model rather than continuously retraining itself in real time.

### 3. CSV-Based Bulk Processing

Bulk analysis depends on correctly formatted CSV input.

### 4. SQLite

SQLite is appropriate for this academic/local implementation. A production enterprise deployment would generally use a more scalable database.

### 5. Development Server

The Flask development server is suitable for demonstration. A production deployment should use a production WSGI server and appropriate infrastructure.

---

# Project Highlights

```text
AI-Based Insider Threat Detection
Machine Learning
Random Forest Classification
Employee Behavioral Analysis
Threat Probability
Behavioral Risk Score
Overall Risk Assessment
Final Security Status
Individual Employee Analysis
Bulk CSV Analysis
Flask Web Application
SQLite Database
User Authentication
Prediction History
Security Reports
Model Evaluation
SOC-Style Dashboard
```

---

# End-to-End Summary

```text
                    EMPLOYEE DATA
                          |
                          v
                 DATA PREPROCESSING
                          |
                          v
                  FEATURE ENGINEERING
                          |
                          v
                  RANDOM FOREST MODEL
                          |
                          v
                 ML THREAT PREDICTION
                          |
                          v
                  THREAT PROBABILITY
                          |
                          v
               BEHAVIORAL RISK ANALYSIS
                          |
                          v
                    RISK SCORE
                          |
                          v
                    OVERALL RISK
                          |
              +-----------+-----------+
              |           |           |
              v           v           v
             LOW        MEDIUM      CRITICAL
                          |
                          v
                 SECURITY STATUS
                          |
                          v
                  FLASK WEB PLATFORM
                          |
              +-----------+-----------+
              |           |           |
              v           v           v
         DASHBOARD   BULK ANALYSIS   REPORTS
```

---

# Author

## Mohammed Mohsin

**B.Tech - Electronics and Communication Engineering**

**B.S. Abdur Rahman Crescent Institute of Science and Technology**

**Batch: 2026**

---

# Project Domain

```text
Artificial Intelligence
Machine Learning
Cybersecurity
Insider Threat Detection
Behavioral Intelligence
Data Analytics
Web Application Development
```

---

# License

This project is developed for academic and educational purposes.

See the `LICENSE` file for additional information.

---

## Final Note

The **AI-Powered Insider Threat Detection & Behavioral Intelligence System** demonstrates an end-to-end approach to insider threat analysis by combining Machine Learning, employee behavioral analytics, risk scoring, database storage, and a Flask-based security dashboard.

The system supports both individual and bulk employee analysis and provides security analysts with actionable risk information through a centralized web interface.
