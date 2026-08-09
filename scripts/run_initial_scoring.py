import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.services import ml_service
from app.models import Employee

db = SessionLocal()

print("Calculating behavioral profiles, anomalies, and risk scores...")
try:
    # Build profiles, detect anomalies, and compute risk scores
    ml_service.run_daily_scoring(db)
    print("Scoring run completed successfully!")
except Exception as e:
    print(f"Scoring failed: {e}")
finally:
    db.close()
