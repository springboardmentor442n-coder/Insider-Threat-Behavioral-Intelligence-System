"""
Insider Threat Detection — Model Training
Uses REAL ground-truth labels (matched from CERT r4.2 official answer files
by log-row ID), not synthetic thresholds.
Reads cleaned data from preprocess.py's output.
"""
import os, glob, pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.model_selection import GroupShuffleSplit
from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    precision_score, recall_score, f1_score, precision_recall_curve, auc
)
import xgboost as xgb

from feature_engineering import engineer_features, attach_ldap_context

# =====================================================================
# 1. LOAD CLEANED DATA (output of preprocess.py)
# =====================================================================
BASE_PATH = "/kaggle/working/cleaned/"
ANSWERS_BASE = "/kaggle/input/datasets/andrihjonior/cert-insider-threat-dataset-r4-2/answers/"

logon = pd.read_csv(os.path.join(BASE_PATH, "logon_clean.csv"), parse_dates=["date"])
device = pd.read_csv(os.path.join(BASE_PATH, "device_clean.csv"), parse_dates=["date"])
file_df = pd.read_csv(os.path.join(BASE_PATH, "file_clean.csv"), parse_dates=["date"])
email = pd.read_csv(os.path.join(BASE_PATH, "email_clean.csv"), parse_dates=["date"])
http = pd.read_csv(os.path.join(BASE_PATH, "http_clean.csv"), parse_dates=["date"])

print("Logon activity values:", logon["activity"].unique())

# Capture ID tables (needed for real label matching)
id_tables = {}
for name, df in [("logon", logon), ("device", device), ("file", file_df), ("email", email), ("http", http)]:
    df["day"] = df["date"].dt.date
    id_tables[name] = df[["id", "user", "day"]].copy()

# =====================================================================
# 2. FEATURE ENGINEERING (per user-day)
# =====================================================================
combined_df = engineer_features(logon, device, file_df, email, http)
print(f"Feature table shape: {combined_df.shape}")

# =====================================================================
# 3. LDAP INTEGRATION
# =====================================================================
LDAP_PATH = "/kaggle/input/datasets/andrihjonior/cert-insider-threat-dataset-r4-2/r4.2/LDAP/"
ldap_files = glob.glob(os.path.join(LDAP_PATH, "*.csv"))
ldap_list = []
for f in ldap_files:
    df = pd.read_csv(f)
    df["month_year"] = os.path.basename(f).split(".csv")[0]
    ldap_list.append(df)
master_ldap = pd.concat(ldap_list, ignore_index=True)
master_ldap = master_ldap.drop_duplicates(subset=["user_id", "month_year"], keep="last")

le_dict = {}
combined_df["day"] = pd.to_datetime(combined_df["day"])
combined_df["month_year"] = combined_df["day"].dt.strftime("%Y-%m")
combined_df = pd.merge(combined_df, master_ldap.rename(columns={"user_id": "user"}),
                        on=["user", "month_year"], how="left")
combined_df = combined_df.sort_values(by=["user", "day"])
for col in ["role", "department", "team", "supervisor"]:
    combined_df[col] = combined_df.groupby("user")[col].ffill()
    combined_df[col] = combined_df[col].fillna("Unknown").astype(str)
    le = LabelEncoder()
    combined_df[f"{col}_encoded"] = le.fit_transform(combined_df[col])
    le_dict[col] = le
combined_df.drop(columns=["role", "department", "team", "supervisor", "month_year"], inplace=True)

print(f"Shape after LDAP: {combined_df.shape}")

# =====================================================================
# 4. REAL GROUND-TRUTH LABELS (row-level ID matching against answer files)
# =====================================================================
SCHEMAS = {
    "logon":  ["type", "id", "date", "user", "pc", "activity"],
    "device": ["type", "id", "date", "user", "pc", "activity"],
    "http":   ["type", "id", "date", "user", "pc", "url", "content"],
    "file":   ["type", "id", "date", "user", "pc", "filename", "content"],
    "email":  ["type", "id", "date", "user", "pc", "to", "cc", "bcc",
               "from", "size", "attachment_count", "content"],
}

def parse_answer_file(path):
    rows_by_type = {k: [] for k in SCHEMAS}
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\r\n")
            if not line:
                continue
            row_type = line.split(",", 1)[0]
            if row_type not in SCHEMAS:
                continue
            n_fields = len(SCHEMAS[row_type])
            parts = line.split(",", n_fields - 1)
            if len(parts) == n_fields:
                rows_by_type[row_type].append(parts)
    return rows_by_type

