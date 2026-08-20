**# 🛡️ Insider Threat Behavioral Intelligence System**

An AI-powered Insider Threat Detection System developed using **\*\*Machine Learning, FastAPI, and React\*\***. The system analyzes employee behavioral activities from the CERT Insider Threat Dataset and predicts whether an employee exhibits **\*\*NORMAL\*\*** or **\*\*INSIDER\*\*** behavior based on engineered behavioral features.

\<hr>

**# 📌 Project Overview**

The **\*\*Insider Threat Behavioral Intelligence System\*\*** was developed to identify suspicious employee behavior by analyzing organizational activity logs using Machine Learning.

Instead of directly developing the complete application, the project was implemented in multiple independent phases. Each module was completed, tested, and validated individually before integrating it with the remaining components.

The project implementation includes:

\- Data Preprocessing

\- Feature Engineering

\- Exploratory Data Analysis (EDA)

\- Machine Learning Model Development

\- Model Comparison

\- Model Evaluation

\- Real-Time Data Streaming

\- FastAPI Backend Development

\- REST API Implementation

\- Swagger API Testing

\- React Frontend Development

\- Frontend to Backend Integration

This modular implementation strategy improved maintainability, simplified debugging, and ensured that every module was verified before proceeding to the next implementation stage.

\<hr>

**# 🎯 Problem Statement**

Organizations generate a massive amount of employee activity logs every day, including login records, email communications, file access history, web browsing activity, and device usage.

Traditional security systems mainly depend on predefined rules and signatures, making it difficult to detect behavioral anomalies that evolve over time.

The objective of this project is to develop an intelligent behavioral analytics system capable of learning employee behavior patterns and identifying suspicious insider activities through Machine Learning.

\<hr>

**# 🎯 Project Objectives**

The major objectives of this project are:

\- Analyze employee behavioral activities from the CERT Insider Threat Dataset.

\- Clean and preprocess multiple behavioral datasets.

\- Generate meaningful behavioral features from raw activity logs.

\- Perform Exploratory Data Analysis before model training.

\- Develop anomaly detection models using Machine Learning.

\- Compare multiple anomaly detection algorithms.

\- Select the best-performing model for deployment.

\- Simulate continuous employee behavior through real-time streaming.

\- Develop REST APIs using FastAPI.

\- Integrate backend services with a React-based dashboard.

\- Provide real-time insider threat prediction through a user-friendly interface.

\<hr>

**# 📂 Dataset Description**

The project uses the **\*\*CERT Insider Threat Dataset Version 4.2\*\***, which contains employee behavioral activity collected from different organizational sources.

The datasets used during implementation include:

\- Device Activity Dataset

\- Email Activity Dataset

\- File Access Dataset

\- HTTP Browsing Dataset

\- Logon Activity Dataset

\- Psychometric (OCEAN) Dataset

Instead of merging all datasets directly, each dataset was cleaned and processed independently. After preprocessing, all employee activities were transformed into behavioral features that were later used for Machine Learning.

\<hr>

**# 🏗️ Project Architecture**

The application follows a modular architecture where each component performs a dedicated responsibility before passing its output to the next stage.

