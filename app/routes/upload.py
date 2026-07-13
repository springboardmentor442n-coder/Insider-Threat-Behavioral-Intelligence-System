from flask import Blueprint
from flask import render_template

upload = Blueprint("upload", __name__)


@upload.route("/upload")
def upload_page():

    return render_template("upload.html")