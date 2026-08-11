import os
import sys
import sqlite3
import pandas as pd

# Add backend to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.core.config import settings

def import_results():
    csv_path = settings.RISK_RESULTS_CSV
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")

    if not os.path.exists(csv_path):
        print(f"Error: Target CSV file not found at {csv_path}")
        return

    print(f"Reading dataset from {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows from CSV.")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS behavioral_risk_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT NOT NULL,
        day TEXT NOT NULL,
        logon_count INTEGER DEFAULT 0,
        logoff_count INTEGER DEFAULT 0,
        off_hours_logons INTEGER DEFAULT 0,
        unique_pcs INTEGER DEFAULT 0,
        device_connects INTEGER DEFAULT 0,
        device_disconnects INTEGER DEFAULT 0,
        unique_device_pcs INTEGER DEFAULT 0,
        file_activity_count INTEGER DEFAULT 0,
        unique_file_pcs INTEGER DEFAULT 0,
        unique_files INTEGER DEFAULT 0,
        sensitive_file_count INTEGER DEFAULT 0,
        email_count INTEGER DEFAULT 0,
        attachment_count INTEGER DEFAULT 0,
        total_email_size REAL DEFAULT 0.0,
        unique_email_pcs INTEGER DEFAULT 0,
        external_email_count INTEGER DEFAULT 0,
        http_request_count INTEGER DEFAULT 0,
        unique_http_urls INTEGER DEFAULT 0,
        off_hours_http INTEGER DEFAULT 0,
        prediction INTEGER DEFAULT 0,
        prediction_probability REAL DEFAULT 0.0,
        ml_risk_score REAL DEFAULT 0.0,
        behavioral_risk_score REAL DEFAULT 0.0,
        final_risk_score REAL DEFAULT 0.0,
        severity TEXT DEFAULT 'Low'
    );
    """)

    # Check existing count
    cursor.execute("SELECT COUNT(*) FROM behavioral_risk_records")
    existing_count = cursor.fetchone()[0]

    if existing_count >= len(df):
        print(f"Database already contains {existing_count} records. Skipping duplicate import.")
        conn.close()
        return

    print(f"Importing {len(df)} records into SQLite database {db_path}...")
    
    # Clean duplicates before insert if needed
    cursor.execute("DELETE FROM behavioral_risk_records")
    conn.commit()

    feature_cols = [
        "user", "day", "logon_count", "logoff_count", "off_hours_logons", "unique_pcs",
        "device_connects", "device_disconnects", "unique_device_pcs",
        "file_activity_count", "unique_file_pcs", "unique_files", "sensitive_file_count",
        "email_count", "attachment_count", "total_email_size", "unique_email_pcs", "external_email_count",
        "http_request_count", "unique_http_urls", "off_hours_http",
        "prediction", "prediction_probability", "ml_risk_score", "behavioral_risk_score", "final_risk_score", "severity"
    ]

    available_cols = [c for c in feature_cols if c in df.columns]
    import_df = df[available_cols]

    import_df.to_sql("behavioral_risk_records", conn, if_exists="append", index=False)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM behavioral_risk_records")
    final_count = cursor.fetchone()[0]
    print(f"Import completed successfully. Total records in database: {final_count}")
    conn.close()

if __name__ == "__main__":
    import_results()