\`\`\`text

CERT Insider Threat Dataset

            │

            ▼

Data Preprocessing

            │

            ▼

Behavioral Feature Engineering

            │

            ▼

Exploratory Data Analysis

            │

            ▼

Machine Learning Model Development

            │

            ▼

Model Comparison and Evaluation

            │

            ▼

Real-Time Data Streaming

            │

            ▼

FastAPI Backend

            │

            ▼

REST API

            │

            ▼

React Frontend

            │

            ▼

Behavioral Intelligence Dashboard

\`\`\`

Each module was independently implemented and tested before integration.

\<hr>

**# 🔄 Project Workflow**

The complete implementation followed a structured development workflow.

\`\`\`text

CERT Dataset

↓

Data Cleaning

↓

Feature Engineering

↓

Exploratory Data Analysis

↓

Machine Learning Model Training

↓

Model Comparison

↓

Model Evaluation

↓

Real-Time Streaming

↓

FastAPI Backend

↓

Swagger API Testing

↓

React Frontend

↓

Frontend to Backend Integration

↓

Behavioral Intelligence Dashboard

\`\`\`

This workflow ensured that every implementation phase was successfully validated before moving to the next stage.

\<hr>

**# ⚙️ Implementation Strategy**

The project was implemented incrementally rather than building the complete system at once.

The implementation strategy followed throughout the project includes:

\- Creating a modular project structure.

\- Implementing preprocessing before Machine Learning.

\- Generating behavioral features from employee activity logs.

\- Performing Exploratory Data Analysis to understand the dataset.

\- Training both Isolation Forest and Local Outlier Factor models.

\- Comparing both models before deployment.

\- Selecting Isolation Forest as the deployment model.

\- Saving the trained model using Joblib.

\- Simulating real-time behavioral data through streaming.

\- Developing REST APIs using FastAPI.

\- Testing APIs using Swagger before frontend integration.

\- Building a React dashboard after backend validation.

\- Connecting React with FastAPI through REST APIs.

\- Validating predictions through the web interface.

The modular implementation approach reduced debugging complexity and simplified future enhancements.

\<hr>

\<hr>

**# 🧹 Data Preprocessing**

The preprocessing phase was implemented to clean, standardize, and prepare the CERT Insider Threat Dataset before feature generation.

Implementation steps:

\- Created a dedicated preprocessing module inside the **\*\*ml/preprocessing/\*\*** directory.

\- Processed each CERT dataset independently instead of combining them initially.

\- Cleaned the following datasets:

  - Device Activity

  - Email Activity

  - File Access

  - HTTP Browsing

  - Logon Activity

  - Psychometric (OCEAN)

\- Removed duplicate records.

\- Checked and handled missing values.

\- Standardized column names and data formats.

\- Verified data consistency before further processing.

\- Saved all cleaned datasets inside **\*\*datasets/processed/\*\*** for future use.

This modular preprocessing strategy reduced errors and simplified debugging during feature engineering.

\<hr>

**# ⚙️ Feature Engineering**

Feature Engineering was implemented to convert raw employee activity logs into meaningful behavioral indicators suitable for Machine Learning.

Instead of directly training on raw logs, behavioral features were generated for every employee.

The generated features include:

**### Employee Activity Features**

\- Device Connections

\- Emails Sent

\- Files Accessed

\- Websites Visited

\- Logon Count

**### Psychometric Features (OCEAN)**

\- Openness (O)

\- Conscientiousness (C)

\- Extraversion (E)

\- Agreeableness (A)

\- Neuroticism (N)

Implementation Strategy:

\- Aggregated employee activities using employee IDs.

\- Combined activity metrics with psychometric scores.

\- Generated one behavioral profile for each employee.

\- Saved the engineered dataset as:

\`\`\`

datasets/processed/final\_features.csv

\`\`\`

This engineered dataset became the primary input for all Machine Learning models.

\<hr>

**# 📊 Exploratory Data Analysis (EDA)**

Before training Machine Learning models, Exploratory Data Analysis was performed to understand employee behavioral patterns.

Implementation includes:

\- Dataset overview

\- Shape verification

\- Data type analysis

\- Missing value analysis

\- Statistical summary

\- Feature distribution visualization

\- Correlation analysis

\- Behavioral feature inspection

EDA helped verify that the engineered features were suitable for anomaly detection before model training.

\<hr>

**# 🤖 Machine Learning Model Development**

Since insider threat detection mainly involves identifying unusual behavioral patterns, unsupervised anomaly detection techniques were selected.

Two Machine Learning algorithms were implemented:

\- Isolation Forest

\- Local Outlier Factor (LOF)

Implementation Process:

\- Loaded the engineered behavioral dataset.

\- Selected numerical behavioral features.

\- Trained Isolation Forest.

\- Trained Local Outlier Factor.

\- Generated anomaly predictions.

\- Compared prediction outputs.

\- Saved the trained Isolation Forest model using Joblib.

The trained deployment model was stored inside:

\`\`\`

ml/models/isolation\_forest.pkl

\`\`\`

Saving the trained model eliminated the need for retraining during every prediction request, improving backend response time.

\<hr>

**# 🔍 Model Comparison**

Instead of directly deploying the first trained model, both anomaly detection algorithms were compared.

Models Compared:

\- Isolation Forest

\- Local Outlier Factor (LOF)

Comparison Parameters:

\- Number of detected anomalies

\- Prediction consistency

\- Behavioral classification

\- Deployment suitability

\- Prediction stability

Both models successfully detected abnormal behavioral patterns.

However, Isolation Forest demonstrated more stable predictions and better support for predicting unseen employee behavioral records.

Therefore, Isolation Forest was selected as the final deployment model for backend integration.

\<hr>

**# 📈 Model Evaluation**

A dedicated evaluation notebook was implemented to verify the performance of the trained Machine Learning models.

Implementation includes:

\- Loading engineered behavioral features.

\- Running predictions using Isolation Forest.

\- Running predictions using Local Outlier Factor.

\- Comparing anomaly detection counts.

\- Visualizing prediction distributions.

\- Validating model outputs.

\- Exporting evaluation results.

Generated output:

\`\`\`

datasets/processed/evaluation\_results.csv

\`\`\`

This evaluation phase confirmed that the selected deployment model performed consistently before backend integration.

\<hr>

**# 🌊 Behavioral Analysis

The application now provides a dedicated **Behavioral Analysis** module for analyzing employee behavior through both live and manual workflows.

## Live Data
---

The live analysis interface provides user-controlled monitoring.

Users can:

- Start live monitoring.
- Stop live monitoring.
- View the monitoring/connection state.
- Track records processed.
- Track normal behavior counts.
- Track anomalies detected.
- View the current employee being analyzed.
- View the latest prediction and risk information.

Live monitoring is started explicitly by the user rather than running continuously in the background.

## Manual Test
---

The manual test mode allows a user to provide behavioral feature values and request a prediction through the FastAPI backend.

```text
User Input
    ↓
