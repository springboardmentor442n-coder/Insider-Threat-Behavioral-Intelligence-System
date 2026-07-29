# Insider Threat Behavioral Intelligence System

## Overview

The **Insider Threat Behavioral Intelligence System** is a Deep Learning-based cybersecurity project designed to identify and classify insider threats by analyzing employee behavioral patterns. The system utilizes the CERT Insider Threat Dataset and combines multiple organizational activity logs to detect suspicious behaviors that may indicate malicious insider actions.

Instead of relying on signature-based detection, this project performs **behavioral analytics**, extracting meaningful features from employee activities such as logon events, email communication, web browsing, file operations, USB device usage, and psychometric attributes. These features are then used to train a Multi-Layer Perceptron (MLP) neural network capable of classifying different categories of insider threats.

---

# Project Objectives

- Detect abnormal employee behavior using machine learning.
- Analyze multiple organizational data sources simultaneously.
- Classify different types of insider threats.
- Build an end-to-end behavioral analytics pipeline.
- Generate a reusable trained model for future predictions.

---

# Dataset

The project uses the **CERT Insider Threat Dataset**, which contains simulated enterprise user activities.

### Input Files

- **logon.csv** – User login and logout activities
- **email.csv** – Email communication records
- **http.csv** – Internet browsing history
- **file.csv** – File access and file transfer records
- **device.csv** – USB device connection activities
- **psychometric.csv** – Employee personality scores

---

# Workflow

## 1. Data Loading

The program imports all activity datasets into Pandas DataFrames.

Loaded datasets include:

- Logon activities
- Email records
- HTTP browsing logs
- File operations
- USB device activities
- Psychometric information

---

## 2. Feature Engineering

The raw activity logs are transformed into meaningful behavioral features.

### Logon Features

Examples:

- Number of unique computers used
- Total logons
- Total logoffs
- Weekend logins
- Weekday logins
- Most frequently used PC
- After-hours login count
- Office-hours login count

---

### Email Features

Examples:

- Number of unique recipients
- Average email size
- External emails sent
- Most contacted recipient
- Total email size

---

### HTTP Features

Examples:

- Unique websites visited
- Total web activities
- Number of upload activities
- Average URL length

---

### File Features

Examples:

- Unique files accessed
- USB file transfers
- Deleted files
- Copied files

---

### Device Features

Examples:

- Total USB activities
- After-hours USB usage
- Device disconnections

---

### Psychometric Features

Employee personality traits are included:

- Openness
- Conscientiousness
- Extraversion
- Agreeableness
- Neuroticism

---

# Feature Merging

All engineered features are merged into a single behavioral profile for each employee.

Missing values are handled using:

- Zero filling for activity counts
- Median imputation for numerical features

---

# Behavioral Label Generation

Instead of using manually labeled data, the project creates behavioral labels using deterministic organizational rules.

The following threat categories are generated:

| Label | Description |
|--------|-------------|
| Normal | Regular employee behavior |
| Intellectual Property Theft | Excessive file copying and unusual device usage |
| IT Sabotage | High deletion activity and abnormal device behavior |
| Unauthorized Access | Excessive after-hours logins and suspicious web activity |
| Data Exfiltration | Large external email communication and USB transfers |

---

# Data Preprocessing

The preprocessing pipeline includes:

- Label Encoding
- Missing value handling
- Standard Scaling
- Train/Test Split (80% / 20%)

---

# Deep Learning Model

The project uses a **Multi-Layer Perceptron (MLP)** implemented using **PyTorch**.

### Model Architecture

Input Layer

↓

Linear Layer (128 neurons)

↓

Batch Normalization

↓

ReLU Activation

↓

Dropout (30%)

↓

Linear Layer (64 neurons)

↓

Batch Normalization

↓

ReLU Activation

↓

Dropout (30%)

↓

Output Layer (5 Classes)

---

# Training Configuration

| Parameter | Value |
|-----------|-------|
| Framework | PyTorch |
| Optimizer | Adam |
| Learning Rate | 0.001 |
| Loss Function | CrossEntropyLoss |
| Epochs | 30 |
| Batch Size | 64 |

---

# Model Evaluation

The trained model is evaluated using:

- Classification Report
- Precision
- Recall
- F1 Score
- Validation Loss
- Training Loss

A loss convergence graph is also generated to monitor training performance.

---

# Saved Outputs

After training, the following files are generated:

| File | Purpose |
|------|----------|
| behavioral_intelligence_model.pth | Trained Deep Learning Model |
| pipeline_scaler.pkl | Feature Standardization |
| target_label_encoder.pkl | Threat Label Encoder |

These files can be reused during deployment for real-time insider threat prediction.

---
#reference notebook link
https://www.kaggle.com/code/goseh11/major-project
