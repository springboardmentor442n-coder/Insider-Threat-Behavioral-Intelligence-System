from flask import Blueprint, render_template
from flask_login import login_required

from app.extensions import db
from app.models import Employee, Prediction


dashboard = Blueprint(
    "dashboard",
    __name__
)


@dashboard.route("/dashboard")
@login_required
def home():

    # =========================================================
    # TOTAL EMPLOYEES
    # =========================================================

    total_employees = Employee.query.count()


    # =========================================================
    # LATEST PREDICTION FOR EACH EMPLOYEE
    # =========================================================

    employees = Employee.query.all()

    latest_predictions = []

    for employee in employees:

        latest_prediction = (
            Prediction.query
            .filter_by(employee_id=employee.id)
            .order_by(
                Prediction.created_at.desc(),
                Prediction.id.desc()
            )
            .first()
        )

        if latest_prediction:
            latest_predictions.append(latest_prediction)


    # =========================================================
    # EMPLOYEES ANALYZED
    # =========================================================

    employees_analyzed = len(latest_predictions)


    # =========================================================
    # HIGH RISK ALERTS
    # =========================================================

    high_risk_alerts = 0

    for prediction in latest_predictions:

        risk = (
            prediction.overall_risk_level or ""
        ).strip().upper()

        if risk in ["HIGH", "CRITICAL"]:
            high_risk_alerts += 1


    # =========================================================
    # SAFE EMPLOYEES
    # =========================================================

    safe_employees = 0

    for prediction in latest_predictions:

        risk = (
            prediction.overall_risk_level or ""
        ).strip().upper()

        if risk == "LOW":
            safe_employees += 1


    # =========================================================
    # RISK DISTRIBUTION
    # =========================================================

    risk_distribution = {
        "LOW": 0,
        "MEDIUM": 0,
        "HIGH": 0,
        "CRITICAL": 0
    }

    for prediction in latest_predictions:

        risk = (
            prediction.overall_risk_level or ""
        ).strip().upper()

        if risk in risk_distribution:
            risk_distribution[risk] += 1


    # =========================================================
    # THREAT / NORMAL COUNT
    # =========================================================

    threat_count = 0
    normal_count = 0

    for prediction in latest_predictions:

        prediction_type = (
            prediction.prediction or ""
        ).strip().upper()

        if prediction_type == "THREAT":
            threat_count += 1

        elif prediction_type == "NORMAL":
            normal_count += 1


    # =========================================================
    # AVERAGE THREAT PROBABILITY
    # =========================================================

    if latest_predictions:

        probabilities = [
            prediction.threat_probability or 0
            for prediction in latest_predictions
        ]

        average_threat_probability = (
            sum(probabilities) / len(probabilities)
        )

    else:

        average_threat_probability = 0


    # =========================================================
    # RECENT THREAT ANALYSES
    #
    # IMPORTANT:
    # Show only the latest prediction for each employee.
    # This prevents duplicate employees appearing in the
    # dashboard.
    # =========================================================

    recent_predictions = sorted(
        latest_predictions,
        key=lambda prediction: (
            prediction.created_at,
            prediction.id
        ),
        reverse=True
    )[:10]


    # =========================================================
    # HIGH RISK EMPLOYEES
    # =========================================================

    high_risk_predictions = []

    for prediction in latest_predictions:

        risk = (
            prediction.overall_risk_level or ""
        ).strip().upper()

        if risk in ["HIGH", "CRITICAL"]:

            high_risk_predictions.append(
                prediction
            )


    # =========================================================
    # SORT HIGH RISK EMPLOYEES
    #
    # Highest behavioral risk score first.
    # =========================================================

    high_risk_predictions.sort(
        key=lambda prediction: (
            prediction.behavioral_risk_score or 0
        ),
        reverse=True
    )


    # =========================================================
    # RENDER DASHBOARD
    # =========================================================

    return render_template(
        "dashboard.html",

        total_employees=total_employees,

        employees_analyzed=employees_analyzed,

        high_risk_alerts=high_risk_alerts,

        safe_employees=safe_employees,

        risk_distribution=risk_distribution,

        threat_count=threat_count,

        normal_count=normal_count,

        average_threat_probability=average_threat_probability,

        recent_predictions=recent_predictions,

        high_risk_predictions=high_risk_predictions
    )