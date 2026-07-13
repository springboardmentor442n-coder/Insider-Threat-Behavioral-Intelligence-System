from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session

auth = Blueprint("auth", __name__)


USERNAME = "admin"

PASSWORD = "admin123"


@auth.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        if username == USERNAME and password == PASSWORD:

            session["user"] = username

            return redirect(url_for("dashboard.home"))

        return render_template("login.html",
                               error="Invalid Username or Password")

    return render_template("login.html")


@auth.route("/logout")
def logout():

    session.clear()

    return redirect("/")