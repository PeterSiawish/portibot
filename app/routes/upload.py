from flask import Blueprint, render_template, request, current_app

from app.utilities.cv_upload_utils import validate_file
from app.services.file_services import save_file, delete_file
from app.services.cv_services import extract_text
from app.services.text_processing_service import clean_text
from app.services.skill_extraction import extract_skills
from app.services.skill_comparison import full_comparison
from app.services.auto_service import run_auto_match
from app.services.cv_embedding import embed_cv_data
from app.services.evaluation_service import evaluate

from app.services.job_embedding_cache import JOB_DATA, JOB_EMBEDDINGS

upload = Blueprint("upload", __name__)


@upload.route("/upload", methods=["GET", "POST"])
def upload_page():
    if request.method == "POST":
        file = request.files.get("cv")
        role = request.form.get("role")

        is_valid, message = validate_file(file)

        if not is_valid:
            return render_template("error.html", message=message)

        file_path = save_file(file)

        text = extract_text(file_path)

        delete_file(file_path)

        text = clean_text(text)

        gemini_client = current_app.gemini_client
        cv_data = extract_skills(text, gemini_client)

        embedded_cv_data = embed_cv_data(cv_data, model=current_app.embedding_model)

        if role != "auto":
            embedded_job_data = JOB_EMBEDDINGS[role]
            job_data = JOB_DATA[role]

            results = full_comparison(
                cv_data, embedded_cv_data, job_data, embedded_job_data, role
            )

            evaluation = evaluate(results, gemini_client)

            return f"Successfully received file: {file.filename}<hr>{cv_data}<hr>{job_data}<hr>{results}<hr>{evaluation}"
        else:
            results = run_auto_match(
                cv_data, embedded_cv_data, JOB_DATA, JOB_EMBEDDINGS
            )

            return f"Successfully received file: {file.filename}<hr>{cv_data}<hr>{results}<hr>{JOB_DATA}"

    if request.method == "GET":
        return render_template("upload.html")
