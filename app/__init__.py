from flask import Flask
from google import genai
from google.genai.types import HttpOptions
from sentence_transformers import SentenceTransformer
from flask_apscheduler import APScheduler
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

from app.services.job_embedding_cache import preload_jobs
from app.utilities.session_db import init_db, close_db
from app.utilities.session_handling import cleanup_expired_sessions

# Import all blueprints
from app.routes.home import home
from app.routes.upload import upload
from app.routes.results import results
from app.routes.preview import preview

# Initialize the scheduler for session cleanup
scheduler = APScheduler()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile("config.py")

    app.gemini_client = genai.Client(
        api_key=app.config.get("GEMINI_API_KEY"),
        http_options=HttpOptions(retry_options=app.config.get("GEMINI_RETRY_CONFIG")),
    )
    app.embedding_model = SentenceTransformer(app.config.get("EMBEDDING_MODEL_PATH"))

    app.analyzer = AnalyzerEngine()
    app.anonymizer = AnonymizerEngine()

    app.teardown_appcontext(close_db)

    with app.app_context():
        preload_jobs(app, app.embedding_model)

        init_db()

    app.register_blueprint(home)
    app.register_blueprint(upload)
    app.register_blueprint(results)
    app.register_blueprint(preview)

    # Ensure scheduler runs in app context
    def scheduled_cleanup():
        with app.app_context():
            cleanup_expired_sessions()

    scheduler.init_app(app)
    scheduler.add_job(
        id="session_cleanup",
        func=scheduled_cleanup,
        trigger="interval",
        minutes=10,
        replace_existing=True,
    )

    scheduler.start()

    return app
