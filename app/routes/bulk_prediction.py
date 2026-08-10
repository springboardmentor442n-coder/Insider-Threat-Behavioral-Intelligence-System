import io
import csv

import pandas as pd

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file
)

from flask_login import login_required

from app.extensions import db
from app.models import Employee, Prediction, RiskIndicator

from ml.predict import predict_employee


bulk_prediction = Blueprint(
    "bulk_prediction",
    __name__,
    url_prefix="/bulk-analysis"
)


# =========================================================
# CSV COLUMNS
# =========================================================

CSV_COLUMNS = [
    "employee_id",

    "department",
    "role",
    "business_unit",

    "login_count",
    "logoff_count",

    "night_login_count",
    "weekend_login_count",

    "unique_pc_count",

    "night_login_ratio",
    "weekend_login_ratio",

    "pc_switching_frequency",

    "usb_connect_count",
    "usb_disconnect_count",
    "usb_total_activity",
    "usb_connect_ratio",

    "file_copy_count",
    "avg_daily_file_copy",
    "max_daily_file_copy",

    "email_sent_count",
    "external_email_count",
    "avg_attachment_count",
    "avg_email_size",
    "external_email_ratio",

    "website_visit_count",
    "unique_domain_count",
    "avg_daily_web_activity",

    "O",
    "C",
    "E",
    "A",
    "N"
]


# =========================================================
# NUMERIC COLUMNS
# =========================================================
# IMPORTANT:
# business_unit is NOT here because it is a String field.

NUMERIC_COLUMNS = [
    "login_count",
    "logoff_count",

    "night_login_count",
    "weekend_login_count",

    "unique_pc_count",

    "night_login_ratio",
    "weekend_login_ratio",

    "pc_switching_frequency",

    "usb_connect_count",
    "usb_disconnect_count",
    "usb_total_activity",
    "usb_connect_ratio",

    "file_copy_count",
    "avg_daily_file_copy",
    "max_daily_file_copy",

    "email_sent_count",
    "external_email_count",
    "avg_attachment_count",
    "avg_email_size",
    "external_email_ratio",

    "website_visit_count",
    "unique_domain_count",
    "avg_daily_web_activity",

    "O",
    "C",
    "E",
    "A",
    "N"
]


# =========================================================
# NORMALIZE PREDICTION STATUS
# =========================================================

def normalize_prediction_status(raw_status):

    if isinstance(raw_status, str):

        status_value = raw_status.strip().upper()

    else:

        status_value = raw_status


    if status_value in [
        1,
        "1",
        True,
        "THREAT"
    ]:

        return "THREAT"


    elif status_value in [
        0,
        "0",
        False,
        "NORMAL"
    ]:

        return "NORMAL"


    raise ValueError(
        f"Invalid prediction status returned by ML model: "
        f"{raw_status}"
    )


# =========================================================
# BULK ANALYSIS
# =========================================================

