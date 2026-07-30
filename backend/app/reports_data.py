"""Report data layer. Spec Module 12.

One function per report type. Each pulls real data from the database and returns a
ReportDocument (see reporting.py) - it never touches PDF or Excel. That separation
is the whole design: the numbers live here, the formatting lives in the renderers,
and the five report types share both renderers.

THE FIVE REPORTS (spec):
    insider_threat_report   - the top-risk employees and their alerts
    behavioral_analytics    - organisation-wide behavioural statistics
    investigation_report    - one employee's full case file (takes a user_id)
    compliance_report       - the audit trail and alert-handling metrics
    risk_assessment_report  - organisation-wide risk posture

A NOTE ON is_insider. It is the CERT answer key. It appears in NONE of these
reports - not the org-wide ones and emphatically not the investigation case file,
for the same reason the investigation API withholds it: a report an analyst files
is part of forming a judgement, and printing the answer on it makes it theatre. In
production there is no answer key; the reports work the same way here.
"""
from __future__ import annotations

from datetime import timedelta

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from backend.app.models import (
    Alert,
    AlertSeverity,
    AlertStatus,
    AuditLog,
    Employee,
    SecurityUser,
)
from backend.app.features_models import UserBaseline
from backend.app.reporting import (
    ReportDocument,
    SummarySection,
    TableSection,
    TextSection,
)

# The severities that constitute an "actionable" alert (used in several reports).
_ACTIONABLE = (AlertSeverity.HIGH, AlertSeverity.CRITICAL)


def _sev_rank(sev: AlertSeverity) -> int:
    order = {
        AlertSeverity.CRITICAL: 5, AlertSeverity.HIGH: 4, AlertSeverity.MEDIUM: 3,
        AlertSeverity.LOW: 2, AlertSeverity.INFORMATIONAL: 1,
    }
    return order.get(sev, 0)


# ===========================================================================
# 1. INSIDER THREAT REPORT - the riskiest people, right now
# ===========================================================================

def insider_threat_report(db: Session, *, limit: int = 25, by: str = "") -> ReportDocument:
    """Top-risk employees ranked by their peak alert risk score, with the alert
    evidence behind each. The report a SOC lead scans to see who needs attention."""
    doc = ReportDocument(
        title="Insider Threat Report",
        subtitle="Highest-risk employees ranked by peak alert score",
        generated_by=by,
    )

    # peak risk score + alert count per user, most severe first
    rows = db.execute(
        select(
            Alert.user_id,
            func.max(Alert.risk_score).label("peak"),
            func.count().label("n"),
        )
        .group_by(Alert.user_id)
        .order_by(func.max(Alert.risk_score).desc())
        .limit(limit)
    ).all()

    total_alerts = db.scalar(select(func.count()).select_from(Alert)) or 0
    total_actionable = db.scalar(
        select(func.count()).select_from(Alert).where(Alert.severity.in_(_ACTIONABLE))
    ) or 0
    flagged_users = db.scalar(select(func.count(func.distinct(Alert.user_id)))) or 0

    doc.add(SummarySection("At a glance", [
        ("Employees flagged", str(flagged_users)),
        ("Total alerts", str(total_alerts)),
        ("High / critical alerts", str(total_actionable)),
        ("Shown in this report", str(len(rows))),
    ]))

    # enrich with names/departments
    table_rows = []
    for user_id, peak, n in rows:
        emp = db.get(Employee, user_id)
        table_rows.append([
            user_id,
            emp.employee_name if emp else "-",
            emp.department if emp and emp.department else "-",
            emp.role if emp and emp.role else "-",
            f"{peak:.0f}",
            str(n),
        ])

    doc.add(TableSection(
        "Ranked employees",
        ["User ID", "Name", "Department", "Role", "Peak score", "Alerts"],
        table_rows,
        note="Peak score is the highest single-day risk score this employee reached "
             "(0-100). Ranking is by peak, not volume - one very high day outranks "
             "many mild ones.",
    ))

    doc.add(TextSection(
        "How to read this",
        "Each row is an employee with at least one alert. The peak score is this "
        "person's most anomalous single day, scored against their own behavioural "
        "baseline. A high peak with few alerts is a sharp, short deviation (the "
        "signature of a one-day exfiltration); a high alert count is sustained "
        "unusual behaviour. Both warrant review - open the employee in the console "
        "for the day-by-day evidence."
    ))
    return doc


