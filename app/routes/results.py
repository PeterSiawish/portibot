from flask import Blueprint, render_template
from app.utilities.session_handling import get_session


results = Blueprint("results", __name__)


@results.route("/results/<session_id>")
def show_results(session_id):
    data = get_session(session_id)

    if not data:
        return render_template("error.html", message="Session Expired.")

    if data["role"] == "auto":
        return render_template(
            "results_auto.html",
            evaluation=data["evaluation"],
            session_id=session_id,
        )
    else:
        return render_template(
            "results_role.html",
            evaluation=data["evaluation"],
            session_id=session_id,
        )
