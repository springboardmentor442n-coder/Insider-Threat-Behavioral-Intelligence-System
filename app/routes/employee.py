from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)
from app.models import Employee, Prediction
from flask_login import login_required

from app.extensions import db
from app.models import Employee


employee = Blueprint(
    "employee",
    __name__,
    url_prefix="/employees"
)


# =========================================================
# EMPLOYEE LIST
# =========================================================

@employee.route("/")
@login_required
def employees():

    employees = Employee.query.order_by(
        Employee.created_at.desc()
    ).all()

    employee_rows = []

    for emp in employees:

        latest_prediction = None

        if emp.predictions:

            latest_prediction = max(
                emp.predictions,
                key=lambda p: p.created_at
            )

        employee_rows.append({
            "employee": emp,
            "prediction": latest_prediction
        })

    return render_template(
        "employee.html",
        employee_rows=employee_rows
    )


# =========================================================
# ADD EMPLOYEE
# =========================================================

@employee.route("/add", methods=["GET", "POST"])
@login_required
def add_employee():

    if request.method == "POST":

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
                url_for("employee.add_employee")
            )


        existing_employee = Employee.query.filter_by(
            employee_id=employee_id
        ).first()


        if existing_employee:

            flash(
                "Employee ID already exists.",
                "danger"
            )

            return redirect(
                url_for("employee.add_employee")
            )


        new_employee = Employee(

            employee_id=employee_id,

            department=department,

            role=role,

            business_unit=business_unit
        )


        db.session.add(new_employee)

        db.session.commit()


        flash(
            "Employee added successfully.",
            "success"
        )


        return redirect(
            url_for("employee.employees")
        )


    return render_template(
        "employee_details.html"
    )


# =========================================================
# EMPLOYEE DETAILS
# =========================================================
@employee.route("/<int:employee_id>")
@login_required
def employee_details(employee_id):

    employee_record = Employee.query.get_or_404(
        employee_id
    )

    latest_prediction = Prediction.query.filter_by(
        employee_id=employee_record.id
    ).order_by(
        Prediction.created_at.desc()
    ).first()

    return render_template(
        "employee_details.html",
        employee=employee_record,
        latest_prediction=latest_prediction
    )

# =========================================================
# DELETE EMPLOYEE
# =========================================================

@employee.route(
    "/<int:employee_id>/delete",
    methods=["POST"]
)
@login_required
def delete_employee(employee_id):

    employee_record = Employee.query.get_or_404(
        employee_id
    )


    db.session.delete(
        employee_record
    )

    db.session.commit()


    flash(
        "Employee deleted successfully.",
        "success"
    )


    return redirect(
        url_for("employee.employees")
    )