# ===========================================================================
# 2. BEHAVIORAL ANALYTICS REPORT - organisation-wide behaviour
# ===========================================================================

def behavioral_analytics_report(db: Session) -> ReportDocument:
    """Organisation-wide behavioural statistics: how the population behaves, which
    departments carry the most alert load, and the baseline coverage the whole
    system rests on."""
    doc = ReportDocument(
        title="Behavioral Analytics Report",
        subtitle="Organisation-wide behavioural statistics and baseline coverage",
    )

    n_employees = db.scalar(select(func.count()).select_from(Employee)) or 0
    n_baselines = db.scalar(select(func.count()).select_from(UserBaseline)) or 0
    ever_usb = db.scalar(
        select(func.count()).select_from(UserBaseline).where(UserBaseline.ever_used_usb.is_(True))
    ) or 0
    ever_after_hours = db.scalar(
        select(func.count()).select_from(UserBaseline)
        .where(UserBaseline.ever_worked_after_hours.is_(True))
    ) or 0

    doc.add(SummarySection("Population", [
        ("Employees", str(n_employees)),
        ("Behavioural baselines built", str(n_baselines)),
        ("Have ever used USB", f"{ever_usb} ({_pct(ever_usb, n_baselines)})"),
        ("Have ever worked after hours", f"{ever_after_hours} ({_pct(ever_after_hours, n_baselines)})"),
    ]))

    # population averages from baselines - the "normal" the system compares against
    avg = db.execute(select(
        func.avg(UserBaseline.mean_logon_count),
        func.avg(UserBaseline.mean_usb_connect),
        func.avg(UserBaseline.mean_file_events),
        func.avg(UserBaseline.mean_after_hours_logon),
    )).one()
    doc.add(TableSection(
        "Population behavioural averages",
        ["Behaviour", "Population mean (per day)"],
        [
            ["Logon count", f"{(avg[0] or 0):.2f}"],
            ["USB connections", f"{(avg[1] or 0):.3f}"],
            ["File events", f"{(avg[2] or 0):.2f}"],
            ["After-hours logons", f"{(avg[3] or 0):.3f}"],
        ],
        note="These are the averages of each employee's personal daily mean. USB "
             "and after-hours rates are low precisely because most employees never "
             "do them - which is what makes a first occurrence significant.",
    ))

    # alert load by department
    dept_rows = db.execute(
        select(Employee.department, func.count(Alert.id))
        .join(Alert, Alert.user_id == Employee.user_id)
        .group_by(Employee.department)
        .order_by(func.count(Alert.id).desc())
        .limit(15)
    ).all()
    doc.add(TableSection(
        "Alert load by department",
        ["Department", "Alerts"],
        [[d or "(unknown)", str(n)] for d, n in dept_rows],
        note="Where the alerts concentrate. A department far above the others is "
             "either a genuine hotspot or a place where the baseline needs review.",
    ))

    doc.add(TextSection(
        "Methodology",
        "Every statistic here is computed from the behavioural baselines built "
        "during each employee's training window. The system does not compare an "
        "employee to a fixed threshold; it compares them to their own history and "
        "to their department peers. That is what separates behavioural analytics "
        "from rule-based alerting: 'unusual' is defined per person, not per policy."
    ))
    return doc


# ===========================================================================
# 3. INVESTIGATION REPORT - one employee's case file
# ===========================================================================

