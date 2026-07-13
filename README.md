# Insider-Threat-Behavioral-Intelligence-System

A Machine Learning based Insider Threat Detection System using the **CERT Insider Threat Dataset (Release 4.2)**.

## Current Progress

Preprocessing Completed

- Dataset Understanding
- Data Cleaning
- Chunk-Based Processing
- Feature Engineering
- Feature Aggregation
- Threat Label Generation
- Employee Feature Dataset Creation

---

## Dataset

- CERT Insider Threat Dataset Release 4.2
- Source: https://www.kaggle.com/datasets/andrihjonior/cert-insider-threat-dataset-r4-2

---

## Project Structure

```
dataset/
└── processed/
    └── employee_features.csv

preprocessing/
├── aggregator.py
├── dataset_config.py
├── preprocess.py
├── login_processor.py
├── device_processor.py
├── file_processor.py
├── email_processor.py
├── http_processor.py
├── psychometric_processor.py
└── ldap_processor.py
```

---

## Preprocessing Workflow

```
Raw CERT Dataset
        ↓
Data Cleaning
        ↓
Chunk-Based Processing
        ↓
Feature Engineering
        ↓
Feature Aggregation
        ↓
Threat Label Assignment
        ↓
employee_features.csv
```

---

## Features Extracted

- Login Activity
- USB Activity
- File Activity
- Email Activity
- Web Activity
- Psychometric Scores
- Employee Information
- Threat Label

---

## Output

The preprocessing pipeline generates:

```
dataset/processed/employee_features.csv
```

- 1000 Employees
- 33 Features
- 70 Insider Users
- 930 Normal Users

---

## Technologies Used

- Python
- Pandas
- NumPy

---

## Next Steps

- Machine Learning Model Training
  
---

## Auth
**Mohmed Mohsin**
