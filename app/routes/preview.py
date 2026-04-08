from flask import Blueprint, render_template

from app.utilities.session_handling import get_session


preview = Blueprint("preview", __name__)


@preview.route("/preview/<session_id>")
def preview_portfolio(session_id):
    data = get_session(session_id)

    if not data:
        return render_template("error.html", message="Session Expired.")

    return render_template("preview_portfolio.html", session_id=session_id)


@preview.route("/preview/content/<session_id>")
def portfolio_endpoint(session_id):
    data = get_session(session_id)

    if not data:
        return render_template("error.html", message="Invalid Session.")

    html = data["website"]["html_code"]

    return html
