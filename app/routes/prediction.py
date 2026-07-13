from flask import Blueprint
from flask import render_template

prediction = Blueprint("prediction", __name__)


@prediction.route("/prediction")
def prediction_page():

    return render_template("prediction.html")