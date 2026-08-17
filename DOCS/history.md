# Project History - Insider Threat Detection

## Timeline

### 2026-07-26 - Project Initialization

#### Initial Setup
- Working directory: D:\OPENCODE\insider-threat-detection
- Git repository initialized (no commits yet)
- Dataset discovered: CMU CERT R6.2 (~93.3 GB)

---

#### Complete Data Discovery

**Raw Data** (`DATA/raw/r6.2/r6.2/`):

| File | Rows | Fields | Notes |
|------|------|--------|-------|
| http.csv | **117,025,217** | id,date,user,pc,url,activity,content | LARGEST file (~60% of dataset) |
| email.csv | **10,994,958** | id,date,user,pc,to,cc,bcc,from,activity,size,attachments,content | ~20% of dataset |
| logon.csv | **3,530,286** | id,date,user,pc,activity | Logon/Logoff events |
| file.csv | **2,014,884** | id,date,user,pc,filename,activity,to_removable_media,from_removable_media,content | File ops |
| device.csv | **1,551,829** | id,date,user,pc,file_tree,activity | USB connect/disconnect |
| decoy_file.csv | **31,096** | decoy_filename,pc | Honeypot files |
| psychometric.csv | **4,001** | employee_name,user_id,O,C,E,A,N | Big 5 personality |
| LDAP/ | **18 files** | employee_name,user_id,email,role,projects,business_unit,functional_unit,department,team,supervisor | Monthly org snapshots (2009-12 to 2011-05) |

**Ground Truth** (`DATA/raw/answers/`):
- `insiders.csv` - 192 insider instances across all CERT releases
- `scenarios.txt` - 5 red team scenario descriptions
- Individual incident detail files (r*.csv)

**Processed Data** (`DATA/processed/`):
- `user_features.csv` - 4,001 users x 39 features
- `detection_results.csv` - Predictions with anomaly/classification scores
- `risk_scores.csv` - Risk scores (0-100) with severity mapping

**Other**:
- `DATA/threat_detection.db` - SQLite database

---

#### Key Data Source Details Learned

**Logon**: Screen unlocks=logons, screen locks NOT recorded. Some intentionally missing. After-hours significant. 4k assigned PCs + 400 shared. ITAdmin=global access.

**Device**: USB thumb drives. file_tree=semicolon-delimited dirs. Some disconnects missing.

**File**: Open/Write/Copy/Delete operations. to_removable_media/from_removable_media flags. Hex headers correlate with file extensions.

**Email**: Send/View. Friendship graph + organizational graph. Non-employees use non-DTAA addresses. Terminated employees still contactable.

**HTTP**: WWW Download/Upload/Visit. Most domains randomly generated. URL words relate to page topic.

**Psychometric**: Big 5 (O,C,E,A,N). Extroversion→connections. Conscientiousness→lateness. Latent job satisfaction→job search.

**LDAP**: Hierarchical org: BU > FU > Dept > Team > Supervisor.

---

#### Documentation Created
1. `requirements.txt` - Python dependencies (18 packages)
2. `project_design.md` - Complete system architecture with data schemas
3. `my.md` - Comprehensive project memory
4. `history.md` - This file

---

## Project Statistics

### Dataset Overview
| Metric | Value |
|--------|-------|
| Total Users | 4,000 |
| Total Raw Records | ~138M rows |
| Largest Source | http.csv (117M rows) |
| Email Records | 11M rows |
| Insider Instances | 192 (across all releases) |
| R6.2 Insiders | 4 unique users |
| Time Period | Dec 2009 - May 2011 |
| Data Size | ~93.3 GB |

### Feature Categories
- **Logon**: 14 features (totals, ratios, temporal patterns)
- **File**: 13 features (operations, patterns, temporal)
- **Email**: 9 features (volume, recipients, temporal)
- **Device**: 3 features (usage patterns)
- **Total**: 39+ behavioral features per user

### Red Team Scenarios (R6.2)
| Scenario | Users | Description |
|----------|-------|-------------|
| 1 | ACM2278 | Data exfiltration via removable drives + wikileaks |
| 2 | CMP2946 | Job hunting + competitor data theft |
| 3 | PLJ1771 | Keylogger + privilege escalation |
| 4 | CDE1846 | Unauthorized access + data hoarding (3 months) |

---

## Key Discoveries

