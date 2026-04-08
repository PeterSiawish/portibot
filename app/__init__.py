from flask import Flask
from google import genai
from google.genai.types import HttpOptions, HttpRetryOptions
from sentence_transformers import SentenceTransformer

from app.services.job_embedding_cache import preload_jobs

# Import all blueprints
from app.routes.home import home
from app.routes.upload import upload
from app.routes.results import results
from app.routes.preview import preview


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile("config.py")

    retry_config = HttpRetryOptions(
        attempts=4,
        initial_delay=2.0,
        max_delay=30.0,
        exp_base=2.0,
        jitter=1.0,
        http_status_codes=[429, 503],
    )

    app.gemini_client = genai.Client(
        api_key=app.config.get("GEMINI_API_KEY"),
        http_options=HttpOptions(retry_options=retry_config),
    )
    app.embedding_model = SentenceTransformer(app.config.get("EMBEDDING_MODEL_PATH"))

    with app.app_context():
        preload_jobs(app, app.embedding_model)

    app.register_blueprint(home)
    app.register_blueprint(upload)
    app.register_blueprint(results)
    app.register_blueprint(preview)

    return app
