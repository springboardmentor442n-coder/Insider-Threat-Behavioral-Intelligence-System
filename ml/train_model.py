import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
PROCESSED_DATA = Path("dataset/processed")

print("=" * 50)
print("INSIDER THREAT MODEL TRAINING")
print("=" * 50)

print("\nLoading feature engineered dataset...")

df = pd.read_csv(PROCESSED_DATA / "logon_features.csv")

print("Dataset loaded successfully!")

print("\nDataset Shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

import pandas as pd
from pathlib import Path

PROCESSED_DATA = Path("dataset/processed")

print("=" * 50)
print("INSIDER THREAT MODEL TRAINING")
print("=" * 50)

print("\nLoading feature engineered dataset...")

df = pd.read_csv(PROCESSED_DATA / "logon_features.csv")

print("Dataset loaded successfully!")

print("\nDataset Shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())
print("\nCreating target column...")

df["target"] = df["late_night_login"]

print("Target column created!")

print(df["target"].value_counts())
print("\nSelecting features...")

X = df[
    [
        "login_count",
        "unique_pc_count",
        "is_weekend",
        "hour"
    ]
]

y = df["target"]

print(X.head())

print("\nTarget:")
print(y.head())
from sklearn.model_selection import train_test_split

print("\nSplitting dataset...")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))
print("\nTraining Random Forest model...")

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

print("Model trained successfully!")
print("\nMaking predictions...")

y_pred = model.predict(X_test)

print("Prediction completed!")

print(y_pred[:20])
print("\nEvaluating model...")

accuracy = accuracy_score(y_test, y_pred)

print("\nAccuracy:")
print(accuracy)

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))
model_path = "ml/models/random_forest_model.pkl"

joblib.dump(model, model_path)

print("\nModel saved successfully!")
print(model_path)