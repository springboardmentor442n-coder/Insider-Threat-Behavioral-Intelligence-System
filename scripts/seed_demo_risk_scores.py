"""
Demo Risk Score Seeder
======================
Populates the database with a realistic spread of risk scores across all employees
for demonstration purposes. Creates Critical, High, Medium, and Low risk distributions.

Run with:
    python scripts/seed_demo_risk_scores.py
"""
import sys
import os
import random
from datetime import datetime, timezone, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models import Employee, RiskScore, RiskCategory, Alert, AlertSeverity, AlertStatus

random.seed(42)

# Risk distribution: (category, score_range, weight)
RISK_PROFILES = [
    {
        "category": RiskCategory.critical,
        "score_min": 80, "score_max": 98,
        "weight": 0.12,
        "top_factors_pool": [
            {"factor": "Privilege Escalation", "score": 9.2, "weight": "18.4%"},
            {"factor": "USB/External Storage", "score": 8.7, "weight": "17.4%"},
            {"factor": "After-Hours Activity", "score": 8.1, "weight": "16.2%"},
            {"factor": "Database Queries", "score": 7.9, "weight": "15.8%"},
            {"factor": "Failed Login Attempts", "score": 7.6, "weight": "15.2%"},
            {"factor": "Large Data Transfers", "score": 7.2, "weight": "14.4%"},
            {"factor": "Cloud Uploads", "score": 6.8, "weight": "13.6%"},
        ],
        "shap_explanation": "High privilege abuse risk. Unusual access patterns combined with off-hours activity and data exfiltration indicators.",
        "recommended_action": "IMMEDIATE: Suspend account and escalate to Security Manager. Initiate forensic investigation.",
        "trend_options": ["increasing", "increasing", "stable"],
    },
    {
        "category": RiskCategory.high,
        "score_min": 60, "score_max": 79,
        "weight": 0.20,
        "top_factors_pool": [
            {"factor": "Failed Login Attempts", "score": 6.5, "weight": "13.0%"},
            {"factor": "VPN Usage Anomaly", "score": 5.9, "weight": "11.8%"},
            {"factor": "After-Hours Activity", "score": 5.6, "weight": "11.2%"},
            {"factor": "File Download Volume", "score": 5.2, "weight": "10.4%"},
            {"factor": "Database Access", "score": 4.9, "weight": "9.8%"},
            {"factor": "Unusual Login Hours", "score": 4.6, "weight": "9.2%"},
        ],
        "shap_explanation": "Elevated behavioral anomalies detected. Multiple risk indicators above baseline.",
        "recommended_action": "PRIORITY: Review activity logs in detail. Schedule security interview within 48 hours.",
        "trend_options": ["increasing", "stable", "stable"],
    },
    {
        "category": RiskCategory.medium,
        "score_min": 35, "score_max": 59,
        "weight": 0.35,
        "top_factors_pool": [
            {"factor": "Email Activity", "score": 3.8, "weight": "7.6%"},
            {"factor": "Website Visits", "score": 3.2, "weight": "6.4%"},
            {"factor": "Login Frequency", "score": 2.9, "weight": "5.8%"},
            {"factor": "File Downloads", "score": 2.7, "weight": "5.4%"},
            {"factor": "Session Duration", "score": 2.4, "weight": "4.8%"},
        ],
        "shap_explanation": "Moderate behavioral deviation. Some activities fall outside normal baselines but not conclusive.",
        "recommended_action": "MONITOR: Continue observation over the next 7 days. No immediate action required.",
        "trend_options": ["stable", "stable", "decreasing"],
    },
    {
        "category": RiskCategory.low,
        "score_min": 8, "score_max": 34,
        "weight": 0.33,
        "top_factors_pool": [
            {"factor": "Login Time", "score": 1.5, "weight": "3.0%"},
            {"factor": "Session Duration", "score": 1.2, "weight": "2.4%"},
            {"factor": "Login Frequency", "score": 0.9, "weight": "1.8%"},
            {"factor": "Department Context", "score": 0.7, "weight": "1.4%"},
        ],
        "shap_explanation": "Behavior consistent with normal employee patterns. No significant anomalies detected.",
        "recommended_action": "ROUTINE: Standard monitoring. No action required.",
        "trend_options": ["stable", "decreasing", "stable"],
    },
]


