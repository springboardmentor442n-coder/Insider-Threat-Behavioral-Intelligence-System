from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.extensions import db
from app.models import Employee, Prediction, RiskIndicator

from ml.predict import predict_employee


prediction = Blueprint(
    "prediction",
    __name__,
    url_prefix="/prediction"
)


@prediction.route("/", methods=["GET", "POST"])
@login_required
def prediction_page():

    # =====================================================
    # GET
    # =====================================================

    if request.method == "GET":

        employee_id = request.args.get(
            "employee_id",
            ""
        ).strip()

        employee = None

        if employee_id:

            try:
                employee = Employee.query.get(
                    int(employee_id)
                )

            except (ValueError, TypeError):
                employee = None

        return render_template(
            "manual_prediction.html",
            employee=employee
        )


    # =====================================================
    # POST
    # =====================================================

    try:

        # -------------------------------------------------
        # Employee information
        # -------------------------------------------------

        employee_id = request.form.get(
            "employee_id",
            ""
        ).strip()

        department = request.form.get(
            "department",
            ""
        ).strip()

        role = request.form.get(
            "role",
            ""
        ).strip()

        business_unit = request.form.get(
            "business_unit",
            ""
        ).strip()


        if not employee_id:

            flash(
                "Employee ID is required.",
                "danger"
            )

            return redirect(
                url_for(
                    "prediction.prediction_page"
                )
            )


        # -------------------------------------------------
        # Helper for numeric fields
        # -------------------------------------------------

        def get_float(name):

            value = request.form.get(
                name,
                "0"
            )

            if value is None or value.strip() == "":
                return 0.0

            return float(value)


        # =================================================
        # CREATE EMPLOYEE DATA FOR ML
        # =================================================

        employee_data = {

            "department": department,
            "role": role,
            "business_unit": business_unit,

            # LOGIN
            "login_count": get_float("login_count"),
            "logoff_count": get_float("logoff_count"),
            "night_login_count": get_float("night_login_count"),
            "weekend_login_count": get_float("weekend_login_count"),
            "unique_pc_count": get_float("unique_pc_count"),
            "night_login_ratio": get_float("night_login_ratio"),
            "weekend_login_ratio": get_float("weekend_login_ratio"),
            "pc_switching_frequency": get_float(
                "pc_switching_frequency"
            ),

            # USB
            "usb_connect_count": get_float(
                "usb_connect_count"
            ),
            "usb_disconnect_count": get_float(
                "usb_disconnect_count"
            ),
            "usb_total_activity": get_float(
                "usb_total_activity"
            ),
            "usb_connect_ratio": get_float(
                "usb_connect_ratio"
            ),

            # FILE
            "file_copy_count": get_float(
                "file_copy_count"
            ),
            "avg_daily_file_copy": get_float(
                "avg_daily_file_copy"
            ),
            "max_daily_file_copy": get_float(
                "max_daily_file_copy"
            ),

            # EMAIL
            "email_sent_count": get_float(
                "email_sent_count"
            ),
            "external_email_count": get_float(
                "external_email_count"
            ),
            "avg_attachment_count": get_float(
                "avg_attachment_count"
            ),
            "avg_email_size": get_float(
                "avg_email_size"
            ),
            "external_email_ratio": get_float(
                "external_email_ratio"
            ),

            # WEB
            "website_visit_count": get_float(
                "website_visit_count"
            ),
            "unique_domain_count": get_float(
                "unique_domain_count"
            ),
            "avg_daily_web_activity": get_float(
                "avg_daily_web_activity"
            ),

            # PERSONALITY
            "O": get_float("O"),
            "C": get_float("C"),
            "E": get_float("E"),
            "A": get_float("A"),
            "N": get_float("N")
        }


        # =================================================
        # RUN MACHINE LEARNING PREDICTION
        # =================================================

        result = predict_employee(
            employee_data
        )


        # =================================================
        # NORMALIZE ML PREDICTION
        # =================================================
        #
        # The ML function may return:
        #
        #     1
        #     "1"
        #     True
        #     "THREAT"
        #
        # or
        #
        #     0
        #     "0"
        #     False
        #     "NORMAL"
        #
        # We always convert it to:
        #
        #     THREAT
        #     NORMAL
        #
        # =================================================

        raw_status = result.get("status")

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

            prediction_status = "THREAT"

        elif status_value in [
            0,
            "0",
            False,
            "NORMAL"
        ]:

            prediction_status = "NORMAL"

        else:

            raise ValueError(
                f"Invalid prediction status returned by ML model: "
                f"{raw_status}"
            )


        # Make sure the result page also receives
        # the normalized prediction.

        result["status"] = prediction_status


        # =================================================
        # FIND OR CREATE EMPLOYEE
        # =================================================

        employee = Employee.query.filter_by(
            employee_id=employee_id
        ).first()


        if employee is None:

            employee = Employee(

                employee_id=employee_id,

                department=department,

                role=role,

                business_unit=business_unit,

                login_count=employee_data[
                    "login_count"
                ],

                logoff_count=employee_data[
                    "logoff_count"
                ],

                night_login_count=employee_data[
                    "night_login_count"
                ],

                weekend_login_count=employee_data[
                    "weekend_login_count"
                ],

                unique_pc_count=employee_data[
                    "unique_pc_count"
                ],

                night_login_ratio=employee_data[
                    "night_login_ratio"
                ],

                weekend_login_ratio=employee_data[
                    "weekend_login_ratio"
                ],

                pc_switching_frequency=employee_data[
                    "pc_switching_frequency"
                ],

                usb_connect_count=employee_data[
                    "usb_connect_count"
                ],

                usb_disconnect_count=employee_data[
                    "usb_disconnect_count"
                ],

                usb_total_activity=employee_data[
                    "usb_total_activity"
                ],

                usb_connect_ratio=employee_data[
                    "usb_connect_ratio"
                ],

                file_copy_count=employee_data[
                    "file_copy_count"
                ],

                avg_daily_file_copy=employee_data[
                    "avg_daily_file_copy"
                ],

                max_daily_file_copy=employee_data[
                    "max_daily_file_copy"
                ],

                email_sent_count=employee_data[
                    "email_sent_count"
                ],

                external_email_count=employee_data[
                    "external_email_count"
                ],

                avg_attachment_count=employee_data[
                    "avg_attachment_count"
                ],

                avg_email_size=employee_data[
                    "avg_email_size"
                ],

                external_email_ratio=employee_data[
                    "external_email_ratio"
                ],

                website_visit_count=employee_data[
                    "website_visit_count"
                ],

                unique_domain_count=employee_data[
                    "unique_domain_count"
                ],

                avg_daily_web_activity=employee_data[
                    "avg_daily_web_activity"
                ],

                O=employee_data["O"],
                C=employee_data["C"],
                E=employee_data["E"],
                A=employee_data["A"],
                N=employee_data["N"]
            )

            db.session.add(
                employee
            )

            db.session.flush()

        else:

            # ---------------------------------------------
            # UPDATE EMPLOYEE INFORMATION
            # ---------------------------------------------

            employee.department = department
            employee.role = role
            employee.business_unit = business_unit

            employee.login_count = employee_data[
                "login_count"
            ]

            employee.logoff_count = employee_data[
                "logoff_count"
            ]

            employee.night_login_count = employee_data[
                "night_login_count"
            ]

            employee.weekend_login_count = employee_data[
                "weekend_login_count"
            ]

            employee.unique_pc_count = employee_data[
                "unique_pc_count"
            ]

            employee.night_login_ratio = employee_data[
                "night_login_ratio"
            ]

            employee.weekend_login_ratio = employee_data[
                "weekend_login_ratio"
            ]

            employee.pc_switching_frequency = employee_data[
                "pc_switching_frequency"
            ]

            employee.usb_connect_count = employee_data[
                "usb_connect_count"
            ]

            employee.usb_disconnect_count = employee_data[
                "usb_disconnect_count"
            ]

            employee.usb_total_activity = employee_data[
                "usb_total_activity"
            ]

            employee.usb_connect_ratio = employee_data[
                "usb_connect_ratio"
            ]

            employee.file_copy_count = employee_data[
                "file_copy_count"
            ]

            employee.avg_daily_file_copy = employee_data[
                "avg_daily_file_copy"
            ]

            employee.max_daily_file_copy = employee_data[
                "max_daily_file_copy"
            ]

            employee.email_sent_count = employee_data[
                "email_sent_count"
            ]

            employee.external_email_count = employee_data[
                "external_email_count"
            ]

            employee.avg_attachment_count = employee_data[
                "avg_attachment_count"
            ]

            employee.avg_email_size = employee_data[
                "avg_email_size"
            ]

            employee.external_email_ratio = employee_data[
                "external_email_ratio"
            ]

            employee.website_visit_count = employee_data[
                "website_visit_count"
            ]

            employee.unique_domain_count = employee_data[
                "unique_domain_count"
            ]

            employee.avg_daily_web_activity = employee_data[
                "avg_daily_web_activity"
            ]

            employee.O = employee_data["O"]
            employee.C = employee_data["C"]
            employee.E = employee_data["E"]
            employee.A = employee_data["A"]
            employee.N = employee_data["N"]


        # =================================================
        # CREATE PREDICTION RECORD
        # =================================================

        prediction_record = Prediction(

            employee_id=employee.id,

            # IMPORTANT:
            # Always save THREAT / NORMAL
            prediction=prediction_status,

            # IMPORTANT:
            # Also save normalized value here.
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

                prediction_id=prediction_record.id,

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
        # COMMIT EVERYTHING
        # =================================================

        db.session.commit()


        # =================================================
        # DISPLAY RESULT
        # =================================================

        return render_template(

            "prediction_result.html",

            result=result,

            employee=employee,

            prediction=prediction_record

        )


    except ValueError:

        db.session.rollback()

        flash(
            "Please enter valid numeric values in all numerical fields.",
            "danger"
        )

        return redirect(
            url_for(
                "prediction.prediction_page"
            )
        )


    except Exception as e:

        db.session.rollback()

        import traceback

        print()
        print("=" * 80)
        print("PREDICTION ERROR")
        print("=" * 80)

        traceback.print_exc()

        print("=" * 80)
        print()

        raise