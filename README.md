# Insider-Threat-Behavioral-Intelligence-System

# Insider Threat Behavioral Intelligence System

## Dataset

**CERT r4.2 Insider Threat Dataset** ([Kaggle](https://www.kaggle.com/datasets/andrihjonior/cert-insider-threat-dataset-r4-2))

| File | Description | Rows |
|---|---|---|
| `logon.csv` | Logon/logoff events | ~855K |
| `device.csv` | USB connect/disconnect events | ~405K |
| `http.csv` | Web browsing activity | ~28.4M |
| `email.csv` | Email metadata and content | ~2.6M |
| `file.csv` | File copies to removable media | ~446K |
| `psychometric.csv` | Big-5 personality scores per employee | 1,000 |
| `LDAP/*.csv` | Monthly employee org snapshots | 18 files |
| `answers/insiders.csv` | Ground-truth malicious insiders (multi-release) |

The dataset spans **1,000 users** from **Jan 2010 to May 2011** and includes 3 known insider threat scenarios (in `answers/r4.2-1/`, `r4.2-2/`, `r4.2-3/`).

## What's in this notebook

`data-preprocessing-insider-threat-dectection.ipynb
` performs the EDA phase of Milestone 1:

- Loads all core log files using **Polars' lazy API** (`pl.scan_csv`) for memory-efficient processing on large files (esp. `http.csv` at 28M+ rows)
- Schema inspection, null/duplicate checks, and datetime parsing across all files
- Unique user counts per data source
- Behavioral pattern analysis: logon hour/day-of-week distribution, after-hours and weekend activity flags
- USB device usage patterns, email recipient/attachment analysis, file extension breakdown
- Top domain analysis from HTTP logs
- Merges 18 monthly LDAP snapshots into a unified employee identity table
- Cross-validates activity-log users against LDAP records
- Loads ground-truth insider labels and scenario descriptions for future model evaluation

## Tech Stack

- **Language:** Python 3.12
- **Data processing:** Polars (lazy/streaming engine, chosen for RAM efficiency over pandas)
- **Visualization:** Matplotlib, Seaborn
- **Environment:** Kaggle Notebooks

## How to Run

1. Attach the [CERT r4.2 dataset](https://www.kaggle.com/datasets/andrihjonior/cert-insider-threat-dataset-r4-2) to a Kaggle notebook
2. Run all cells top-to-bottom (Kaggle notebooks don't persist variables across sessions)
3. Update `BASE` path if your dataset mount path differs

[Benarji-chowdary] — built as part of a mentored insider threat detection project.