def build_malicious_id_tables(answers_base, scenario_folders=("r4.2-1", "r4.2-2", "r4.2-3")):
    all_rows = {k: [] for k in SCHEMAS}
    for folder in scenario_folders:
        for path in glob.glob(os.path.join(answers_base, folder, "*.csv")):
            parsed = parse_answer_file(path)
            for k, rows in parsed.items():
                for r in rows:
                    all_rows[k].append(r + [folder])
    return {k: pd.DataFrame(v, columns=SCHEMAS[k] + ["scenario"]) for k, v in all_rows.items()}

malicious_tables = build_malicious_id_tables(ANSWERS_BASE)
mal_id_sets = {k: set(v["id"]) for k, v in malicious_tables.items()}

day_label_parts = []
for source, mal_ids in mal_id_sets.items():
    matched = id_tables[source][id_tables[source]["id"].isin(mal_ids)][["user", "day"]]
    day_label_parts.append(matched)

day_labels = pd.concat(day_label_parts, ignore_index=True).drop_duplicates()
day_labels["is_insider"] = 1
print(f"Malicious user-days: {len(day_labels)} | Unique insiders: {day_labels['user'].nunique()}")

combined_df["day"] = pd.to_datetime(combined_df["day"]).dt.date
combined_df = combined_df.merge(day_labels[["user", "day", "is_insider"]], on=["user", "day"], how="left")
combined_df["is_insider"] = combined_df["is_insider"].fillna(0).astype(int)
print(combined_df["is_insider"].value_counts())

# =====================================================================
# 5. USER-BASED TRAIN/TEST SPLIT (prevents identity leakage)
# =====================================================================
gss = GroupShuffleSplit(n_splits=1, test_size=0.3, random_state=42)
train_idx, test_idx = next(gss.split(combined_df, groups=combined_df["user"]))
train_df = combined_df.iloc[train_idx].copy()
test_df = combined_df.iloc[test_idx].copy()

assert len(set(train_df["user"]) & set(test_df["user"])) == 0, "User leakage between train/test!"

X_cols = [c for c in combined_df.columns if c not in ["user", "day", "is_insider"]]
assert "is_insider" not in X_cols, "Label leaked into features!"

X_train, y_train = train_df[X_cols], train_df["is_insider"]
X_test, y_test = test_df[X_cols], test_df["is_insider"]

# =====================================================================
# 6. SCALE + TRAIN XGBOOST
# =====================================================================
scaler = MinMaxScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

neg, pos = (y_train == 0).sum(), (y_train == 1).sum()
model = xgb.XGBClassifier(
    n_estimators=150, max_depth=6, learning_rate=0.05,
    scale_pos_weight=neg / pos, random_state=42, eval_metric="aucpr"
)
model.fit(X_train_scaled, y_train)

y_pred = model.predict(X_test_scaled)
y_prob = model.predict_proba(X_test_scaled)[:, 1]

precision, recall, _ = precision_recall_curve(y_test, y_prob)
pr_auc = auc(recall, precision)

print(f"PR-AUC: {pr_auc:.4f}")
print(f"Precision: {precision_score(y_test, y_pred):.4f}")
print(f"Recall: {recall_score(y_test, y_pred):.4f}")
print(f"F1: {f1_score(y_test, y_pred):.4f}")

flagged_users = set(test_df.loc[y_pred == 1, "user"])
true_insiders_test = set(test_df.loc[y_test == 1, "user"])
print(f"User-level recall: {len(flagged_users & true_insiders_test)}/{len(true_insiders_test)}")

# =====================================================================
# 7. ISOLATION FOREST (unsupervised comparison)
# =====================================================================
iso_forest = IsolationForest(n_estimators=200, contamination=0.003, random_state=42)
iso_forest.fit(X_train_scaled)
iso_pred = np.where(iso_forest.predict(X_test_scaled) == -1, 1, 0)
print("\nIsolation Forest F1:", f1_score(y_test, iso_pred, zero_division=0))

# =====================================================================
# 8. SAVE ARTIFACTS
# =====================================================================
os.makedirs("model", exist_ok=True)
with open("model/model.pkl", "wb") as f:
    pickle.dump(model, f)
with open("model/scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)
with open("model/feature_columns.pkl", "wb") as f:
    pickle.dump(X_cols, f)
with open("model/le_dict.pkl", "wb") as f:
    pickle.dump(le_dict, f)
with open("model/isolation_forest.pkl", "wb") as f:
    pickle.dump(iso_forest, f)

print("\nAll artifacts saved to model/")
