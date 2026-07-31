import pandas as pd


def generate_risk_reasons(employee: pd.Series):

    reasons = []

    # Login Behaviour
    if employee["after_hours_logins"] >= 5:
        reasons.append("Frequent after-hours logins")

    if employee["weekend_logins"] >= 3:
        reasons.append("Weekend login activity")

    # HTTP Behaviour
    if employee["http_visit_count"] >= 56099:
        reasons.append("High web browsing activity")

    # Email Behaviour
    if employee["external_emails"] >= 2600:
        reasons.append("Large number of external emails")

    # File Behaviour
    if employee["file_access_count"] >= 2321:
        reasons.append("High file access activity")

    # Device Behaviour
    if employee["device_usage_count"] >= 2004:
        reasons.append("Frequent USB/device usage")

    # If no major indicators exist
    if len(reasons) == 0:
        reasons.append("No abnormal behaviour detected")

    return reasons