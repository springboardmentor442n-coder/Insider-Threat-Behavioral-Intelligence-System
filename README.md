# Insider-Threat-Behavioral-Intelligence-System


# Project Overview

The "Insider Threat Behavioral Intelligence System "is an AI-driven platform designed to identify potential insider threats by analyzing employee behavioral activity logs. The system uses machine learning techniques to process organizational activity data, identify suspicious behavior patterns, and assist security teams in early threat detection.

# Problem Statement

Organizations generate a large volume of employee activity logs every day, including login records, emails, file access, USB device usage, web browsing, and organizational information. Detecting insider threats manually is difficult due to the scale and complexity of the data.

The objective of this project is to build an intelligent system that analyzes these behavioral logs and identifies anomalous user activities using Artificial Intelligence and Machine Learning.

# Project Objectives

- Analyze employee behavioral activity logs.
- Perform data preprocessing and cleaning.
- Build a unified behavioral dataset from multiple log sources.
- Apply Machine Learning techniques for insider threat detection.
- Generate employee risk scores.
- Provide a dashboard for monitoring suspicious activities.


# Dataset

 Dataset Used : CERT Insider Threat Dataset Version 4.2

 Primary Data Sources :
 - LDAP
 - Logon
 - Device
 - Email
 - File
 - HTTP
 - Psychometric

# Technology Stack

 Programming Language:
 - Python 3

 Data Processing:
 - Polars

 Backend:
 - FastAPI *(Planned for upcoming milestones)*

 Frontend :
- React.js *(Planned for upcoming milestones)*

 Database :
 - PostgreSQL *(Planned)*

## Version Control

- Git
- GitHub

## Development Environment

- Antigravity IDE
- Jupyter Notebook
- Kaggle Notebook (Dataset Exploration)

# Current Milestone (Week 1 & Week 2)

 Completed:
 - Repository initialization
 - GitHub branch setup
 - Technology stack selection
 - CERT v4.2 dataset study
 - Project architecture understanding
 
 In Progress :
 - Dataset exploration
 - Exploratory Data Analysis (EDA)
 - LDAP dataset analysis
 - Data preprocessing using Polars

Upcoming:
 - Cleaning all CERT datasets
 - Feature engineering
 - Dataset integration
 - Machine Learning model development


# Project Structure

Insider-Threat-Behavioral-Intelligence-System/
│
├── backend/
├── frontend/
├── datasets/
├── docs/
├── ml/
│   ├── notebooks/
│   ├── preprocessing/
│   ├── processed_data/
│   ├── models/
│   └── utils/
│
├── requirements.txt
├── README.md
└── LICENSE