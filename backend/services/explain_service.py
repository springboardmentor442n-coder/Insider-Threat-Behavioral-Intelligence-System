"""
explain_service.py

Explainable AI Service
Generates human-readable explanations
for employee risk scores.
"""

from services.risk_service import calculate_employee_risk


# ==========================================================
# Risk Recommendations
# ==========================================================

def get_recommendations(level):

    if level == "Critical":
        return [
            "Immediately notify SOC.",
            "Disable employee account.",
            "Audit USB activities.",
            "Review recent emails.",
            "Inspect downloaded files.",
        ]

    elif level == "High":
        return [
            "Monitor employee activity.",
            "Review external communications.",
            "Inspect file transfers.",
            "Check login history.",
        ]

    elif level == "Medium":
        return [
            "Continue monitoring.",
            "Review unusual activities.",
        ]

    else:

        return [
            "No suspicious activity detected."
        ]


# ==========================================================
# Explanation Generator
# ==========================================================

def generate_explanation(username):

    risk = calculate_employee_risk(username)

    if risk is None:
        return None

    features = risk["features"]

    explanations = []

    # ---------------------------------------------------
    # Login
    # ---------------------------------------------------

    if features["night_logins"]:

        explanations.append(
            f"Logged in during night hours {features['night_logins']} times."
        )

    if features["weekend_logins"]:

        explanations.append(
            f"Logged in on weekends {features['weekend_logins']} times."
        )

    if features["unique_pcs"] > 1:

        explanations.append(
            f"Used {features['unique_pcs']} different computers."
        )

    # ---------------------------------------------------
    # USB
    # ---------------------------------------------------

    if features["usb_connects"]:

        explanations.append(
            f"Connected USB devices {features['usb_connects']} times."
        )

    # ---------------------------------------------------
    # Email
    # ---------------------------------------------------

    if features["external_emails"]:

        explanations.append(
            f"Sent {features['external_emails']} external emails."
        )

    if features["attachments"]:

        explanations.append(
            f"Shared {features['attachments']} email attachments."
        )

    if features["large_attachments"]:

        explanations.append(
            f"Sent {features['large_attachments']} large emails."
        )

    # ---------------------------------------------------
    # Websites
    # ---------------------------------------------------

    if features["file_sharing"]:

        explanations.append(
            f"Visited file-sharing websites {features['file_sharing']} times."
        )

    if features["social_media"]:

        explanations.append(
            f"Visited social-media websites {features['social_media']} times."
        )

    if features["job_sites"]:

        explanations.append(
            f"Visited job-search websites {features['job_sites']} times."
        )

    if features["developer_sites"]:

        explanations.append(
            f"Visited developer websites {features['developer_sites']} times."
        )

    # ---------------------------------------------------
    # Files
    # ---------------------------------------------------

    if features["file_access"]:

        explanations.append(
            f"Accessed {features['file_access']} files."
        )

    if features["archives"]:

        explanations.append(
            f"Opened {features['archives']} archive files."
        )

    if features["executables"]:

        explanations.append(
            f"Executed or accessed {features['executables']} executable files."
        )

    return {

        "employee": username,

        "risk_score": risk["risk_score"],

        "risk_level": risk["risk_level"],

        "summary": (
            f"Employee is classified as "
            f"{risk['risk_level']} risk "
            f"with a score of {risk['risk_score']}."
        ),

        "reasons": risk["reasons"],

        "behavior_summary": explanations,

        "recommendations": get_recommendations(
            risk["risk_level"]
        )
    }


# ==========================================================
# Bulk Explanations
# ==========================================================

def generate_all_explanations():

    from services.feature_service import get_all_profiles

    results = []

    for employee in get_all_profiles():

        results.append(
            generate_explanation(employee)
        )

    return results
