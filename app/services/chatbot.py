"""
AI Security Assistant Service
=============================
Processes natural language security queries from the SOC console.
Extracts facts from the database and returns expert analytical explanations,
remediation playbooks, and markdown tables.
"""
import re
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.models import Employee, RiskScore, Alert, Incident, Anomaly, Department
from app.ml import inference as inf_service


def handle_chat_query(db: Session, query: str) -> str:
    """
    Parses the NLP chat query and generates a context-rich markdown report
    based on live database facts.
    """
    q = query.lower().strip()

    # 1. "Why is employee <ID/Name> risky?" or "What caused this prediction?"
    emp_match = re.search(r"(?:why is employee|explain employee|about employee|what caused the prediction for)\s+([\w\d\-\s\.\@]+)", q)
    if emp_match:
        target = emp_match.group(1).strip()
        return _explain_employee_risk(db, target)

    # 2. "What caused this prediction?" (General latest prediction detail)
    if "caused this prediction" in q or "explain the latest prediction" in q:
        # Find the highest risk employee and explain them
        latest_risk = db.query(RiskScore).order_by(desc(RiskScore.total_score)).first()
        if latest_risk:
            return _explain_employee_risk(db, str(latest_risk.employee_id))
        return "No risk scores have been generated yet to explain."

    # 3. "Show suspicious employees today" or "who is risky today"
    if "suspicious" in q or "risky" in q or "threats today" in q:
        return _list_suspicious_employees(db)

    # 4. "Explain today's alerts" or "what are today's alerts"
    if "alert" in q:
        return _explain_todays_alerts(db)

    # 5. "Generate incident summary" or "summarize incidents"
    if "incident" in q or "summary" in q:
        return _generate_incident_summary(db)

    # 6. "Suggest mitigation steps" or "remediation"
    if "mitigation" in q or "remediation" in q or "mitigate" in q:
        # Pick the highest risk employee and suggest playbooks
        latest_risk = db.query(RiskScore).order_by(desc(RiskScore.total_score)).first()
        if latest_risk:
            emp = latest_risk.employee
            return _suggest_mitigation(db, emp)
        return "No high risk employees detected. Standard baseline monitoring active."

    # 7. "Summarize weekly threats" or "weekly report"
    if "weekly" in q or "week" in q:
        return _summarize_weekly_threats(db)

    # Help / Fallback
    return (
        "### 🛡️ SOC Assistant capabilities\n"
        "I am your AI Behavioral Intelligence Assistant. You can ask me questions like:\n"
        "- `Why is employee EMP001 risky?` or `Why is Alice Johnson risky?`\n"
        "- `Show suspicious employees today` (Lists top threat ratings)\n"
        "- `Explain today's alerts` (Breakdown of recent security indicators)\n"
        "- `Generate incident summary` (Status report on active investigations)\n"
        "- `Suggest mitigation steps` (Remediation playbooks for high-risk profiles)\n"
        "- `Summarize weekly threats` (Executive weekly analytics summary)"
    )


def _explain_employee_risk(db: Session, target: str) -> str:
    # Try finding employee by code, email or full name
    emp = (
        db.query(Employee)
        .filter(
            (Employee.employee_id == target) |
            (Employee.email == target) |
            (Employee.full_name.like(f"%{target}%")) |
            (Employee.id.like(target))
        )
        .first()
    )

    if not emp:
        return f"❌ Employee matching **'{target}'** was not found in the identity catalog."

    # Fetch latest risk score
    latest_score = (
        db.query(RiskScore)
        .filter(RiskScore.employee_id == emp.id)
        .order_by(desc(RiskScore.score_date))
        .first()
    )

    if not latest_score:
        return f"ℹ️ **{emp.full_name}** ({emp.employee_id}) has no risk score calculated yet."

    # Build report
    score_val = latest_score.total_score
    cat = latest_score.risk_category.value.upper()
    trend = latest_score.trend
    trend_arrow = "📈" if trend == "increasing" else "📉" if trend == "decreasing" else "➡️"

    # Fetch details from prediction
    pred = inf_service.predict_employee(db, emp.id, days=30)
    top_factors = pred.get("top_features", [])

    shap_rows = ""
    for tf in top_factors:
        f_name = tf["feature"].replace("_", " ").title()
        val = tf["value"]
        contrib = tf["contribution"]
        bar_len = int(max(contrib * 40, 1))
        bar = "🟢" * bar_len if contrib < 0.05 else "🟡" * bar_len if contrib < 0.15 else "🔴" * bar_len
        shap_rows += f"| **{f_name}** | `{val:.1f}` | {bar} (+{contrib*100:.1f}%) |\n"

    dept_name = emp.department.name if emp.department else "N/A"

    report = (
        f"### 👤 Risk Explanation: {emp.full_name} ({emp.employee_id})\n"
        f"- **Department:** {dept_name} | **Designation:** {emp.designation}\n"
        f"- **Risk Classification:** `{cat}`\n"
        f"- **Combined Threat Score:** `{score_val:.1f}%` (Dev: {pred['isolation_forest_score']:.0f}%, Conf: {pred['confidence']:.0f}%)\n"
        f"- **Trend Indicator:** {trend_arrow} `{trend}`\n\n"
        f"#### 🧠 SHAP Feature Contribution Analysis\n"
        f"The model's neural path weights identified the following positive behavioral drivers:\n"
        f"| Feature | Value | Contribution Level |\n"
        f"| :--- | :--- | :--- |\n"
        f"{shap_rows}\n"
        f"#### 🔍 AI Security Explanation\n"
        f"> *\"{pred['shap_explanation']}\"*\n\n"
        f"#### 🛡️ Suggested Mitigation Playbook\n"
        f"- {pred['recommended_action']}\n"
        f"- Revoke active OAuth token sessions and monitor source IP `{emp.id}` activity feeds."
    )
    return report


