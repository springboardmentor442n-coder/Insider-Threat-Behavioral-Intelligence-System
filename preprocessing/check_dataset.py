import pandas as pd

df = pd.read_csv("dataset/processed/employee_features.csv")

print("=" * 80)
print("Shape")
print(df.shape)

print("=" * 80)
print("Columns")
print(df.columns.tolist())

print("=" * 80)
print("Missing Values")
print(df.isnull().sum())

print("=" * 80)
print("Threat Label Distribution")

if "threat_label" in df.columns:
    print(df["threat_label"].value_counts())
else:
    print("No threat_label column found")

print("=" * 80)
print(df.head())