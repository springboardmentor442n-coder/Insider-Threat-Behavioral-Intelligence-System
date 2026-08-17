# Insider Threat Detection System - Project Design

## Project Overview
This project implements an advanced insider threat detection system using the CMU CERT R6.2 dataset. The system analyzes user behavior patterns across **7 data sources** to identify potential insider threats through anomaly detection and behavioral classification.

## Dataset Information
- **Source**: CMU CERT R6.2 Dataset
- **Size**: ~93.3 GB raw data
- **Time Period**: Dec 2009 - May 2011 (18 months)
- **Users**: 4,000 employees + organizational hierarchy
- **Data Sources**: Logon, File, Email, HTTP, Device, Decoy, LDAP, Psychometric

### Data Scale

| Source | Records | Size Impact |
|--------|---------|-------------|
| http.csv | 117,025,217 | ~60% of dataset |
| email.csv | 10,994,958 | ~20% of dataset |
| file.csv | 2,014,884 | ~5% of dataset |
| logon.csv | 3,530,286 | ~5% of dataset |
| device.csv | 1,551,829 | ~3% of dataset |
| LDAP/ | 18 monthly snapshots | ~3% of dataset |
| decoy_file.csv | 31,096 | <1% |
| psychometric.csv | 4,001 | <1% |

## System Architecture

### 1. Data Pipeline
```
Raw Data (CSV, 93GB)
    │
    ├── Chunked Loading (Dask/Vaex)
    │
    ▼
Preprocessing
    ├── Deduplication
    ├── Timestamp normalization
    ├── User-PC mapping
    │
    ▼
Feature Engineering (39 features/user)
    ├── Logon features (14)
    ├── File features (12)
    ├── Email features (8)
    ├── Device features (3)
    │
    ▼
Label Generation (insiders.csv ground truth)
    │
    ▼
Model Training
    ├── Anomaly Detection (Isolation Forest)
    ├── Supervised Classification (XGBoost/LightGBM)
    │
    ▼
Risk Scoring & Severity Mapping
```

### 2. Data Source Schemas

#### logon.csv (3.5M rows)
- `id, date, user, pc, activity`
- Activity: Logon / Logoff
- Screen unlocks = logons; screen locks NOT recorded
- Some logons intentionally missing (dirty data simulation)
- 4,000 assigned PCs + 400 shared lab machines
- ITAdmin role = sysadmin with global access

#### device.csv (1.5M rows)
- `id, date, user, pc, file_tree, activity`
- Activity: Connect / Disconnect
- file_tree: semicolon-delimited directory list on USB
- Some disconnects missing (power down before removal)
- User baseline varies; deviations are significant

#### file.csv (2.0M rows)
- `id, date, user, pc, filename, activity, to_removable_media, from_removable_media, content`
- Activity: File Open, File Write, File Copy, File Delete
- Content: hex file header + keywords
- to/from_removable_media flags track data exfiltration

#### email.csv (11.0M rows)
- `id, date, user, pc, to, cc, bcc, from, activity, size, attachments, content`
- Activity: Send / View
- Driven by friendship graph + organizational graph
- Non-employees use non-DTAA addresses
- Terminated employees remain as eligible contacts

#### http.csv (117.0M rows)
- `id, date, user, pc, url, activity, content`
- Activity: WWW Download, WWW Upload, WWW Visit
- URLs contain topic keywords
- WARNING: most domain names randomly generated
- Content = space-separated keyword list

#### psychometric.csv (4,001 rows)
- `employee_name, user_id, O, C, E, A, N`
- Big 5 personality scores
- Extroversion → friendship graph connections
- Conscientiousness → late work arrivals
- Latent job satisfaction → job searching behavior

#### LDAP/ (18 monthly files: 2009-12 to 2011-05)
- `employee_name, user_id, email, role, projects, business_unit, functional_unit, department, team, supervisor`
- Organizational hierarchy: BU > FU > Dept > Team > Supervisor
- ITAdmin = system administrator role

#### decoy_file.csv (31,096 entries)
- `decoy_filename, pc`
- Honeypot files placed on machines
- Access to decoy files = suspicious behavior

### 3. Feature Categories (39 features)

