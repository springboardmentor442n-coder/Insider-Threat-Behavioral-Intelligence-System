import pandas as pd
import numpy as np
import os
import pickle
from functools import reduce

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, IsolationForest
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
import matplotlib.pyplot as plt
import seaborn as sns

# =====================================================================
# 0. CHECK AVAILABLE FILES (run once to confirm paths / look for real labels)
# =====================================================================
print("Files available in /kaggle/input:")
for root, dirs, files in os.walk('/kaggle/input'):
    for f in files:
        print(os.path.join(root, f))
print("\n--- Look for insiders.csv / answers.csv / answers folder above ---\n")

# =====================================================================
# 1. LOAD RAW DATA
# =====================================================================
DATA_DIR = "/kaggle/input/datasets/mrajaxnp/cert-insider-threat-detection-research"

logon_data = pd.read_csv(f"{DATA_DIR}/logon.csv")
email_data = pd.read_csv(f"{DATA_DIR}/email.csv")
http_data = pd.read_csv(f"{DATA_DIR}/http.csv")  # remove nrows limit — read full file if memory allows
file_data = pd.read_csv(f"{DATA_DIR}/file.csv")
device_data = pd.read_csv(f"{DATA_DIR}/device.csv")
psychometric_data = pd.read_csv(f"{DATA_DIR}/psychometric.csv")

# Sanity check — confirm logon.csv has both Logon and Logoff events combined
print("Logon activity values:", logon_data['activity'].unique())

# =====================================================================
# 2. PREP DATE / DAY / HOUR COLUMNS
# =====================================================================
for df in [logon_data, email_data, http_data, file_data, device_data]:
    df['date'] = pd.to_datetime(df['date'])
    df['day'] = df['date'].dt.dayofweek       # 0=Mon ... 6=Sun
    df['hour'] = df['date'].dt.hour
    df['calendar_day'] = df['date'].dt.date

file_data['to_removable_media'] = file_data['to_removable_media'].astype(bool)
file_data['from_removable_media'] = file_data['from_removable_media'].astype(bool)
email_data['attachments'] = pd.to_numeric(email_data['attachments'], errors='coerce').fillna(0).astype(int)

# =====================================================================
# 3. FEATURE ENGINEERING (per user-day)
# =====================================================================

# ---- LOGON ----
logon_features = logon_data.groupby(['user', 'calendar_day']).agg(
    L1=('pc', 'nunique'),
    L2=('activity', lambda x: (x == 'Logon').sum()),
    L3=('activity', lambda x: (x == 'Logoff').sum()),
    L6=('day', lambda x: int(x.iloc[0] >= 5)),
    L8=('pc', lambda x: x.value_counts().idxmax()),
    L9=('hour', lambda x: ((x < 6) | (x > 18)).sum()),
    L10=('hour', lambda x: ((x >= 6) & (x <= 18)).sum()),
    L11=('pc', lambda x: x.value_counts().max() / len(x)),
    L12=('hour', lambda x: (x > 22).sum()),
    L13=('hour', lambda x: (x < 6).sum()),
).reset_index().rename(columns={'calendar_day': 'date'})

# ---- EMAIL ----
email_features = email_data.groupby(['user', 'calendar_day']).agg(
    E1=('to', 'nunique'),
    E2=('cc', 'count'),
    E3=('bcc', 'count'),
    E4=('size', 'mean'),
    E5=('attachments', 'sum'),
    E6=('to', lambda x: sum('@' in str(a) and not str(a).endswith('dtaa.com') for a in x.astype(str))),
    E7=('attachments', lambda x: x.gt(0).sum()),
    E8=('hour', lambda x: ((x < 6) | (x > 18)).sum()),
    E9=('pc', 'nunique'),
    E11=('size', 'sum'),
    E12=('to', lambda x: x.dropna().astype(str).str.contains('gmail.com|yahoo.com|msn.com|juno.com|.net').sum()),
    E13=('content', lambda x: x.dropna().astype(str).str.count('confidential|password|secure').sum()),
    E16=('content', lambda x: x.dropna().astype(str).str.len().mean()),
).reset_index().rename(columns={'calendar_day': 'date'})