Prediction Form
    ↓
FastAPI API
    ↓
Isolation Forest
    ↓
Prediction Result
```

## 📦 Batch Analysis
---

A dedicated **Batch Analysis** module supports analysis of multiple employee behavioral records.

```text
Multiple Records
      ↓
Preprocessing
      ↓
Feature Processing
      ↓
ML Prediction
      ↓
Batch Results
```

## 👤 Employee Analysis
---

The **Employees** module provides employee-focused analysis and connects employee information with behavioral prediction results.

## 📜 Prediction History
---

The **Prediction History** module keeps track of generated predictions and presents useful information such as employee ID, prediction, timestamp, risk/activity information, and analysis source.

## Result Presentation
---

The **ResultCard** component presents prediction and risk information in a clear dashboard format.

# 🚀 Backend Development**
---

The backend of the project was developed using **\*\*FastAPI\*\*** to expose the trained Machine Learning model as REST APIs.

A modular backend architecture was followed to improve maintainability and future scalability.

Backend folder structure:

\`\`\`

backend/

│

├── app/

│   ├── main.py

│   ├── routes.py

│   ├── predictor.py

│   ├── schemas.py

│   └── \_\_init\_\_.py

\`\`\`

Implementation Details:

\- Created FastAPI application.

\- Loaded the trained Isolation Forest model during server startup.

\- Separated prediction logic from routing.

\- Used Pydantic models for request validation.

\- Implemented JSON response handling.

\- Organized backend files into independent modules.

This modular architecture simplified debugging and future enhancements.

\<hr>

**# 🔗 REST API Implementation**

The Machine Learning model was exposed through REST APIs so that external applications could communicate with the prediction engine.

Implemented APIs:

**### Home API**

\`\`\`

GET /

\`\`\`

Returns API status.

Example Response

\`\`\`json

{

  "message": "Insider Threat Behavioral Intelligence System API is Running"

}

\`\`\`

**### Prediction API**

\`\`\`

POST /predict

\`\`\`

Receives employee behavioral features and returns prediction.

Input Features:

\- Device Connections

\- Emails Sent

\- Files Accessed

\- Websites Visited

\- Logon Count

\- Openness

\- Conscientiousness

\- Extraversion

\- Agreeableness

\- Neuroticism

Output

\`\`\`json

{

    "prediction":"NORMAL"

}

\`\`\`

or

\`\`\`json

{

    "prediction":"INSIDER"

}

\`\`\`

\<hr>

**# 🧪 API Testing (Swagger)**

After implementing the backend APIs, Swagger UI was used to validate every endpoint before frontend integration.

Swagger Features Used:

\- API Documentation

\- JSON Request Validation

\- API Response Validation

\- Prediction Testing

\- Error Handling Verification

Testing Process:

\- Started FastAPI server.

\- Opened Swagger Documentation.

\- Tested prediction endpoint.

\- Verified JSON request format.

\- Confirmed prediction response.

\- Validated backend functionality before React integration.

This ensured that backend services were functioning correctly before connecting the frontend.

\<hr>

**# 💻 Frontend Development

The frontend application was developed using **React + Vite** and redesigned as an interactive cybersecurity behavioral intelligence dashboard.

## Main Frontend Components
---

```text
frontend/src/components/