#### Logon Features (14)
| Feature | Description |
|---------|-------------|
| logon_total | Total logon events |
| logon_count | Logon count |
| logoff_count | Logoff count |
| logon_logoff_ratio | Logon/logoff ratio |
| unique_pcs_logon | Unique PCs accessed |
| logon_off_hours | Off-hours logon count |
| logon_off_hours_ratio | Off-hours logon ratio |
| logon_weekend | Weekend logon count |
| logon_weekend_ratio | Weekend logon ratio |
| logon_unique_days | Unique active days |
| logon_avg_per_day | Average logons per day |
| logon_max_in_day | Max logons in a day |
| logon_after_midnight | After midnight logons |
| logon_total (base) | Base total |

#### File Features (12)
| Feature | Description |
|---------|-------------|
| file_total | Total file operations |
| file_unique_files | Unique files accessed |
| file_unique_pcs | Unique PCs for files |
| file_off_hours | Off-hours file ops |
| file_off_hours_ratio | Off-hours file ratio |
| file_weekend | Weekend file ops |
| file_weekend_ratio | Weekend file ratio |
| file_max_in_day | Max file ops in a day |
| file_unique_days | Unique active file days |
| file_file_open | File Open count |
| file_file_delete | File Delete count |
| file_file_copy | File Copy count |
| file_file_write | File Write count |

#### Email Features (8)
| Feature | Description |
|---------|-------------|
| email_total | Total email events |
| email_unique_recipients | Unique recipients |
| email_avg_size | Average email size |
| email_max_size | Max email size |
| email_with_attachments | Emails with attachments |
| email_off_hours | Off-hours emails |
| email_off_hours_ratio | Off-hours email ratio |
| email_unique_days | Unique email days |
| email_external | External email count |

#### Device Features (3)
| Feature | Description |
|---------|-------------|
| device_total | Total device events |
| device_unique_pcs | Unique PCs for device |
| device_off_hours | Off-hours device events |

### 4. Detection Methods

#### Anomaly Detection
- **Isolation Forest**: Unsupervised anomaly detection
- **One-Class SVM**: Boundary-based anomaly detection
- **Autoencoder**: Deep learning reconstruction error

#### Supervised Classification
- **Random Forest**: Ensemble-based classification
- **XGBoost**: Gradient boosting classifier
- **LightGBM**: Light gradient boosting machine

#### Risk Scoring
- Combined anomaly + classification scores
- Weighted ensemble approach
- Temporal risk escalation

### 5. Red Team Scenarios (Ground Truth)

| Scenario | Description | Key Indicators |
|----------|-------------|----------------|
| 1 | Data exfiltration via removable drives + wikileaks.org | Off-hours logon, thumb drive spike, data upload |
| 2 | Job hunting + competitor solicitation + data theft | Job websites, thumb drive spike before departure |
| 3 | Sysadmin disgruntled + keylogger + mass email | Keylogger download, thumb drive to supervisor PC |
| 4 | Unauthorized access + email to home (3 months) | Login to others' PCs, file search, home email |
| 5 | Layoff group member uploads to Dropbox | Document upload for personal gain |

## Model Performance Metrics
- Precision, Recall, F1-Score
- AUC-ROC Curve
- False Positive Rate
- Detection Rate at various thresholds
- Confusion Matrix

## Output Files
- `user_features.csv`: 4,001 users x 39 engineered features
- `detection_results.csv`: Model predictions (anomaly_pred, anomaly_score, threat_prob, threat_pred)
- `risk_scores.csv`: Risk assessment (risk_score 0-100, severity: high/medium/low)

## Risk Severity Levels
- **High**: Score ≥ 50 → Immediate investigation required
- **Medium**: Score 30-50 → Monitor closely
- **Low**: Score < 30 → Normal activity

## Future Enhancements
1. **Streaming Pipeline**: Process 117M http rows with Dask/Spark
2. **Graph Analysis**: Email/organizational relationship graphs
3. **NLP**: Email content analysis for sentiment/topics
4. **Temporal LSTM**: Sequential pattern detection
5. **Explainable AI**: SHAP values for alert justification
6. **Real-time Dashboard**: Live risk monitoring
7. **LDAP Integration**: Role-based anomaly context
