from flask import Flask
from google import genai

# Import all blueprints
from app.routes.home import home
from app.routes.upload import upload


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_pyfile("config.py")

    app.gemini_client = genai.Client(api_key=app.config.get("GEMINI_API_KEY"))

    app.register_blueprint(home)
    app.register_blueprint(upload)

    return app
