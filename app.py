from flask import Flask, render_template, request
from ml.predict import predict_employee

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def analyst():

    result = None
    employee = {}

    if request.method == "POST":

        employee = {

            "department": request.form.get(
                "department", "Unknown"
            ),

            "role": request.form.get(
                "role", "Unknown"
            ),

            "business_unit": request.form.get(
                "business_unit", 1
            ),

            "login_count": float(
                request.form.get("login_count", 0)
            ),

            "logoff_count": float(
                request.form.get("logoff_count", 0)
            ),

            "night_login_count": float(
                request.form.get("night_login_count", 0)
            ),

            "weekend_login_count": float(
                request.form.get("weekend_login_count", 0)
            ),

            "unique_pc_count": float(
                request.form.get("unique_pc_count", 0)
            ),

            "night_login_ratio": float(
                request.form.get("night_login_ratio", 0)
            ),

            "weekend_login_ratio": float(
                request.form.get("weekend_login_ratio", 0)
            ),

            "pc_switching_frequency": float(
                request.form.get(
                    "pc_switching_frequency", 0
                )
            ),

            "usb_connect_count": float(
                request.form.get(
                    "usb_connect_count", 0
                )
            ),

            "usb_disconnect_count": float(
                request.form.get(
                    "usb_disconnect_count", 0
                )
            ),

            "usb_total_activity": float(
                request.form.get(
                    "usb_total_activity", 0
                )
            ),

            "usb_connect_ratio": float(
                request.form.get(
                    "usb_connect_ratio", 0
                )
            ),

            "file_copy_count": float(
                request.form.get(
                    "file_copy_count", 0
                )
            ),

            "avg_daily_file_copy": float(
                request.form.get(
                    "avg_daily_file_copy", 0
                )
            ),

            "max_daily_file_copy": float(
                request.form.get(
                    "max_daily_file_copy", 0
                )
            ),

            "email_sent_count": float(
                request.form.get(
                    "email_sent_count", 0
                )
            ),

            "external_email_count": float(
                request.form.get(
                    "external_email_count", 0
                )
            ),

            "avg_attachment_count": float(
                request.form.get(
                    "avg_attachment_count", 0
                )
            ),

            "avg_email_size": float(
                request.form.get(
                    "avg_email_size", 0
                )
            ),

            "external_email_ratio": float(
                request.form.get(
                    "external_email_ratio", 0
                )
            ),

            "website_visit_count": float(
                request.form.get(
                    "website_visit_count", 0
                )
            ),

            "unique_domain_count": float(
                request.form.get(
                    "unique_domain_count", 0
                )
            ),

            "avg_daily_web_activity": float(
                request.form.get(
                    "avg_daily_web_activity", 0
                )
            ),

            "O": float(
                request.form.get("O", 0)
            ),

            "C": float(
                request.form.get("C", 0)
            ),

            "E": float(
                request.form.get("E", 0)
            ),

            "A": float(
                request.form.get("A", 0)
            ),

            "N": float(
                request.form.get("N", 0)
            )
        }

        result = predict_employee(
            employee
        )

    return render_template(
        "analyst.html",
        result=result,
        employee=employee
    )


if __name__ == "__main__":

    app.run(
        debug=True
    )