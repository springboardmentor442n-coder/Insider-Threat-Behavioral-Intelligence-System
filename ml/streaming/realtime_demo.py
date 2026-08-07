import time
from pathlib import Path

from stream_data import stream_data
from feature_builder import build_features
from predictor import predict_user

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = PROJECT_ROOT / "datasets" / "processed" / "final_features.csv"

print("=" * 60)
print(" REAL-TIME INSIDER THREAT DETECTION SYSTEM ")
print("=" * 60)

stream = stream_data(DATA_PATH)

while True:

    row = next(stream)

    features = build_features(row)

    prediction = predict_user(features)

    print("\n" + "-" * 50)
    print(f"User               : {row['user']}")
    print(f"Device Connections : {row['device_connections']}")
    print(f"Emails Sent        : {row['emails_sent']}")
    print(f"Files Accessed     : {row['files_accessed']}")
    print(f"Websites Visited   : {row['websites_visited']}")
    print(f"Logon Count        : {row['logon_count']}")

    print("-" * 50)

    if prediction == "INSIDER":
        print("🚨 ALERT : INSIDER THREAT DETECTED")
    else:
        print("✅ NORMAL USER")

    print("-" * 50)

    time.sleep(2)