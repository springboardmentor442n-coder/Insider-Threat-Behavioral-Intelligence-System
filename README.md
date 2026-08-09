# Insider-Threat-Behavioral-Intelligence-System

## 📌 Project Overview

The Insider Threat Behavioral Intelligence System is a machine learning-based application designed to identify potentially suspicious employee behavior by analyzing activities such as HTTP access, logons, device usage, file access, and email activity.

The system uses behavioral features extracted from user activity logs and a Random Forest Classifier to classify users as either **Normal Users** or **Potential Insider Threats**.

A Streamlit dashboard provides interactive predictions, confidence/probability information, and SHAP-based explanations of model predictions.

## 🎯 Objectives

- Analyze employee behavioral activity from multiple sources.
- Perform data preprocessing and feature engineering.
- Identify behavioral patterns associated with insider threats.
- Train a machine learning classification model.
- Provide prediction probabilities.
- Explain predictions using SHAP.
- Provide an interactive Streamlit dashboard.

## 📊 Dataset

This project uses the **CERT Insider Threat Dataset (Release 4.2)**.

The dataset contains user activity information including:

- HTTP activity
- Logon activity
- Device activity
- File activity
- Email activity

The original dataset is **not included in this repository** because of its large size.

## ⚙️ Features

The system creates behavioral features such as:

- HTTP Count
- Unique URLs
- After Hours Activity
- Weekend Activity
- Logon Count
- Unique PCs
- Device Count
- File Count
- Unique Files
- Email Count
- Unique Receivers
- Total Attachments

## 🤖 Machine Learning

A **Random Forest Classifier** is used for insider-threat classification.

The trained model is stored at:

```text
models/insider_threat_model.pkl
```
The model was evaluated using:

- Accuracy
- Precision
- Recall
- F1 Score
- Confusion Matrix
- Classification Report

## 🔍 Explainable AI

**SHAP (SHapley Additive exPlanations)** is used to explain model predictions and identify which behavioral features contribute to the prediction.

This helps make the system more interpretable instead of providing only a prediction.

## 🖥️ Streamlit Application

The Streamlit application allows users to:

1. Enter employee behavioral information.
2. Generate a risk prediction.
3. View the predicted category.
4. View confidence/probability.
5. View SHAP-based explanations.
6. Understand the important behavioral factors behind the prediction.

## 🛠️ Technologies Used

- Python
- Pandas
- NumPy
- Scikit-learn
- Random Forest
- SHAP
- Matplotlib
- Streamlit
- Joblib
- Jupyter Notebook

## 📁 Project Structure

```text
Insider-Threat-Behavioral-Intelligence-System/
│
├── models/
│   └── insider_threat_model.pkl
│
├── notebooks/
│   ├── 01-data-preprocessing.ipynb
│   └── 02-feature-engineering.ipynb
│
├── streamlit_app/
│   ├── app.py
│   ├── daily_features.csv
│   └── requirements.txt
│
├── docs/
├── outputs/
├── .gitignore
├── LICENSE
└── README.md
