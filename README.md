# Insider Threat Behavioral Intelligence System


An AI-powered Insider Threat Detection System designed to identify suspicious employee behavior using behavioral analytics and machine learning.


## 📌 Overview


The system analyzes user activities such as:


- Logon activities
- USB/device connections
- File activities
- Email activities
- HTTP/web activities


These activities are processed and converted into behavioral features to detect abnormal or risky behavior.


## 🎯 Objectives


- Detect potential insider threats
- Analyze employee behavioral patterns
- Calculate behavioral risk scores
- Classify users based on threat severity
- Provide security alerts and investigations
- Visualize risk information through a dashboard


## 🏗️ System Architecture


```text
User Activity Data
        ↓
Data Preprocessing
        ↓
Feature Engineering
        ↓
Machine Learning Model
        ↓
Risk Score Calculation
        ↓
Threat Classification
        ↓
Backend API
        ↓
Frontend Dashboard
🧠 Machine Learning

The project uses a trained Gradient Boosting model for behavioral risk prediction.

The model uses features including:

Logon count
Off-hours logons
Distinct PCs
USB connections
File activities
Sensitive file activities
Email activities
External emails
Attachments
HTTP requests
Off-hours HTTP activity
📊 Risk Classification

User behavior is classified into different risk levels:

Low
Medium
High
Critical

The system generates a risk score based on behavioral and machine learning analysis.

💻 Frontend

The frontend provides a security monitoring dashboard containing:

Dashboard
Threat Detection
Threat Center
Alerts
Investigations
Reports
User Management
User Details

The interface provides visual representations of employee risk and suspicious activities.

⚙️ Backend

The backend is developed using Python and FastAPI.

It provides APIs for:

User management
Behavioral analysis
Risk prediction
Alerts
Dashboard metrics
Investigations
Reports
Explainability
🗄️ Database

SQLite is used for storing application data.

The database stores information related to:

Users
Behavioral risk records
Security alerts
Investigations
📁 Project Structure
Insider-Threat-Behavioral-Intelligence-System/
│
├── backend/
├── datasets/
├── frontend/
├── ml/
├── notebooks/
├── scripts/
├── tests/
├── docs/
├── README.md
├── requirements.txt
└── .gitignore
📓 Notebooks

The notebooks contain the machine learning workflow including:

Dataset exploration
Data cleaning
Feature engineering
Behavioral analysis
Model training
Model evaluation
Risk analysis
🔄 Workflow
CERT Dataset
     ↓
Data Cleaning
     ↓
Feature Engineering
     ↓
Behavioral Analysis
     ↓
Model Training
     ↓
Risk Prediction
     ↓
FastAPI Backend
     ↓
React Frontend
🚀 Running the Project
Backend
cd backend
pip install -r ../requirements.txt
uvicorn main:app --reload
Frontend
cd frontend
npm install
npm run dev
🔍 Key Features
AI-based insider threat detection
Behavioral risk scoring
Suspicious activity detection
Real-time dashboard
Security alerts
Risk distribution
User risk analysis
Investigation management
Report generation
Machine learning prediction
🛠️ Technologies Used

Frontend: React, JavaScript, HTML, CSS

Backend: Python, FastAPI

Database: SQLite

Machine Learning: Scikit-learn, Pandas, NumPy

Development: Git, GitHub, VS Code

📈 Outcome

The completed system provides an integrated platform for analyzing employee behavior, identifying suspicious activities, calculating risk levels, and presenting security insights through an interactive dashboard.

👨‍💻 Author

Sunil M C

B.Tech Artificial Intelligence
SRM Institute of Science and Technology