├── BatchAnalysis.jsx
├── BehaviorAnalysis.jsx
├── Employees.jsx
├── Login.jsx
├── Overview.jsx
├── PredictionForm.jsx
├── PredictionHistory.jsx
├── ResultCard.jsx
└── Sidebar.jsx
```

### 🧭 Dashboard Modules

- **Overview** — overall behavioral intelligence information.
- **Behavioral Analysis** — live and manual behavioral analysis.
- **Batch Analysis** — multiple-record prediction.
- **Employees** — employee-focused analysis.
- **Prediction Form** — manual behavioral feature input.
- **Prediction History** — previously generated prediction results.
- **Result Card** — prediction and risk presentation.
- **Sidebar** — dashboard navigation.

The frontend was designed to provide a clear workflow from behavioral input to Machine Learning prediction and result interpretation.

# 🔄 Frontend to Backend Integration
---

The frontend communicates with the FastAPI backend through the API service:

```text
User
 ↓
React Dashboard
 ↓
Prediction / Analysis Module
 ↓
frontend/src/services/api.js
 ↓
FastAPI Backend
 ↓
ML Predictor
 ↓
Isolation Forest
 ↓
Prediction
 ↓
Result Card / Prediction History
```

This provides an end-to-end prediction workflow from user input to Machine Learning result.

# 📁 Project Directory Structure
---

The current project follows a modular structure:

```text
Insider-Threat-Behavioral-Intelligence-System/
│
├── backend/
│   └── app/
│       ├── main.py
│       ├── predictor.py
│       └── routes.py
│
├── datasets/
│
├── docs/
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── BatchAnalysis.jsx
│   │   │   ├── BehaviorAnalysis.jsx
│   │   │   ├── Employees.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── Overview.jsx
│   │   │   ├── PredictionForm.jsx
│   │   │   ├── PredictionHistory.jsx
│   │   │   ├── ResultCard.jsx
│   │   │   └── Sidebar.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── ml/
│   ├── feature_engineering/
│   │   └── merge_features.py
│   ├── models/
│   │   ├── isolation_forest.pkl
│   │   └── retrain.py
│   └── preprocessing/
│       └── clean_data.py
│
├── clean_email.py
├── count_users.py
├── implementation_plan.md
├── README.md
└── LICENSE
```

# 🛠️ Technologies Used**
---

**### Programming Languages**

\- Python

\- JavaScript

**### 🤖 Machine Learning**

\- Scikit-learn

\- Pandas

\- NumPy

\- Joblib

**### Data Visualization**

\- Matplotlib

\- Seaborn

**### Backend**

\- FastAPI

\- Uvicorn

\- Pydantic

**### Frontend**

\- React

\- Vite

\- HTML

\- CSS

\- JavaScript

**### Development Tools**

\- Visual Studio Code

\- Git

\- GitHub

\- Swagger UI

**### 📂 Dataset**

\- CERT Insider Threat Dataset Version 4.2

\<hr>

**# 📋 Prerequisites

Before running the project, make sure the following software and tools are installed.

### Required Software

- **Python 3.x** — required for the Machine Learning pipeline and FastAPI backend.
- **Node.js and npm** — required for the React/Vite frontend.
- **Git** — required for cloning and managing the project repository.
- **A modern web browser** — required to use the dashboard.
- **A code editor** such as Visual Studio Code — recommended for development.

### Required Python Packages

The backend environment should include the packages required by the project, including:

- FastAPI
- Uvicorn
- Scikit-learn
- Pandas
- NumPy
- Joblib
- Python Multipart
- WebSockets

Install any project dependencies from the backend requirements file if your repository contains one.

### Required Frontend Packages

The frontend requires the packages declared in:

```text
frontend/package.json
```

Install them with:

```bash
cd frontend
npm install
```

### Environment Requirements

Before starting the application:

1. Make sure the trained model file is available.
2. Make sure the processed dataset files required by the project are present.
3. Make sure the backend and frontend use the expected local ports.
4. Start the backend before testing prediction features.
5. Start the frontend in a separate terminal.
6. For live monitoring, make sure the FastAPI WebSocket endpoint is available.

# ▶️ Running the Project**

Machine Learning

\- Run preprocessing scripts.

\- Generate behavioral features.

\- Train Machine Learning models.

\- Save trained model.

Backend

\`\`\`

uvicorn backend.app.main\:app --reload

\`\`\`

Swagger

\`\`\`

http\://127.0.0.1:8000/docs

\`\`\`

Frontend

\`\`\`

cd frontend

npm install

npm run dev

\`\`\`

Frontend URL

\`\`\`

http\://localhost:5173

\`\`\`

The complete application runs successfully after starting both the backend and frontend servers.

\<hr>

**# ⭐ Implementation Highlights

Major implementation achievements:

- Designed a modular project architecture.
- Cleaned and preprocessed multiple behavioral datasets.
- Generated behavioral features from employee activity logs.
- Performed Exploratory Data Analysis.
- Implemented Isolation Forest.
- Implemented Local Outlier Factor.
- Compared anomaly detection algorithms.
- Selected Isolation Forest for deployment.
- Saved the trained model using Joblib.
- Added model retraining support.
- Developed the FastAPI backend.
- Created REST APIs.
- Validated APIs using Swagger.
- Built a React + Vite behavioral intelligence dashboard.
- Implemented manual behavioral prediction.
- Implemented live behavioral analysis.
- Added Start/Stop live monitoring controls.
- Added Batch Analysis.
- Added Employee Analysis.
- Added Prediction History.
- Added prediction result and risk presentation.
- Connected frontend with backend.
- Organized the application into reusable React components.
- Improved the dashboard for cybersecurity behavioral monitoring.

# ⚠️ Challenges Faced**
---

Challenges encountered during development:

\- Cleaning multiple behavioral datasets.

\- Combining employee activity records.

\- Designing meaningful behavioral features.

\- Comparing multiple anomaly detection algorithms.

\- Integrating Machine Learning with FastAPI.

\- Validating APIs using Swagger.

\- Handling frontend-backend communication.

\- Resolving CORS issues.

\- Building a responsive dashboard.

\- Testing complete end-to-end prediction flow.

Each challenge was addressed through modular implementation and independent testing.

\<hr>

**# ✅ Conclusion**

The Insider Threat Behavioral Intelligence System was successfully developed as an end-to-end Machine Learning application capable of analyzing employee behavioral activities and predicting potential insider threats.

The project combines behavioral analytics, anomaly detection, REST APIs, and an interactive React dashboard into a unified system.

By following a modular implementation strategy, each component was independently developed, validated, and integrated, resulting in a scalable and maintainable application suitable for future enhancements such as database integration, live monitoring, authentication, and cloud deployment.

\<hr>