def investigation_report(db: Session, *, user_id: str, days: int = 90) -> ReportDocument | None:
    """The full case file for one employee: identity, baseline, and the alert
    timeline. The document an analyst prints and attaches to a case.

    Returns None if the employee does not exist (the router turns that into a 404).
    """
    employee = db.get(Employee, user_id)
    if employee is None:
        return None

    doc = ReportDocument(
        title=f"Investigation Report: {user_id}",
        subtitle=f"Case file for {employee.employee_name}",
    )

    doc.add(SummarySection("Subject", [
        ("User ID", employee.user_id),
        ("Name", employee.employee_name),
        ("Role", employee.role or "-"),
        ("Department", employee.department or "-"),
        ("Team", employee.team or "-"),
        ("Supervisor", employee.supervisor or "-"),
    ]))

    baseline = db.scalar(select(UserBaseline).where(UserBaseline.user_id == user_id))
    if baseline:
        doc.add(SummarySection("Behavioural baseline", [
            ("Training days", str(baseline.training_days)),
            ("Mean logons/day", f"{baseline.mean_logon_count:.2f}"),
            ("Mean USB/day", f"{baseline.mean_usb_connect:.3f}"),
            ("Mean file events/day", f"{baseline.mean_file_events:.2f}"),
            ("Mean after-hours logons/day", f"{baseline.mean_after_hours_logon:.3f}"),
            ("Ever used USB", "yes" if baseline.ever_used_usb else "no"),
            ("Ever worked after hours", "yes" if baseline.ever_worked_after_hours else "no"),
        ]))

    # alert timeline
    alerts = list(db.scalars(
        select(Alert).where(Alert.user_id == user_id)
        .order_by(Alert.alert_date.desc()).limit(days)
    ).all())

    if alerts:
        rows = [[
            a.alert_date.isoformat(),
            a.severity.value,
            f"{a.risk_score:.0f}",
            f"{a.ml_probability:.3f}",
            a.status.value,
        ] for a in alerts]
        doc.add(TableSection(
            "Alert timeline",
            ["Date", "Severity", "Risk score", "ML probability", "Status"],
            rows,
            note=f"{len(alerts)} alert(s), newest first. Risk score is 0-100; ML "
                 f"probability is the supervised model's confidence this day is "
                 f"malicious.",
        ))
    else:
        doc.add(TextSection("Alert timeline", "No alerts on record for this employee."))

    doc.add(TextSection(
        "Assessment basis",
        "This case file deliberately does not state a verdict. It presents the "
        "subject's behaviour against their own baseline and the alerts the system "
        "raised; the judgement is the investigator's to make and record. The "
        "baseline is the crux of every entry - an alert means this employee "
        "deviated from how THEY normally behave, not from an arbitrary limit."
    ))
    return doc


# ===========================================================================
# 4. COMPLIANCE REPORT - audit trail and alert handling
# ===========================================================================

def compliance_report(db: Session, *, days: int = 90) -> ReportDocument:
    """Who did what, and how the alert queue is being handled. The report that
    answers an auditor: are alerts being triaged, and is every action attributable?"""
    doc = ReportDocument(
        title="Compliance Report",
        subtitle="Audit trail and alert-handling metrics",
    )

    # alert handling metrics
    total = db.scalar(select(func.count()).select_from(Alert)) or 0
    by_status = dict(db.execute(
        select(Alert.status, func.count()).group_by(Alert.status)
    ).all())
    resolved = (by_status.get(AlertStatus.RESOLVED_TRUE_POSITIVE, 0)
                + by_status.get(AlertStatus.RESOLVED_FALSE_POSITIVE, 0))
    open_n = total - resolved

    doc.add(SummarySection("Alert handling", [
        ("Total alerts", str(total)),
        ("Resolved", str(resolved)),
        ("Still open", str(open_n)),
        ("Resolution rate", _pct(resolved, total)),
    ]))

    # status breakdown table
    doc.add(TableSection(
        "Alerts by status",
        ["Status", "Count"],
        [[s.value.replace("_", " "), str(by_status.get(s, 0))] for s in AlertStatus],
        note="Every alert has a status, and every status change is recorded in the "
             "audit trail below - a resolution that leaves no trace is not a "
             "resolution.",
    ))

    # audit trail - action counts
    action_rows = db.execute(
        select(AuditLog.action, func.count())
        .group_by(AuditLog.action)
        .order_by(func.count().desc())
    ).all()
    doc.add(TableSection(
        "Operator actions (audit trail)",
        ["Action", "Times performed"],
        [[a, str(n)] for a, n in action_rows],
        note="Aggregate counts of every consequential operator action. The full "
             "per-event trail with timestamps and actors is available in the Audit "
             "Log view.",
    ))

    # who is active
    operators = db.execute(
        select(SecurityUser.email, SecurityUser.role, func.count(AuditLog.id))
        .outerjoin(AuditLog, AuditLog.security_user_id == SecurityUser.id)
        .group_by(SecurityUser.email, SecurityUser.role)
        .order_by(func.count(AuditLog.id).desc())
    ).all()
    doc.add(TableSection(
        "Operators",
        ["Operator", "Role", "Audited actions"],
        [[e, r.value.replace("_", " "), str(n)] for e, r, n in operators],
    ))

    doc.add(TextSection(
        "Attestation",
        "This report is generated directly from the system's audit log and alert "
        "records. Every operator action that changes an alert's state is logged "
        "with the actor's identity and a timestamp; this report aggregates those "
        "logs. It is a factual summary of activity, not an assessment of whether "
        "any individual alert was handled correctly."
    ))
    return doc


