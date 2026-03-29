from flask import Blueprint, render_template, request
from app.utilities.file_utils import validate_file

upload = Blueprint("upload", __name__)


@upload.route("/upload", methods=["GET", "POST"])
def upload_page():
    if request.method == "POST":
        file = request.files.get("cv")

        is_valid, message = validate_file(file)

        if not is_valid:
            return message

        return f"Successfully received file: {file.filename}"

    if request.method == "GET":
        return render_template("upload.html")
