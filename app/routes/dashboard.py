from flask import Blueprint
from flask import render_template

dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/dashboard")
def home():

    return render_template("dashboard.html")