# ---- HTTP ----
http_features = http_data.groupby(['user', 'calendar_day']).agg(
    H1=('url', 'nunique'),
    H2=('activity', 'count'),
    H3=('hour', lambda x: ((x < 6) | (x > 18)).sum()),
    H5=('activity', lambda x: x.str.contains('WWW Upload', case=False, na=False).sum()),
    H6=('url', lambda x: x.str.contains('alibaba|amazon|ebay', na=False).sum()),
    H7=('url', lambda x: x.str.contains('examiner|discovery|foodnetwork|thechive|wsj', na=False).sum()),
    H8=('url', lambda x: x.str.contains('soundcloud|m-w|youtube|cafemom|netflix', na=False).sum()),
    H9=('url', lambda x: x.str.len().mean()),
    H10=('activity', lambda x: x.str.contains('WWW Download', case=False, na=False).sum()),
    H11=('content', lambda x: x.dropna().astype(str).str.count(r'\bsecure\b|\bpassword\b').sum()),
    H12=('content', lambda x: x.dropna().astype(str).str.len().mean()),
).reset_index().rename(columns={'calendar_day': 'date'})

# ---- FILE ----
file_features = file_data.groupby(['user', 'calendar_day']).agg(
    F1=('filename', 'nunique'),
    F2=('activity', 'count'),
    F3=('to_removable_media', 'sum'),
    F4=('from_removable_media', 'sum'),
    F5=('hour', lambda x: ((x < 6) | (x > 18)).sum()),
    F7=('activity', lambda x: x.str.contains('delete', case=False, na=False).sum()),
    F8=('activity', lambda x: x.str.contains('copy', case=False, na=False).sum()),
    F9=('activity', lambda x: x.str.contains('write', case=False, na=False).sum()),
    F10=('content', lambda x: x.dropna().astype(str).str.count('confidential|password|sensitive').sum()),
    F11=('content', lambda x: x.dropna().astype(str).str.len().mean()),
).reset_index().rename(columns={'calendar_day': 'date'})

# ---- DEVICE ----
device_features = device_data.groupby(['user', 'calendar_day']).agg(
    D1=('pc', 'nunique'),
    D2=('activity', 'count'),
    D3=('hour', lambda x: ((x < 6) | (x > 18)).sum()),
    D5=('activity', lambda x: x.str.contains('connect', case=False, na=False).sum()),
    D6=('activity', lambda x: x.str.contains('disconnect', case=False, na=False).sum()),
).reset_index().rename(columns={'calendar_day': 'date'})

# ---- PSYCHOMETRIC (static per user) ----
psychometric_features = psychometric_data[['user_id', 'O', 'C', 'E', 'A', 'N']].rename(columns={'user_id': 'user'})

# ---- MERGE ALL (per user-day) ----
daily_dfs = [logon_features, email_features, http_features, file_features, device_features]
combined_df = reduce(lambda l, r: pd.merge(l, r, on=['user', 'date'], how='outer'), daily_dfs)
combined_df = combined_df.fillna(0)

combined_df = combined_df.merge(psychometric_features, on='user', how='left')
psych_cols = ['O', 'C', 'E', 'A', 'N']
combined_df[psych_cols] = combined_df[psych_cols].fillna(combined_df[psych_cols].mean())

print("\nFeature table shape:", combined_df.shape)
combined_df.to_csv('/kaggle/working/features_final.csv', index=False)

# =====================================================================
# 4. LABELING — TEMPORARY THRESHOLD-BASED (placeholder)
# NOTE: Replace this block once real CERT ground-truth answer files
# are located — merge them on ['user','date'] instead of computing
# labels from feature thresholds.
# =====================================================================
feature_columns = ['F8', 'D3', 'F7', 'D6', 'H5', 'L9', 'F3', 'E6']
feature_means = combined_df[feature_columns].mean()

def assign_label(row):
    if all(row[f] <= feature_means[f] * 0.9 for f in feature_columns):
        return "Normal"
    elif row['F8'] > feature_means['F8'] * 1.2 or row['D3'] > feature_means['D3'] * 1.2:
        return "Intellectual Property Theft"
    elif row['F7'] > feature_means['F7'] * 1.2 or row['D6'] > feature_means['D6'] * 1.2:
        return "IT Sabotage"
    elif row['H5'] > feature_means['H5'] * 1.2 or row['L9'] > feature_means['L9'] * 1.2:
        return "Unauthorized Access"
    elif row['F3'] > feature_means['F3'] * 1.2 or row['E6'] > feature_means['E6'] * 1.2:
        return "Data Exfiltration"
    else:
        return "Normal"

combined_df['Label'] = combined_df.apply(assign_label, axis=1)
print("\nLabel distribution:\n", combined_df['Label'].value_counts())