### Data Quality Notes
- http.csv is 117M rows - needs Dask/Spark for processing
- Email content contains dummy text (historical paragraphs, not real content)
- Some dates have formatting issues (e.g., `/21/2011` in insiders.csv line 191)
- "Dense needle" scenarios (4.2, 5.2) have many instances per scenario type
- Email size and attachment count NOT correlated with each other

### Processing Requirements
- Must use chunked/streaming processing for http.csv and email.csv
- Consider Dask or Vaex for out-of-core dataframe operations
- Memory management is critical
- LDAP data changes over time - need temporal alignment

### Risk Score Analysis
- Highest risk users: ACM2278 (61.83), CMP2946 (56.81), PLJ1771 (54.61), CDE1846 (45.27)
- Risk score formula combines anomaly_pred, anomaly_score, threat_prob, threat_pred
- Severity: high (>=50), medium (30-50), low (<30)

---

## Files Created This Session
1. `requirements.txt` - Python dependencies
2. `project_design.md` - System architecture (updated with all schemas)
3. `my.md` - Project memory (comprehensive)
4. `history.md` - This file

---

## Next Steps (Potential)
1. Implement chunked data loading pipeline for 93GB dataset
2. Feature engineering optimization with all 39 features
3. Model training and cross-validation
4. Real-time streaming detection system
5. Visualization dashboard
6. Explainable AI integration (SHAP)
7. Graph-based email/relationship analysis
8. Temporal analysis with LDAP snapshots

---

## Notes for Future Sessions
- **CRITICAL**: http.csv is 117M rows - always process in chunks
- Always check `DATA/raw/answers/insiders.csv` for ground truth
- Key users to validate: ACM2278, CMP2946, PLJ1771, CDE1846
- LDAP has 18 monthly snapshots - org structure changes over time
- Psychometric data is available but not used in current features
- Decoy file access is a strong indicator of suspicious behavior
- ITAdmin role users have global access - factor into risk scoring

---

## CRITICAL WORKFLOW RULES

### Rule 1: ALWAYS Log Work to history.md
- Every task, change, or decision MUST be logged in this file
- If stuck or confused, CHECK history.md FIRST
- If hallucinating or uncertain, CHECK history.md FIRST
- This file is the single source of truth for project state

### Rule 2: Environment Files
- `.env` - Contains all project configuration (paths, parameters, dataset info)
- `.env.example` - Template for new setups
- `.gitignore` should exclude `.env` but track `.env.example`

### Rule 3: Directory Structure
```
insider-threat-detection/
├── .env                  # Environment config (local, not committed)
├── .env.example          # Environment template (committed)
├── history.md            # ALWAYS LOG HERE - single source of truth
├── my.md                 # Project memory
├── project_design.md     # Architecture documentation
├── requirements.txt      # Python dependencies
├── DATA/                 # All data files
│   ├── raw/              # Original dataset
│   ├── processed/        # Engineered features
│   ├── threat_detection.db
│   ├── OUTPUT/           # Generated outputs, plots, reports
│   ├── LOGS/             # Execution logs
│   ├── MODELS/           # Saved model artifacts
│   └── DOCS/             # Additional documentation
└── .git/                 # Version control
```

---

## Environment Setup Notes
- Created `.env` with all project paths and parameters
- Created `.env.example` as template
- Created `.gitignore` to exclude .env, __pycache__, models, logs
- Created directories: OUTPUT, LOGS, MODELS, DOCS

---

## CRITICAL WORKFLOW RULES (MANDATORY)

### Rule 1: ALWAYS Log Work to history.md
- Every task, change, or decision MUST be logged in this file
- If stuck or confused, CHECK history.md FIRST
- If hallucinating or uncertain, CHECK history.md FIRST
- This file is the single source of truth for project state
- Format: `### YYYY-MM-DD - Task Description`

### Rule 2: Environment Files
- `.env` - Contains all project configuration (paths, parameters, dataset info)
- `.env.example` - Template for new setups
- `.gitignore` excludes `.env` but tracks `.env.example`

