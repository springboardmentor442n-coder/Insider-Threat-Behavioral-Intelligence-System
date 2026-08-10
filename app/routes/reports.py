from flask import Blueprint, render_template
from flask_login import login_required

from app.models import Prediction


reports = Blueprint(
    "reports",
    __name__,
    url_prefix="/reports"
)


@reports.route("/")
@login_required
def reports_page():

    # =====================================================
    # ALL PREDICTIONS
    # =====================================================

    predictions = (
        Prediction.query
        .order_by(Prediction.created_at.desc())
        .all()
    )


    # =====================================================
    # TOTAL PREDICTIONS
    # =====================================================

    total_predictions = len(predictions)


    # =====================================================
    # THREAT / NORMAL COUNTS
    #
    # Supports both:
    #   "THREAT" / "NORMAL"
    # and older:
    #   1 / 0
    # =====================================================

    threat_predictions = 0
    normal_predictions = 0


    for prediction in predictions:

        value = prediction.prediction

        # New format
        if value == "THREAT":
            threat_predictions += 1

        elif value == "NORMAL":
            normal_predictions += 1

        # Old database format
        elif str(value) == "1":
            threat_predictions += 1

        elif str(value) == "0":
            normal_predictions += 1


    # =====================================================
    # CRITICAL PREDICTIONS
    # =====================================================

    critical_predictions = 0

    for prediction in predictions:

        if prediction.overall_risk_level == "CRITICAL":
            critical_predictions += 1


    # =====================================================
    # RENDER
    # =====================================================

    return render_template(
        "reports.html",

        predictions=predictions,

        total_predictions=total_predictions,

        threat_predictions=threat_predictions,

        normal_predictions=normal_predictions,

        critical_predictions=critical_predictions
    )