# =====================================================================
# 5. PREPARE X / y
# =====================================================================
X = combined_df.drop(columns=['user', 'date', 'Label'], errors='ignore')
y = combined_df['Label']

categorical_cols = X.select_dtypes(include=['object']).columns
for col in categorical_cols:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col].astype(str))

X = X.fillna(X.mean(numeric_only=True))

# =====================================================================
# 6. SCALE + SPLIT
# =====================================================================
scaler = MinMaxScaler()
X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.3, random_state=42, stratify=y
)

# =====================================================================
# 7. TRAIN + COMPARE SUPERVISED MODELS
# =====================================================================
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Random Forest": RandomForestClassifier(n_estimators=200, random_state=42),
    "Gradient Boosting": GradientBoostingClassifier(random_state=42),
    "KNN": KNeighborsClassifier(),
    "SVM": SVC(),
}

results = {}
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

for name, model in models.items():
    print(f"\n================= {name} =================")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="macro", zero_division=0)
    recall = recall_score(y_test, y_pred, average="macro", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)
    results[name] = acc

    print("Test Accuracy:", acc)
    print("Precision (macro):", precision)
    print("Recall (macro):", recall)
    print("F1 (macro):", f1)
    print("\nClassification Report:\n", classification_report(y_test, y_pred, zero_division=0))

    cv_scores = cross_val_score(model, X_train, y_train, cv=skf, scoring='accuracy')
    print("CV Fold Scores:", cv_scores)
    print("CV Mean Accuracy:", cv_scores.mean())

    cm = confusion_matrix(y_test, y_pred, labels=model.classes_)
    plt.figure(figsize=(7, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=model.classes_, yticklabels=model.classes_)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title(f"{name} — Confusion Matrix")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

results_df = pd.DataFrame(list(results.items()), columns=["Model", "Test Accuracy"])
results_df = results_df.sort_values(by="Test Accuracy", ascending=False)
print("\n================= MODEL COMPARISON =================")
print(results_df)

# =====================================================================
# 8. ISOLATION FOREST (unsupervised anomaly detection)
# =====================================================================
print("\n================= Isolation Forest =================")

iso_forest = IsolationForest(n_estimators=200, contamination=0.05, random_state=42)
iso_forest.fit(X_train)

iso_pred_test = iso_forest.predict(X_test)
iso_labels_test = np.where(iso_pred_test == -1, "Anomaly", "Normal")

y_test_binary = np.where(y_test == "Normal", "Normal", "Anomaly")

print("Isolation Forest flagged anomalies (test set):", (iso_labels_test == "Anomaly").sum(),
      "out of", len(iso_labels_test))
print("\nComparison against threshold-based labels (Normal vs Any-Threat):")
print(classification_report(y_test_binary, iso_labels_test, zero_division=0))

cm_iso = confusion_matrix(y_test_binary, iso_labels_test, labels=["Normal", "Anomaly"])
plt.figure(figsize=(6, 5))
sns.heatmap(cm_iso, annot=True, fmt='d', cmap='Oranges',
            xticklabels=["Normal", "Anomaly"], yticklabels=["Normal", "Anomaly"])
plt.xlabel("Predicted")
plt.ylabel("Actual (threshold-based)")
plt.title("Isolation Forest — Confusion Matrix")
plt.tight_layout()
plt.show()

anomaly_scores = iso_forest.decision_function(X_test)
combined_df.loc[X_test.index, 'iso_anomaly_score'] = anomaly_scores
combined_df.loc[X_test.index, 'iso_prediction'] = iso_labels_test

# =====================================================================
# 9. SAVE ARTIFACTS
# =====================================================================
best_model_name = results_df.iloc[0]['Model']
best_model = models[best_model_name]
print(f"\nBest performing model: {best_model_name}")

with open("/kaggle/working/model.pkl", "wb") as f:
    pickle.dump(best_model, f)
with open("/kaggle/working/isolation_forest.pkl", "wb") as f:
    pickle.dump(iso_forest, f)
with open("/kaggle/working/scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)
with open("/kaggle/working/feature_means.pkl", "wb") as f:
    pickle.dump(X.mean().to_dict(), f)

combined_df.to_csv('/kaggle/working/labeled_with_isoforest.csv', index=False)

print("\nAll artifacts saved to /kaggle/working/")
print("\nModel, scaler, and feature means saved.")
