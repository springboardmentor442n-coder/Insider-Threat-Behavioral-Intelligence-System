from flask import Blueprint
from flask import render_template

history = Blueprint("history", __name__)


@history.route("/history")
def history_page():

    return render_template("history.html")