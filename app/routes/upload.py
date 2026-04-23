from flask import Blueprint, render_template, request, current_app, redirect, url_for

from app.utilities.cv_upload_utils import validate_file
from app.utilities.session_handling import create_session
from app.services.file_services import save_file, delete_file
from app.services.cv_services import extract_text
from app.services.text_processing_service import clean_text
from app.services.skill_extraction import extract_skills
from app.services.skill_comparison import full_comparison
from app.services.auto_service import run_auto_match
from app.services.cv_embedding import embed_cv_data
from app.services.evaluation_service import evaluate_role, evaluate_auto
from app.services.portfolio_generation import generate_portfolio
from app.services.hide_pii import redact_cv

from app.services.job_embedding_cache import JOB_DATA, JOB_EMBEDDINGS

upload = Blueprint("upload", __name__)


@upload.route("/upload", methods=["GET", "POST"])
def upload_page():
    if request.method == "POST":
        file = request.files.get("cv")
        role = request.form.get("role")
        consent = request.form.get("consent")

        if consent != "true":
            return render_template(
                "error.html", message="You must consent to the terms and conditions."
            )

        if not role:
            return render_template("error.html", message="Invalid job role selected.")

        is_valid, message = validate_file(file)

        if not is_valid:
            return render_template("error.html", message=message)

        file_path = save_file(file)
        try:
            text = extract_text(file_path)

            if text is None:
                return render_template(
                    "error.html",
                    message="Unsupported file type after upload. Use PDF or DOCX.",
                )

            # Redact PII from the CV text
            text, first_name = redact_cv(
                text, current_app.analyzer, current_app.anonymizer
            )

            # Basic text cleaning
            text = clean_text(text)

            gemini_client = current_app.gemini_client
            cv_data = extract_skills(text, gemini_client)
            cv_data["first_name"] = first_name

            embedded_cv_data = embed_cv_data(cv_data, model=current_app.embedding_model)

            if role != "auto":
                embedded_job_data = JOB_EMBEDDINGS[role]
                job_data = JOB_DATA[role]

                results = full_comparison(
                    cv_data,
                    embedded_cv_data,
                    job_data,
                    embedded_job_data,
                    role,
                    first_name,
                )

                evaluation = evaluate_role(results, gemini_client)
            else:
                results = run_auto_match(
                    cv_data, embedded_cv_data, JOB_DATA, JOB_EMBEDDINGS, first_name
                )
                evaluation = evaluate_auto(results, gemini_client)

            website = generate_portfolio(cv_data, gemini_client)

            session_data = {"evaluation": evaluation, "website": website, "role": role}

            session_id = create_session(session_data)

            return redirect(url_for("results.show_results", session_id=session_id))
        except RuntimeError as e:
            return render_template("error.html", message=str(e))
        except Exception:
            current_app.logger.exception("Upload pipeline failed")
            return render_template(
                "error.html",
                message="Something went wrong while processing your CV. Please try again.",
            )
        finally:
            delete_file(file_path)

    if request.method == "GET":
        return render_template("upload.html")
