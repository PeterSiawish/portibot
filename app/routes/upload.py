from flask import Blueprint, render_template, request

from app.utilities.cv_upload_utils import validate_file
from app.services.file_services import save_file, delete_file
from app.services.cv_services import extract_text

upload = Blueprint("upload", __name__)


@upload.route("/upload", methods=["GET", "POST"])
def upload_page():
    if request.method == "POST":
        file = request.files.get("cv")

        is_valid, message = validate_file(file)

        if not is_valid:
            return message

        file_path = save_file(file)

        text = extract_text(file_path)

        delete_file(file_path)

        return f"Successfully received file: {file.filename} => {text}"

    if request.method == "GET":
        return render_template("upload.html")