# ===========================================================================
# 5. RISK ASSESSMENT REPORT - organisation-wide posture
# ===========================================================================

def risk_assessment_report(db: Session) -> ReportDocument:
    """Organisation-wide risk posture: how alerts distribute across severity, how
    much is unresolved, and the recent trend. The executive summary a manager
    reads first."""
    doc = ReportDocument(
        title="Risk Assessment Report",
        subtitle="Organisation-wide security posture",
    )

    total = db.scalar(select(func.count()).select_from(Alert)) or 0
    by_sev = dict(db.execute(
        select(Alert.severity, func.count()).group_by(Alert.severity)
    ).all())
    crit = by_sev.get(AlertSeverity.CRITICAL, 0)
    high = by_sev.get(AlertSeverity.HIGH, 0)
    actionable = crit + high

    doc.add(SummarySection("Posture", [
        ("Total alerts", str(total)),
        ("Critical", str(crit)),
        ("High", str(high)),
        ("Actionable (high + critical)", f"{actionable} ({_pct(actionable, total)})"),
    ]))

    doc.add(TableSection(
        "Alert severity distribution",
        ["Severity", "Count", "Share"],
        [[s.value, str(by_sev.get(s, 0)), _pct(by_sev.get(s, 0), total)]
         for s in sorted(AlertSeverity, key=_sev_rank, reverse=True)],
        note="The shape of the queue. A healthy distribution is bottom-heavy - many "
             "informational, few critical. A top-heavy queue means either a real "
             "incident or a miscalibrated detector.",
    ))

    # recent trend: alerts per month over the data window
    _actionable_flag = func.sum(
        case((Alert.severity.in_(_ACTIONABLE), 1), else_=0)
    )
    trend = db.execute(
        select(
            func.date_trunc("month", Alert.alert_date).label("m"),
            func.count(),
            _actionable_flag,
        )
        .group_by("m")
        .order_by("m")
    ).all()
    if trend:
        doc.add(TableSection(
            "Monthly alert trend",
            ["Month", "Total alerts", "High + critical"],
            [[m.strftime("%Y-%m") if m else "-", str(n), str(int(a or 0))]
             for m, n, a in trend],
            note="Alert volume over the observation window, with the actionable "
                 "share called out. Rising actionable counts are the signal that "
                 "matters, independent of total noise.",
        ))

    doc.add(TextSection(
        "Interpretation",
        "This posture is built from every alert the system has raised. The "
        "actionable rate - the share of alerts that are high or critical - is the "
        "single number to watch: it is deliberately low by design, because the "
        "detector is tuned for a very low false-positive rate. A sudden rise in the "
        "actionable count, not the total, is what should prompt investigation."
    ))
    return doc


# ---------------------------------------------------------------------------
def _pct(n: int, total: int) -> str:
    if not total:
        return "0.0%"
    return f"{100.0 * n / total:.1f}%"


# The registry the router uses. Maps the URL slug to (data function, needs_user_id).
REPORTS = {
    "insider-threat": (insider_threat_report, False),
    "behavioral-analytics": (behavioral_analytics_report, False),
    "investigation": (investigation_report, True),
    "compliance": (compliance_report, False),
    "risk-assessment": (risk_assessment_report, False),
}