### Rule 3: Directory Structure
```
INSIDER-THREAT-DETECTION/
│
├── DATA/
│   ├── raw/                    # Original CMU CERT R6.2 dataset
│   ├── processed/              # Cleaned and transformed data
│   ├── features/               # Engineered features
│   └── threat_detection.db     # SQLite database
│
├── NOTEBOOKS/                  # Jupyter notebooks for exploration
│
├── SRC/
│   ├── preprocessing/          # Data loading and cleaning
│   ├── feature_engineering/    # Feature creation and selection
│   ├── models/                 # ML model implementations
│   ├── evaluation/             # Model evaluation metrics
│   ├── dashboard/              # Visualization and reporting
│   └── utils/                  # Shared utilities
│
├── MODELS/                     # Saved model artifacts
│
├── OUTPUT/
│   ├── reports/                # Generated reports
│   ├── graphs/                 # Visualization plots
│   └── predictions/            # Model predictions
│
├── LOGS/                       # Application logs
│
├── DOCS/                       # Project documentation
│
├── tests/                      # Unit and integration tests
│
├── app.py                      # Main application entry point
├── train.py                    # Model training script
├── requirements.txt            # Python dependencies
├── README.md                   # Project readme
└── .gitignore                  # Git ignore rules
```

---

## Environment Setup Notes
- Created `.env` with all project paths and parameters
- Created `.env.example` as template
- Created `.gitignore` to exclude .env, __pycache__, models, logs, data
- Created all directories with .gitkeep files for empty dirs
- Moved documentation to DOCS/ folder
- Created utility modules in SRC/utils/

---

### 2026-07-26 - Project Restructuring

#### New Directory Structure Implemented
```
INSIDER-THREAT-DETECTION/
├── DATA/
│   ├── raw/                    # Original CMU CERT R6.2 dataset
│   ├── processed/              # Cleaned and transformed data
│   ├── features/               # Engineered features
│   └── threat_detection.db     # SQLite database
├── NOTEBOOKS/                  # Jupyter notebooks
├── SRC/
│   ├── preprocessing/          # Data loading and cleaning
│   ├── feature_engineering/    # Feature creation
│   ├── models/                 # ML models
│   ├── evaluation/             # Metrics
│   ├── dashboard/              # Visualization
│   └── utils/                  # Shared utilities
├── MODELS/                     # Saved model artifacts
├── OUTPUT/
│   ├── reports/                # Generated reports
│   ├── graphs/                 # Visualization plots
│   └── predictions/            # Model predictions
├── LOGS/                       # Application logs
├── DOCS/                       # Project documentation
├── tests/                      # Unit and integration tests
├── app.py                      # Main application entry
├── train.py                    # Model training script
├── requirements.txt            # Python dependencies
├── README.md                   # Project readme
└── .gitignore                  # Git ignore rules
```

#### Files Created
- `app.py` - Main application entry point
- `train.py` - Model training script
- `README.md` - Project documentation
- `SRC/utils/config.py` - Configuration utilities
- `SRC/utils/logger.py` - Logging utilities
- `SRC/__init__.py` and all subdirectory `__init__.py` files
- `.gitkeep` files for empty directories

#### Files Moved
- `project_design.md` → `DOCS/project_design.md`
- `my.md` → `DOCS/my.md`
- `history.md` → `DOCS/history.md`

#### Directory Renames
- `DATA/raw/r6.2/r6.2/` → `DATA/raw/CERT_R6.2/data/`
- Removed unnecessary nested folder

