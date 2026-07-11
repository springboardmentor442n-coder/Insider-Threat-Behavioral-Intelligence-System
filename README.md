# Insider Threat Behavioral Intelligence System

A Machine Learning project developed as part of the **Infosys Springboard Internship** to analyze employee behavioral patterns and build a foundation for insider threat detection using the CERT Insider Threat Dataset v4.2.

---

## Project Overview

This project focuses on understanding employee logon behavior through data preprocessing, feature engineering, and exploratory data analysis (EDA). The processed dataset will be used in future milestones to train machine learning models capable of identifying suspicious insider activities.

---

## Milestone 1 Completed

### Dataset Research
- Studied the CERT Insider Threat Dataset v4.2
- Selected `logon.csv` for behavioral analysis

### Data Preprocessing
- Loaded the dataset
- Inspected dataset structure
- Checked data types
- Checked missing values
- Checked duplicate records
- Converted date column to datetime format

### Feature Engineering
The following features were created:

- `login_hour`
- `day`
- `month`
- `weekday`
- `is_after_hours`

### Exploratory Data Analysis (EDA)

The following analyses were completed:

- Logon vs Logoff Distribution
- Login Hour Distribution
- Working Hours vs After Hours
- Top Active Users
- Top Active Computers
- Hourly Employee Activity
- Weekday Activity Distribution

---

## Project Structure

```text
Insider-Threat-Behavioral-Intelligence-System/

backend/
datasets/
docs/
frontend/
ml/
notebooks/

README.md
requirements.txt
.gitignore
LICENSE
```

---

## Documentation

The project documentation is available in the `docs/` folder:

- `dataset_description.md`
- `feature_engineering.md`
- `eda_summary.md`

---

## Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- Jupyter / Kaggle Notebook
- Git
- GitHub

---

## Repository Contents

```
docs/
    dataset_description.md
    feature_engineering.md
    eda_summary.md

ml/
    preprocessing.py

notebooks/
    01_Data_Preprocessing.ipynb
```

---

## Current Status

| Task | Status |
|------|--------|
| Dataset Research | ✅ |
| Data Cleaning | ✅ |
| Feature Engineering | ✅ |
| Exploratory Data Analysis | ✅ |
| Machine Learning Model | ⏳ In Progress |
| Insider Threat Prediction | ⏳ Planned |

---

## Future Work

- Data Integration
- Machine Learning Model Training
- Insider Threat Classification
- Risk Score Prediction
- Explainable AI (XAI)
- Interactive Dashboard

---

## Author

**Sunil M C**

B.Tech Artificial Intelligence

SRM Institute of Science and Technology

Infosys Springboard Internship – 2026
