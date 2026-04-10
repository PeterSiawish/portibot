from flask import Blueprint, render_template, Response

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

    website = data.get("website")
    html = website.get("html_code")

    if not html:
        return render_template("error.html", message="No portfolio available.")

    return html


@preview.route("/download/<session_id>")
def download_portfolio(session_id):
    data = get_session(session_id)

    if not data:
        return render_template("error.html", message="Invalid Session.")

    html = data.get("website", {}).get("html_code")

    if not html:
        return render_template("error.html", message="No portfolio available.")

    filename = data.get("website", {}).get("filename", "portfolio.html")

    return Response(
        html,
        mimetype="text/html",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
