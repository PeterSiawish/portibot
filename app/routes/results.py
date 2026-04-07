from flask import Blueprint, render_template

from app.utilities.temp_storage import get_session


results = Blueprint("results", __name__)


@results.route("/results/<session_id>")
def show_results(session_id):
    data = get_session(session_id)

    if not data:
        return render_template("error.html", message="Session Expired.")

    return render_template(
        "results.html",
        evaluation=data["evaluation"],
        session_id=session_id,
    )


@results.route("/portfolio/<session_id>")
def portfolio_preview(session_id):
    data = get_session(session_id)

    if not data:
        return render_template("error.html", message="Invalid Session.")

    html = data["website"]["html_code"]

    return html