#### Updated
- `.gitignore` - Now excludes DATA/raw, DATA/processed, OUTPUT/*, MODELS/*, LOGS/*
- Directory structure documented in history.md

---

### 2026-07-26 - Created Setup Guide

#### New File Created
- `DOCS/guide.txt` - Complete guide explaining everything done

#### Contents
- What the project is
- Step-by-step explanation of all work
- What each file does
- Important facts to remember
- How to recreate the structure yourself

---

### 2026-08-02 - Completed 13_Model_Interpretation.ipynb

#### Task
Complete notebook 13 (Model Interpretation / Explainability).

#### What Was Done
- Rebuilt `NOTEBOOKS/13_Model_Interpretation.ipynb` (51 cells:
  27 markdown + 24 code, executed, 0 errors)
- Every step has a markdown cell explaining it
- Content per user spec:
  - Part A/B (0-14): title/intro, imports, load dataset +
    restore feature names, load RF model, predictions,
    dataset info (799 normal / 1 insider), prediction
    distribution + viz, interpretation
  - Part C (15-30): RF feature importance -> top 20 -> chart ->
    top 10 -> save feature_importance.csv -> key findings ->
    ranking summary -> top 5 print
  - Part D (31-45): permutation importance (n_repeats=10,
    scoring=accuracy) -> perm_df -> top 20 -> chart ->
    compare vs RF importance -> save permutation_importance.csv
    -> interpretation
  - Part E (46-66): individual prediction analysis ->
    prediction_df (actual/predicted + probabilities) ->
    prediction distribution -> probability histogram ->
    top risk ranking -> top 10 high risk -> bar chart ->
    model confidence describe -> confidence histogram ->
    low confidence predictions -> save prediction_analysis.csv
    -> interpretation
  - Part F (67-81): misclassified employee analysis ->
    misclassified df -> stats (1 of 800) -> error rate 0.12%
    -> pie chart -> highest-error employees ->
    save misclassified_employees.csv -> interpretation
    (1 error = the insider predicted normal, a false negative)
  - Part G (82-89): explainability summary -> top 10 RF +
    permutation features -> prediction summary
    (800/799/1, 99.88% acc) -> save explainability_summary.csv
    -> overall findings -> final explainability report ->
    conclusion
  - Confusion matrix | classification report
  - Part H (94-104): SHAP (optional, added - numba/numpy fix
    makes shap 0.52.0 work) -> TreeExplainer -> shap_values
    (800, 47) class 1, expected 0.4998 -> beeswarm summary plot
    -> global bar plot -> top 10 mean |SHAP| ->
    save shap_importance.csv -> waterfall plot for highest-risk
    employee (idx 350, prob 0.19) -> SHAP interpretation
  - Conclusion

#### Key Fixes
- Fixed numba/NumPy conflict: env now numpy 2.4.6 / numba 0.66.0 / shap 0.52.0
- Model trained with numeric column names (0..46); after renaming X_test to
  real feature names, set `random_forest.feature_names_in_` so predict works.
- Removed redundant early permutation-importance section once user's Part D
  was added (avoid duplicate outputs).

#### Verified
- Top 5: working_days (0.1431), http_download_count (0.1238),
  http_upload_count (0.0977), after_hours_device_events (0.0888),
  files_to_removable_media (0.0803)
- Permutation importance all 0.0 (test set always predicted normal)
- Part E: highest insider probability 0.19 (employee 350),
  model confidence mean 0.9989, min 0.81
- Part F: 1 misclassified employee (insider -> false negative),
  error rate 0.12%
- Part G: prediction summary 800/799/1, accuracy 99.88%,
  final explainability report printed
- Part H (SHAP): TreeExplainer -> shap_values (800,47),
  expected 0.4998; top 5 mean |SHAP| match RF importance
  (working_days, http_download_count, http_upload_count,
  after_hours_device_events, files_to_removable_media);
  waterfall for employee 350 (insider prob 0.19)

#### Files
- `NOTEBOOKS/13_Model_Interpretation.ipynb` (106 cells: 56 md + 50 code)
- `DATA/processed/feature_importance.csv` (regenerated)
- `DATA/processed/permutation_importance.csv` (regenerated)
- `DATA/processed/prediction_analysis.csv` (new, Part E)
- `DATA/processed/misclassified_employees.csv` (new, Part F)
- `DATA/processed/explainability_summary.csv` (new, Part G)
- `DATA/processed/shap_importance.csv` (new, Part H)
- `DOCS/guide.txt` (Step 13 plan + implementation notes)

---

### 2026-08-02 - Started 14_Streamlit_Deployment.ipynb (Batch 1)

#### Task
Create Notebook 14 - a Streamlit Insider Threat Detection Dashboard.
This batch: project structure, empty app files, verify model + features.

#### What Was Done
- Created `NOTEBOOKS/14_Streamlit_Deployment.ipynb` (16 cells:
  8 markdown + 8 code, executed, 0 errors)
- Created `STREAMLIT/` folder + `STREAMLIT/assets/`
- Created empty files: `app.py`, `predict.py`, `utils.py`,
  `style.css`, `requirements.txt`
- Verified `MODELS/`: decision_tree.pkl, logistic_regression.pkl,
  random_forest_model.pkl (+ .gitkeep)
- Loaded RF: RandomForestClassifier(class_weight='balanced',
  random_state=42)
- Verified 47 features from labeled_dataset.csv (drop user, label)

#### Notes
- Old `NOTEBOOKS/14_Model_Deployment.ipynb` is an EMPTY placeholder
  (invalid JSON) - still present, not deleted (pending user decision)
- MODELS listing also shows `.gitkeep` (benign vs sample output)
- iterdir order is alphabetical (benign vs sample output)

#### Files
- `NOTEBOOKS/14_Streamlit_Deployment.ipynb` (new, Batch 1)
- `STREAMLIT/` + `assets/` + 5 empty app files (new)
- `DOCS/guide.txt` (Step 14 plan + Batch 1 notes)

---

### 2026-08-02 - Notebook 14 Batch 2 (Part B - app.py)

#### Task
Generate the complete `app.py` Streamlit application from
inside Notebook 14 (code cell writes the file).

#### What Was Done
- Notebook now 22 cells (11 md + 11 code), executed, 0 errors
- Cell 17 defines `app_code` = full Streamlit app
  (page config, load RF model + feature names, sidebar nav,
  Home / Single Prediction / Batch Prediction / About pages)
- Cells 19/21 write and verify `STREAMLIT/app.py` ->
  "app.py Created Successfully", exists() = True
- app.py syntax-validated (py_compile), ~2.1 KB UTF-8

#### Encoding Fix (important)
- Emoji (🛡️, •) typed directly in commands get corrupted by
  the PowerShell 5.1 codepage before reaching Python.
- Workaround: pass ASCII escapes (\U0001F6E1\uFE0F, \u2022),
  convert to real unicode in-memory in Python, then write the
  notebook JSON / app.py as UTF-8. Notebook cell and app.py
  now both contain correct emoji.
- PowerShell Get-Content misdisplays UTF-8 emoji; always
  verify with Python.

#### Files
- `NOTEBOOKS/14_Streamlit_Deployment.ipynb` (22 cells)
- `STREAMLIT/app.py` (real content, Batch 2)
- `DOCS/guide.txt` (Batch 2 notes)

---

### 2026-08-02 - Notebook 14 Batch 3 (app.py - Single Prediction)

#### Task
Make `app.py` functional: full single-employee prediction
form. Changed DIRECTLY in the file (not via notebook) per
user's decision - notebook only creates the app files.

#### What Was Done
- Replaced the Single Prediction placeholder with:
  - 47 number_input widgets in a 2-column grid
  - "Predict Insider Threat" button
  - model.predict + predict_proba on a 1x47 DataFrame
  - result: st.error "⚠ Insider Threat Detected" /
    st.success "✅ Normal Employee"
  - Normal / Insider probabilities (4 decimals)
- Emoji stored correctly as UTF-8 (👤 ⚠ ✅)

#### Verified
- py_compile -> syntax OK
- streamlit run smoke test -> server started on port 8502,
  model + features loaded, no errors (killed after 25s)
- Note: predict() is positional, so numeric column names
  from training are not a problem.

#### Files
- `STREAMLIT/app.py` (Single Prediction functional)
- `DOCS/guide.txt` (Batch 3 notes)

---

### 2026-08-02 - Notebook 14 Batch 4 (app.py - Batch Prediction)

#### Task
Add CSV upload batch prediction to `app.py`.

#### What Was Done
- Batch Prediction page: file_uploader + preview + Run button
- Column validation (missing features -> st.error; else run)
- predictions + probabilities + Risk Level
  (🟢 Low < 0.30 / 🟡 Medium < 0.70 / 🔴 High)
- results table + download_button (CSV)
- Validation and prediction code nested inside else so it
  runs only on valid input (avoids NameError crash)

#### Critical Bug Fix
- sklearn validates feature names on predict/predict_proba;
  model trained with numeric columns (0..46) -> crash with
  real feature names on BOTH prediction pages
- Fixed: `model.feature_names_in_ = np.asarray(feature_names)`
  after loading feature names (+ `import numpy as np`)
- Not caught by smoke tests (server start doesn't run the
  button-click code); caught by headless logic simulation

#### Verified
- py_compile OK; positive path predicts fine (all Low on
  normal X_test); negative path (numeric columns) correctly
  reports missing columns; smoke test server started OK

#### Files
- `STREAMLIT/app.py` (Batch Prediction functional)
- `DOCS/guide.txt` (Batch 4 notes)

---

### 2026-08-02 - Notebook 14 Batch 5 (app.py - Home Dashboard)

#### Task
Turn the Home page into a professional analytics dashboard.

#### What Was Done
- Replaced Home section with:
  - title + welcome text
  - 3 metric cards (Model / Features / Dataset)
  - Project Overview (behavioural data categories)
  - Project Workflow table (6 steps)
  - Model Information table (RF, 3200/800 samples, 47 features)
  - Dataset Distribution bar chart (3995 normal / 5 insider)
  - Feature Categories table (6 categories)
  - Technologies Used table
  - footer caption
- All tables/dataframes use real data consistent with the
  project (5 insiders, 47 features).

#### Verified (streamlit AppTest)
- HOME/SINGLE/BATCH/ABOUT all render with 0 exceptions
- HOME: 3 metrics, 6 subheaders, 4 tables, bar chart, caption
- SINGLE: 47 number_inputs; predict click works (all-zero ->
  insider 0.51 -> st.error shown, correct model behaviour)
- BATCH: file_uploader present
- Server starts cleanly
- Benign pyarrow auto-fix warning from mixed-type model_info
  "Value" column (displays fine)

#### Files
- `STREAMLIT/app.py` (Home dashboard, Part E)
- `DOCS/guide.txt` (Batch 5 notes)

---

### 2026-08-02 - Notebook 14 Batch 6 (app.py - Part F, UI polish)

#### Task
Professional prediction results + risk analysis in the app.

#### What Was Done
- Single Prediction result section upgraded:
  - 2-col result: Insider/Normal + LOW/MEDIUM/HIGH risk
  - progress bar (insider probability)
  - Normal/Insider probability metric cards (%)
  - Employee Summary dataframe (feature/value)
  - automated Recommendation (normal / monitor / investigate)
- Batch Prediction upgraded after results table:
  - Prediction Summary metrics (Employees/Normal/Insiders +
    Low/Medium/High counts)
  - risk distribution bar chart
  - prediction (Normal/Insider) bar chart
  - Highest Risk Employees top-10 table
  - download button with keyword args + ⬇ label

#### Verified (streamlit AppTest, full interaction)
- SINGLE: 0 exceptions; zero-input -> insider 0.51 ->
  🔴 alert + 🟡 MEDIUM RISK + "should be monitored",
  progress + metrics 49/51% + employee summary df
- BATCH: 0 exceptions; simulated CSV upload (8 rows) ->
  success, metrics 8/8/0 + 8/0/0, 2 bar charts, top-10 df
  (8x51), download button present
- AppTest file_uploader: set_value(("name", bytes, mime))

#### Files
- `STREAMLIT/app.py` (Part F complete)
- `DOCS/guide.txt` (Batch 6 notes)

---

### 2026-08-02 - Notebook 14 Batch 7 (Parts G-J, overwrite incident)

#### Task
About page (Part G) + requirements.txt / style.css / run
instructions (Parts H/I/J) in the notebook.

#### What Was Done
- Part G: replaced `st.title("About")` placeholder in
  `STREAMLIT/app.py` with full About page:
  - "ℹ️ About the Project" title
  - Project Overview text
  - Machine Learning Model table (RF, 3200/800, 47, CERT R6.2)
  - Project Workflow table (7 steps incl Explainable AI + Deployment)
  - Technologies Used table (7 items)
  - Project Highlights (6 st.success checkmarks)
  - caption "Developed as a B.Tech AI & ML Major Project"
- Parts H/I/J: appended notebook cells 22-27 that write
  `requirements.txt` (7 packages) and `style.css` (bg #f5f5f5,
  button radius, h1 #0E76A8) + print run instructions.
  All 28 cells executed, 0 errors, files verified on disk.

#### CRITICAL INCIDENT: notebook overwrote app.py
- Executing notebook 14 re-ran cell 19 which WRITES the stale
  cell-17 `app_code` string over `STREAMLIT/app.py`, reverting it
  to the 117-line placeholder and wiping all Parts C-G edits.
- Detected by AppTest (About page showed old placeholder).
- Fixed: rewrote full final `app.py`; re-verified all 4 pages
  (HOME/SINGLE/BATCH/ABOUT) = 0 exceptions each; single-predict
  (insider 0.51), batch CSV (8 rows -> 8/8/0, 8/0/0, 2 charts,
  top-10 df, download), About (5 subtitles, 3 tables, 6 success).

#### Lesson / Rule
- DO NOT re-execute notebook 14 while app.py is edited directly
  (cell 17 app_code is stale). Refactor proposal pending:
  app.py -> app.py + predict.py + utils.py (+ load style.css).

#### Files
- `STREAMLIT/app.py` (Parts C-G complete)
- `STREAMLIT/requirements.txt`, `STREAMLIT/style.css` (notebook)
- `NOTEBOOKS/14_Streamlit_Deployment.ipynb` (28 cells)
- `DOCS/guide.txt` (Batch 7 notes)

---

### 2026-08-02 - Notebook 14 Batch 8 (refactor + hazard fix)

#### Task
User-approved refactor: split monolithic app.py into modular
files, and strip the stale app_code from the notebook so it can
never overwrite the app again.

#### What Was Done
- `STREAMLIT/utils.py` (new): BASE_DIR paths, `get_feature_names()`
  (@st.cache_data), `load_model()` (@st.cache_resource, sets
  feature_names_in_), `load_css()`.
- `STREAMLIT/predict.py` (new): `risk_level()`,
  `predict_single()`, `predict_batch()`.
- `STREAMLIT/app.py` (rewritten as UI-only): imports utils/predict;
  Home/Single/Batch/About behaviour unchanged; style.css now
  actually loaded via `utils.load_css()`.
- `sys.path` guard in app.py + predict.py so the app runs from
  STREAMLIT/ OR the project root (`streamlit run STREAMLIT/app.py`).

#### Notebook hazard removed
- Deleted old cells 16-21 (stale monolithic `app_code` string +
  `with open(...)` writer that clobbered app.py on every run).
- Replaced with a markdown note ("app is maintained directly in
  the files... does NOT rewrite them") + a no-write verification
  cell. Notebook now 24 cells.
- Re-executed notebook: 0 errors; app.py / predict.py / utils.py
  confirmed byte-identical after re-run (hazard gone).

#### Verified
- AppTest from STREAMLIT/ and from project root: all 4 pages
  0 exceptions; single zero-input -> insider 0.51; batch CSV
  8 rows -> 8/8/0 + 8/0/0; About 5 subtitles / 3 tables / 6
  success.
- Real `streamlit run` smoke test -> HTTP 200.

#### Files
- `STREAMLIT/app.py`, `STREAMLIT/predict.py`, `STREAMLIT/utils.py`
- `STREAMLIT/style.css`, `STREAMLIT/requirements.txt`
- `NOTEBOOKS/14_Streamlit_Deployment.ipynb` (24 cells)
- `DOCS/guide.txt` (Batch 8 notes)

---

### 2026-08-03 - Streamlit Option 3 (type-aware + grouped inputs)

#### Task
User's Option 3: pick widget per feature type and group the 47
inputs into professional category sections on the Single
Prediction page.

#### What Was Done
- Verified the actual data first: NONE of the 47 features are
  true 0/1 booleans (after_hours_events = 0..2763, etc.), so the
  user's sample boolean list was adapted to real dtypes:
  int features -> number_input step=1 format="%d";
  float features -> number_input step=0.1 format="%.2f".
- `utils.get_float_features()` added (@st.cache_data) returning
  frozenset of float-dtype features (21 floats / 26 ints).
- `app.py` FEATURE_CATEGORIES groups features into 6 expanders:
  📂 Logon (11), 💻 Device (5), 📧 Email (7), 📁 File (11),
  🌐 HTTP (8), 🧠 Psychometric (5) - 47 total, order ==
  FEATURE_NAMES so the model input stays column-aligned.

#### Verified
- Coverage: 47 categorized, 0 missing / 0 extra / 0 dups.
- Category order identical to FEATURE_NAMES: True.
- AppTest: 6 expanders, 47 dtype-aware number_inputs, predict
  click 0 exceptions, zero-input -> insider 0.51 (49/51%).
- streamlit run smoke test -> HTTP 200.

#### Files
- `STREAMLIT/app.py`, `STREAMLIT/utils.py`
- `DOCS/guide.txt` (Batch 9 notes)

---

### 2026-07-27 - Created Notebook Files

#### Files Created (empty, ready for code)
```
NOTEBOOKS/
├── 01_Logon_Feature_Engineering.ipynb
├── 02_Device_Feature_Engineering.ipynb
├── 03_Email_Feature_Engineering.ipynb
├── 04_File_Feature_Engineering.ipynb
├── 05_HTTP_Feature_Engineering.ipynb
├── 06_Psychometric_Feature_Engineering.ipynb
├── 07_Merge_All_Features.ipynb
├── 08_Label_Creation.ipynb
├── 09_Data_Preprocessing.ipynb
├── 10_Exploratory_Data_Analysis.ipynb
├── 11_Model_Training.ipynb
├── 12_Model_Evaluation.ipynb
├── 13_Model_Interpretation.ipynb
└── 14_Save_Final_Model.ipynb
```
