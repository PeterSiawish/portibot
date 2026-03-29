from flask import Blueprint, render_template, request, redirect, url_for

upload = Blueprint("upload", __name__)


@upload.route("/upload", methods=["GET", "POST"])
def upload_page():
    if request.method == "POST":
        file = request.files.get("cv")

        if not file:
            # Implement error pages later
            return "No file uploaded"

        return f"Received file: {file.filename}"
    if request.method == "GET":
        return render_template("upload.html")