def pick_profile():
    """Randomly select a risk profile based on weighted distribution."""
    total = sum(p["weight"] for p in RISK_PROFILES)
    r = random.uniform(0, total)
    cumulative = 0
    for profile in RISK_PROFILES:
        cumulative += profile["weight"]
        if r <= cumulative:
            return profile
    return RISK_PROFILES[-1]


def build_explanation(profile: dict) -> dict:
    """Build a realistic explanation JSON block for this risk profile."""
    pool = profile["top_factors_pool"]
    n = min(len(pool), random.randint(3, 5))
    factors = random.sample(pool, n)
    # Jitter scores slightly
    jittered = [
        {
            "factor": f["factor"],
            "score": round(f["score"] * random.uniform(0.85, 1.15), 2),
            "weight": f["weight"]
        }
        for f in factors
    ]
    return {
        "top_factors": jittered,
        "shap_explanation": profile["shap_explanation"],
        "recommended_action": profile["recommended_action"],
        "confidence": round(random.uniform(72.0, 96.0), 1),
    }


def seed_demo_risk_scores():
    db = SessionLocal()
    try:
        employees = db.query(Employee).all()
        if not employees:
            print("❌ No employees found. Run seed.py or seed_cert_employees.py first.")
            return

        # ── Clear in correct FK order ──────────────────────────────────────
        # 1. Null out FK references in alerts so risk_scores can be deleted
        from sqlalchemy import text
        db.execute(text("UPDATE alerts SET risk_score_id = NULL WHERE risk_score_id IS NOT NULL"))
        db.commit()

        # 2. Delete alerts first (child of risk_scores)
        alert_del = db.query(Alert).delete()
        db.commit()
        print(f"🗑️  Cleared {alert_del} existing alert records.")

        # 3. Now safe to delete risk_scores
        deleted = db.query(RiskScore).delete()
        db.commit()
        print(f"🗑️  Cleared {deleted} existing risk score records.")

        created = 0
        category_counts = {cat: 0 for cat in RiskCategory}

        for emp in employees:
            profile = pick_profile()
            score = round(random.uniform(profile["score_min"], profile["score_max"]), 1)
            explanation = build_explanation(profile)
            trend = random.choice(profile["trend_options"])

            # Spread score dates across the last 7 days for realism
            days_ago = random.randint(0, 6)
            score_date = datetime.now(timezone.utc) - timedelta(days=days_ago, hours=random.randint(0, 23))

            rs = RiskScore(
                employee_id=emp.id,
                behavioral_anomaly_score=round(score * 0.4, 1),
                privilege_misuse_score=round(score * 0.25 * random.uniform(0.5, 1.2), 1),
                data_access_violation_score=round(score * 0.2 * random.uniform(0.5, 1.2), 1),
                access_pattern_score=round(score * 0.15 * random.uniform(0.5, 1.2), 1),
                historical_security_score=round(explanation["confidence"], 1),
                total_score=score,
                risk_category=profile["category"],
                trend=trend,
                explanation=explanation,
                isolation_forest_score=round(score * random.uniform(0.88, 1.05), 1),
                xgboost_probability=round(explanation["confidence"] / 100.0, 4),
                score_date=score_date,
            )
            db.add(rs)
            category_counts[profile["category"]] += 1
            created += 1

            # Auto-create alerts for high/critical
            if profile["category"] in (RiskCategory.high, RiskCategory.critical):
                severity = AlertSeverity.critical if profile["category"] == RiskCategory.critical else AlertSeverity.high
                alert_id = f"ALT-DEMO-{emp.id:05d}"
                action_text = explanation["recommended_action"]
                alert = Alert(
                    alert_id=alert_id,
                    employee_id=emp.id,
                    title=f"{'⚠️ CRITICAL' if severity == AlertSeverity.critical else '🔴 HIGH'} Insider Threat Detected: {emp.full_name}",
                    description=f"{explanation['shap_explanation']} | Score: {score:.1f} | Action: {action_text}",
                    severity=severity,
                    status=random.choice([AlertStatus.open, AlertStatus.open, AlertStatus.investigating]),
                    triggered_at=score_date,
                )
                db.add(alert)

        db.commit()

        print("\n" + "=" * 50)
        print(f"✅ Seeded {created} Risk Score records")
        print("=" * 50)
        for cat, count in category_counts.items():
            pct = round((count / created) * 100, 1)
            bar = "█" * int(pct / 4)
            print(f"  {cat.value:12s}  {count:4d}  ({pct:5.1f}%)  {bar}")
        print("=" * 50)
        print("\n✅ Risk page is ready for demo!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_risk_scores()
