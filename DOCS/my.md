# My Project Memory - Insider Threat Detection

## Project Identity
- **Name**: Insider Threat Detection System
- **Location**: D:\OPENCODE\insider-threat-detection
- **Dataset**: CMU CERT R6.2
- **Data Size**: ~93.3 GB
- **Users**: 4,000 employees + org structure
- **Time Period**: Dec 2009 - May 2011

## Complete Dataset Structure

### Raw Data (`DATA/raw/r6.2/r6.2/`)

| File | Rows | Fields | Description |
|------|------|--------|-------------|
| http.csv | **117,025,217** | id,date,user,pc,url,activity,content | Web browsing (largest file!) |
| email.csv | **10,994,958** | id,date,user,pc,to,cc,bcc,from,activity,size,attachments,content | Email communications |
| file.csv | **2,014,884** | id,date,user,pc,filename,activity,to_removable_media,from_removable_media,content | File operations (open/write/copy/delete) |
| logon.csv | **3,530,286** | id,date,user,pc,activity | Logon/Logoff events |
| device.csv | **1,551,829** | id,date,user,pc,file_tree,activity | USB device connect/disconnect |
| decoy_file.csv | **31,096** | decoy_filename,pc | Honeypot/decoy files |
| psychometric.csv | **4,001** | employee_name,user_id,O,C,E,A,N | Big 5 personality scores |
| LDAP/ | **18 files** | employee_name,user_id,email,role,projects,business_unit,functional_unit,department,team,supervisor | Monthly org snapshots (2009-12 to 2011-05) |

### Ground Truth (`DATA/raw/answers/`)
- `insiders.csv` - Master list of 192 insider instances
- `scenarios.txt` - 5 red team scenario descriptions
- Individual incident detail files (r*.csv) with interleaved observables

### Processed Data (`DATA/processed/`)
- `user_features.csv` - 4,001 users x 39 features
- `detection_results.csv` - Predictions (anomaly_pred, anomaly_score, threat_prob, threat_pred)
- `risk_scores.csv` - Risk scores (risk_score 0-100, severity: high/medium/low)

### Database
- `threat_detection.db` - SQLite database

## Data Source Details

### Logon Data
- Activity: Logon/Logoff only
- Screen unlocks recorded as logons; screen locks NOT recorded
- Some daily logons intentionally missing (simulated dirty data)
- After-hours logins are significant indicators
- 400 shared machines (lab-style) + assigned PCs
- ITAdmin role = sysadmin with global access

### Device Data
- USB thumb drive connect/disconnect events
- file_tree field: semicolon-delimited directory list
- Some disconnects missing (power down before removal)
- User's normal usage baseline varies; deviations are significant

### File Data
- Operations: File Open, File Write, File Copy, File Delete
- to_removable_media / from_removable_media flags
- Content: hex-encoded file header + keywords
- File headers same for all MS Office types
- Each user has normal daily file copy count; deviations significant

### Email Data
- Activity: Send/View
- Driven by friendship + organizational graphs
- Non-employees use non-DTAA addresses
- Terminated employees remain as eligible contacts
- Size and attachment count NOT correlated
- Multiple topics per message possible

### HTTP Data
- Activity: WWW Download, WWW Upload, WWW Visit
- URLs contain topic keywords
- WARNING: Most domain names randomly generated
- Modular/community structure but not correlated with email graph

### Psychometric Data (Big 5)
- O = Openness, C = Conscientiousness, E = Extroversion, A = Agreeableness, N = Neuroticism
- Extroversion drives friendship graph connections
- Conscientiousness drives late work arrivals
- Latent job satisfaction variable drives job searching + punctuality

### LDAP Data
- Monthly snapshots of organizational hierarchy
- business_unit > functional_unit > department > team > supervisor
- ITAdmin role identified as system administrators

## Insider Scenarios (5 Types)

| # | Description | Key Indicators |
|---|-------------|----------------|
| 1 | Data exfiltration via removable drives + wikileaks.org | Off-hours logon, thumb drive spike, data upload |
| 2 | Job hunting + competitor solicitation + data theft | Job websites, thumb drive spike before departure |
| 3 | Sysadmin disgruntled + keylogger + mass email | Keylogger download, thumb drive to supervisor PC |
| 4 | Unauthorized access + email to home (3 months) | Login to others' PCs, file search, home email |
| 5 | Layoff group member uploads to Dropbox | Document upload for personal gain |

## Important Users (R6.2 Insiders)

| Scenario | User | Dataset |
|----------|------|---------|
| S1 | ACM2278 | R6.2 |
| S2 | CMP2946 | R6.2 |
| S3 | PLJ1771 | R6.2 |
| S4 | CDE1846 | R6.2 |

## Feature Engineering Approach
- 39 behavioral features per user across all data sources
- **Logon features** (14): totals, ratios, temporal (off-hours, weekend, midnight)
- **File features** (12): operations, patterns, temporal
- **Email features** (8): volume, recipients, temporal, external
- **Device features** (3): totals, unique PCs, off-hours
- Cross-source ratio features for normalization

## Detection Approach
- Multi-model ensemble: Isolation Forest + XGBoost + LightGBM
- Anomaly score + classification probability
- Risk score: weighted combination -> severity mapping
- High (>=50), Medium (30-50), Low (<30)

## Known Issues
- http.csv alone is 117M rows - requires chunked/streaming processing
- Email content is dummy text (historical paragraphs, not real)
- Some dates have formatting issues (e.g., `/21/2011` missing month)
- Dense needle scenarios (4.2, 5.2) have many instances per scenario

## Configuration Notes
- Python 3.8+ required
- Key libraries: pandas, scikit-learn, xgboost, imbalanced-learn
- Memory management critical: http + email alone = 128M+ rows
- Consider Dask or Vaex for out-of-core processing

## Session History
- 2026-07-26: Initial project documentation created
  - Created requirements.txt, project_design.md, my.md, history.md
  - Discovered all data sources and their schemas