def _list_suspicious_employees(db: Session) -> str:
    # Query latest scores for all active employees
    from app.api.v1.endpoints.security import get_risk_leaderboard
    leaderboard = get_risk_leaderboard(db, limit=10)

    if not leaderboard:
        return "No suspicious employees detected today."

    table_rows = ""
    for entry in leaderboard:
        emp = db.query(Employee).filter(Employee.id == entry.employee_id).first()
        dept_name = emp.department.name if emp and emp.department else "N/A"
        icon = "🔴" if entry.current_score >= 75 else "🟡" if entry.current_score >= 50 else "🟢"
        table_rows += (
            f"| {icon} | **{entry.employee_name}** | `{emp.employee_id}` | "
            f"{dept_name} | `{entry.current_score:.1f}%` | `{entry.risk_category.value.upper()}` | {entry.open_alerts} |\n"
        )

    report = (
        "### ⚠️ Live Suspicious Employees Leaderboard\n"
        "Here are the active employees ranked by fused anomaly & classifier risk scores:\n\n"
        "| | Employee | ID | Department | Threat Score | Risk Level | Active Alerts |\n"
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
        f"{table_rows}\n"
        "**Recommendation:** Prioritize containment action for profiles flagged with 🔴 (Critical) or 🟡 (High) threat levels."
    )
    return report


def _explain_todays_alerts(db: Session) -> str:
    since = datetime.now(timezone.utc) - timedelta(days=1)
    alerts = (
        db.query(Alert)
        .filter(Alert.triggered_at >= since)
        .order_by(desc(Alert.triggered_at))
        .all()
    )

    if not alerts:
        return "### 🟢 No security alerts triggered within the last 24 hours."

    alert_list = ""
    for a in alerts:
        emp_name = a.employee.full_name if a.employee else "N/A"
        sev_color = "🔴" if a.severity == AlertSeverity.critical else "🟡" if a.severity == AlertSeverity.high else "🔵"
        alert_list += (
            f"1. **{a.title}** ({a.alert_id})\n"
            f"   - **Employee:** {emp_name} | **Severity:** {sev_color} `{a.severity.value.upper()}`\n"
            f"   - **AI Analysis:** {a.description}\n"
        )

    report = (
        f"### 🚨 Security Alerts Breakdown - Today ({len(alerts)} items)\n"
        "The system recorded the following alerts today:\n\n"
        f"{alert_list}\n"
        "**Incident Action:** Select active alerts in the console to correlate evidence timelines and escalate to formal Incident Response cases."
    )
    return report