@bulk_prediction.route("/", methods=["GET", "POST"])
@login_required
def bulk_analysis():

    # =====================================================
    # GET
    # =====================================================

    if request.method == "GET":

        return render_template(
            "bulk_analysis.html"
        )


    # =====================================================
    # CHECK FILE
    # =====================================================

    uploaded_file = request.files.get(
        "csv_file"
    )


    if not uploaded_file:

        flash(
            "Please select a CSV file.",
            "danger"
        )

        return redirect(
            url_for(
                "bulk_prediction.bulk_analysis"
            )
        )


    if uploaded_file.filename == "":

        flash(
            "Please select a CSV file.",
            "danger"
        )

        return redirect(
            url_for(
                "bulk_prediction.bulk_analysis"
            )
        )


    if not uploaded_file.filename.lower().endswith(".csv"):

        flash(
            "Only CSV files are allowed.",
            "danger"
        )

        return redirect(
            url_for(
                "bulk_prediction.bulk_analysis"
            )
        )


    # =====================================================
    # READ CSV
    # =====================================================

    try:

        df = pd.read_csv(
            uploaded_file
        )

    except Exception as e:

        flash(
            f"Unable to read CSV file: {str(e)}",
            "danger"
        )

        return redirect(
            url_for(
                "bulk_prediction.bulk_analysis"
            )
        )


    # =====================================================
    # CLEAN COLUMN NAMES
    # =====================================================

    df.columns = [
        str(column).strip()
        for column in df.columns
    ]


    # =====================================================
    # CHECK REQUIRED COLUMNS
    # =====================================================

    missing_columns = [
        column
        for column in CSV_COLUMNS
        if column not in df.columns
    ]


    if missing_columns:

        flash(
            "Missing CSV columns: "
            + ", ".join(missing_columns),
            "danger"
        )

        return redirect(
            url_for(
                "bulk_prediction.bulk_analysis"
            )
        )


    # =====================================================
    # CHECK EMPTY FILE
    # =====================================================

    if df.empty:

        flash(
            "The CSV file does not contain any employees.",
            "danger"
        )

        return redirect(
            url_for(
                "bulk_prediction.bulk_analysis"
            )
        )


    # =====================================================
    # RESULTS
    # =====================================================

    results = []

    success_count = 0
    failed_count = 0

    threat_count = 0
    normal_count = 0
    critical_count = 0


    # =====================================================
    # PROCESS EACH EMPLOYEE
    # =====================================================

    for index, row in df.iterrows():

        row_number = index + 2


        try:

            # =================================================
            # EMPLOYEE ID
            # =================================================

            employee_id = str(
                row["employee_id"]
            ).strip()


            if not employee_id:

                raise ValueError(
                    "Employee ID is empty."
                )


            # =================================================
            # CREATE EMPLOYEE DATA
            # =================================================

            employee_data = {}


            for column in CSV_COLUMNS:

                if column == "employee_id":

                    continue


                value = row[column]


                # ---------------------------------------------
                # Missing value
                # ---------------------------------------------

                if pd.isna(value):

                    if column in NUMERIC_COLUMNS:

                        value = 0.0

                    else:

                        value = ""


                # ---------------------------------------------
                # Numeric
                # ---------------------------------------------

                if column in NUMERIC_COLUMNS:

                    try:

                        value = float(value)

                    except (
                        ValueError,
                        TypeError
                    ):

                        raise ValueError(
                            f"Invalid numeric value "
                            f"for '{column}'."
                        )


                # ---------------------------------------------
                # String
                # ---------------------------------------------

                else:

                    value = str(
                        value
                    ).strip()


                employee_data[column] = value


            # =================================================
            # RUN MACHINE LEARNING
            # =================================================

            result = predict_employee(
                employee_data
            )


            # =================================================
            # NORMALIZE STATUS
            # =================================================

            prediction_status = (
                normalize_prediction_status(
                    result.get("status")
                )
            )


            # Make sure result contains
            # normalized status.

            result["status"] = (
                prediction_status
            )


            # =================================================
            # FIND EXISTING EMPLOYEE
            # =================================================

            employee_record = (
                Employee.query
                .filter_by(
                    employee_id=employee_id
                )
                .first()
            )


            # =================================================
            # CREATE EMPLOYEE
            # =================================================

            if employee_record is None:

                employee_record = Employee(

                    employee_id=employee_id,

                    department=employee_data[
                        "department"
                    ],

                    role=employee_data[
                        "role"
                    ],

                    business_unit=employee_data[
                        "business_unit"
                    ]
                )

                db.session.add(
                    employee_record
                )


            else:

                # ---------------------------------------------
                # Update employee
                # ---------------------------------------------

                employee_record.department = (
                    employee_data["department"]
                )

                employee_record.role = (
                    employee_data["role"]
                )

                employee_record.business_unit = (
                    employee_data["business_unit"]
                )


            # =================================================
            # SAVE BEHAVIORAL FEATURES
            # =================================================

            employee_record.login_count = (
                employee_data["login_count"]
            )

            employee_record.logoff_count = (
                employee_data["logoff_count"]
            )

            employee_record.night_login_count = (
                employee_data["night_login_count"]
            )

            employee_record.weekend_login_count = (
                employee_data["weekend_login_count"]
            )

            employee_record.unique_pc_count = (
                employee_data["unique_pc_count"]
            )

            employee_record.night_login_ratio = (
                employee_data["night_login_ratio"]
            )

            employee_record.weekend_login_ratio = (
                employee_data["weekend_login_ratio"]
            )

            employee_record.pc_switching_frequency = (
                employee_data[
                    "pc_switching_frequency"
                ]
            )

            employee_record.usb_connect_count = (
                employee_data[
                    "usb_connect_count"
                ]
            )

            employee_record.usb_disconnect_count = (
                employee_data[
                    "usb_disconnect_count"
                ]
            )

            employee_record.usb_total_activity = (
                employee_data[
                    "usb_total_activity"
                ]
            )

            employee_record.usb_connect_ratio = (
                employee_data[
                    "usb_connect_ratio"
                ]
            )

            employee_record.file_copy_count = (
                employee_data[
                    "file_copy_count"
                ]
            )

            employee_record.avg_daily_file_copy = (
                employee_data[
                    "avg_daily_file_copy"
                ]
            )

            employee_record.max_daily_file_copy = (
                employee_data[
                    "max_daily_file_copy"
                ]
            )

            employee_record.email_sent_count = (
                employee_data[
                    "email_sent_count"
                ]
            )

            employee_record.external_email_count = (
                employee_data[
                    "external_email_count"
                ]
            )

            employee_record.avg_attachment_count = (
                employee_data[
                    "avg_attachment_count"
                ]
            )

            employee_record.avg_email_size = (
                employee_data[
                    "avg_email_size"
                ]
            )

            employee_record.external_email_ratio = (
                employee_data[
                    "external_email_ratio"
                ]
            )

            employee_record.website_visit_count = (
                employee_data[
                    "website_visit_count"
                ]
            )

            employee_record.unique_domain_count = (
                employee_data[
                    "unique_domain_count"
                ]
            )

            employee_record.avg_daily_web_activity = (
                employee_data[
                    "avg_daily_web_activity"
                ]
            )


            # =================================================
            # PERSONALITY
            # =================================================

            employee_record.O = (
                employee_data["O"]
            )

            employee_record.C = (
                employee_data["C"]
            )

            employee_record.E = (
                employee_data["E"]
            )

            employee_record.A = (
                employee_data["A"]
            )

            employee_record.N = (
                employee_data["N"]
            )


            # =================================================
            # FLUSH EMPLOYEE
            # =================================================

            db.session.flush()


            # =================================================
            # CREATE PREDICTION
            # =================================================

            prediction_record = Prediction(

                employee_id=employee_record.id,

                prediction=prediction_status,

                status=prediction_status,

                threat_probability=result[
                    "threat_probability"
                ],

                normal_probability=result[
                    "normal_probability"
                ],

                ml_risk_level=result[
                    "ml_risk_level"
                ],

                behavioral_risk_score=result[
                    "behavioral_risk_score"
                ],

                overall_risk_level=result[
                    "overall_risk_level"
                ],

                recommendation=result[
                    "recommendation"
                ],

                model_name=result[
                    "model"
                ]
            )


            db.session.add(
                prediction_record
            )


            db.session.flush()


            # =================================================
            # SAVE RISK INDICATORS
            # =================================================

            for indicator in result[
                "risk_indicators"
            ]:

                risk_indicator = RiskIndicator(

                    prediction_id=(
                        prediction_record.id
                    ),

                    feature=indicator[
                        "feature"
                    ],

                    value=float(
                        indicator["value"]
                    ),

                    points=float(
                        indicator["points"]
                    ),

                    severity=indicator[
                        "severity"
                    ],

                    reason=indicator[
                        "reason"
                    ]
                )


                db.session.add(
                    risk_indicator
                )


            # =================================================
            # COUNTERS
            # =================================================

            success_count += 1


            if prediction_status == "THREAT":

                threat_count += 1

            else:

                normal_count += 1


            if (
                result["overall_risk_level"]
                == "CRITICAL"
            ):

                critical_count += 1


            # =================================================
            # RESULT
            # =================================================

            results.append({

                "row": row_number,

                "employee_id": employee_id,

                "department":
                    employee_data[
                        "department"
                    ],

                "prediction":
                    prediction_status,

                "threat_probability":
                    result[
                        "threat_probability"
                    ],

                "ml_risk_level":
                    result[
                        "ml_risk_level"
                    ],

                "behavioral_risk_score":
                    result[
                        "behavioral_risk_score"
                    ],

                "overall_risk_level":
                    result[
                        "overall_risk_level"
                    ],

                "model":
                    result[
                        "model"
                    ],

                "recommendation":
                    result[
                        "recommendation"
                    ],

                "success": True

            })


            # =================================================
            # COMMIT THIS EMPLOYEE
            # =================================================

            db.session.commit()


        except Exception as e:

            # =================================================
            # ROLLBACK CURRENT EMPLOYEE
            # =================================================

            db.session.rollback()

            failed_count += 1


            results.append({

                "row": row_number,

                "employee_id":
                    str(
                        row.get(
                            "employee_id",
                            ""
                        )
                    ),

                "department":
                    str(
                        row.get(
                            "department",
                            ""
                        )
                    ),

                "prediction":
                    "-",

                "threat_probability":
                    "-",

                "ml_risk_level":
                    "-",

                "behavioral_risk_score":
                    "-",

                "overall_risk_level":
                    "-",

                "model":
                    "-",

                "recommendation":
                    str(e),

                "success": False

            })


    # =========================================================
    # SHOW RESULTS
    # =========================================================

    return render_template(

        "bulk_results.html",

        results=results,

        total_count=len(df),

        success_count=success_count,

        failed_count=failed_count,

        threat_count=threat_count,

        normal_count=normal_count,

        critical_count=critical_count
    )


# =========================================================
# DOWNLOAD CSV TEMPLATE
# =========================================================

@bulk_prediction.route(
    "/template"
)
@login_required
def download_template():

    output = io.StringIO()

    writer = csv.writer(
        output
    )


    writer.writerow(
        CSV_COLUMNS
    )


    # =====================================================
    # EXAMPLE ROW
    # =====================================================

    writer.writerow([

        "EMP1001",

        "IT",

        "Software Engineer",

        "Technology",

        20,
        18,

        2,
        1,

        3,

        0.10,
        0.05,

        0.15,

        5,
        4,
        9,
        0.55,

        10,
        5,
        12,

        30,
        4,
        1.2,
        100,
        0.13,

        200,
        50,
        100,

        0.5,
        0.6,
        0.5,
        0.7,
        0.3
    ])


    output.seek(0)


    return send_file(

        io.BytesIO(
            output.getvalue().encode(
                "utf-8"
            )
        ),

        mimetype="text/csv",

        as_attachment=True,

        download_name=(
            "employee_bulk_template.csv"
        )
    )