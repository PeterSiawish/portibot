from flask import Flask
from google import genai
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

    app.gemini_client = genai.Client(api_key=app.config.get("GEMINI_API_KEY"))
    app.embedding_model = SentenceTransformer(app.config.get("EMBEDDING_MODEL_PATH"))

    with app.app_context():
        preload_jobs(app, app.embedding_model)

    app.register_blueprint(home)
    app.register_blueprint(upload)
    app.register_blueprint(results)
    app.register_blueprint(preview)

    return app
