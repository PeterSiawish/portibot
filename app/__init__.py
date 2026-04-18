from flask import Flask
from google import genai
from google.genai.types import HttpOptions
from sentence_transformers import SentenceTransformer

from app.services.job_embedding_cache import preload_jobs
from app.utilities.session_db import init_db, close_db

# Import all blueprints
from app.routes.home import home
from app.routes.upload import upload
from app.routes.results import results
from app.routes.preview import preview


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile("config.py")

    app.gemini_client = genai.Client(
        api_key=app.config.get("GEMINI_API_KEY"),
        http_options=HttpOptions(retry_options=app.config.get("GEMINI_RETRY_CONFIG")),
    )
    app.embedding_model = SentenceTransformer(app.config.get("EMBEDDING_MODEL_PATH"))

    with app.app_context():
        preload_jobs(app, app.embedding_model)

        init_db()
        app.teardown_appcontext(close_db)

    app.register_blueprint(home)
    app.register_blueprint(upload)
    app.register_blueprint(results)
    app.register_blueprint(preview)

    return app