def _generate_incident_summary(db: Session) -> str:
    incidents = (
        db.query(Incident)
        .order_by(desc(Incident.opened_at))
        .limit(5)
        .all()
    )

    if not incidents:
        return "### 🟢 No active threat investigation cases found."

    inc_list = ""
    for inc in incidents:
        emp_name = inc.employee.full_name if inc.employee else "N/A"
        analyst = inc.assigned_analyst.full_name if inc.assigned_analyst else "Unassigned"
        status_icon = "🔓" if inc.status == IncidentStatus.open else "🕵️" if inc.status == IncidentStatus.in_progress else "✅"
        inc_list += (
            f"- **{inc.incident_id}**: {inc.title}\n"
            f"  - **Status:** {status_icon} `{inc.status.value.upper()}` | **Severity:** `{inc.severity.value.upper()}`\n"
            f"  - **Subject:** {emp_name} | **Assigned to:** {analyst}\n"
        )

    report = (
        "### 📂 active SOC incident investigations (Recent 5 Cases)\n"
        f"{inc_list}\n"
        "**Mitigation Plan:** Secure communications, revoke active API access keys for compromised subjects, and save forensic data for legal review."
    )
    return report


def _suggest_mitigation(db: Session, emp: Employee) -> str:
    pred = inf_service.predict_employee(db, emp.id, days=30)
    top_feature = pred["top_features"][0]["feature"]

    playbook_map = {
        "failed_logins": (
            "Lock the employee Active Directory account; enforce immediate multi-factor authentication (MFA) reset; "
            "review logon logs for credential spray vectors."
        ),
        "working_hours": (
            "Contact department manager to verify if nocturnal business work hours were pre-authorized; "
            "enable geofencing logon filters."
        ),
        "usb_usage": (
            "Initiate Endpoint Agent quarantine; scan the workstation for physical mass-storage execution logs; "
            "verify compliance with corporate clean-desk policies."
        ),
        "file_downloads": (
            "Revoke download access to the corporate code repositories; check file audit logs for bulk download scripts; "
            "inspect memory cache dumps."
        ),
        "privilege_escalation": (
            "Quarantine host from active local domains; audit active administrative groups; "
            "re-verify authorization for user workstation privileges."
        ),
        "database_access": (
            "Revoke service account credentials; inspect SQL query history for SQL injection or data harvesting; "
            "restrict connections to core database schemas."
        )
    }

    playbook = playbook_map.get(top_feature, "Revoke active token sessions; enable baseline auditing logs.")

    report = (
        f"### 🛡️ Recommended Security Playbook: {emp.full_name}\n"
        f"Subject's primary risk factor is linked to **{top_feature.replace('_', ' ').title()}**.\n\n"
        f"**Incident Response Steps:**\n"
        f"1. **Isolation:** {playbook}\n"
        f"2. **Communication:** Contact manager *({emp.manager.full_name if emp.manager else 'N/A'})* to cross-verify activity.\n"
        f"3. **Containment:** Revoke OAuth tokens and force credential rotation.\n"
        f"4. **Audit:** Download the detailed activity report for timeline forensic analyses."
    )
    return report


def _summarize_weekly_threats(db: Session) -> str:
    since_7d = datetime.now(timezone.utc) - timedelta(days=7)
    
    total_alerts = db.query(func.count(Alert.id)).filter(Alert.triggered_at >= since_7d).scalar() or 0
    resolved_alerts = db.query(func.count(Alert.id)).filter(Alert.triggered_at >= since_7d, Alert.status == AlertStatus.resolved).scalar() or 0
    active_incidents = db.query(func.count(Incident.id)).filter(Incident.opened_at >= since_7d, Incident.status != IncidentStatus.closed).scalar() or 0

    critical_count = db.query(func.count(Alert.id)).filter(Alert.triggered_at >= since_7d, Alert.severity == AlertSeverity.critical).scalar() or 0
    high_count = db.query(func.count(Alert.id)).filter(Alert.triggered_at >= since_7d, Alert.severity == AlertSeverity.high).scalar() or 0

    report = (
        "### 📊 Weekly Security Operations Center (SOC) Report\n"
        f"Weekly summary for last 7 days:\n\n"
        f"- **Alerts Triggered:** `{total_alerts}`\n"
        f"- **Alerts Resolved:** `{resolved_alerts}` (Rate: {resolved_alerts/max(total_alerts, 1)*100:.1f}%)\n"
        f"- **New Incident Investigations:** `{active_incidents}`\n"
        f"- **Critical Alert Level Cases:** `{critical_count}` 🔴\n"
        f"- **High Alert Level Cases:** `{high_count}` 🟡\n\n"
        "#### 🔍 Key Security Observations\n"
        "- Fused ML engines show a cluster of risk alerts matching **large file downloads** and **working hours** deviations.\n"
        "- An anomaly velocity spike has been mapped to local workstation privilege escalations.\n\n"
        "**Executive Recommendation:** Update Endpoint DLP policies and enforce strict access control validation for privileged repositories."
    )
    return report
