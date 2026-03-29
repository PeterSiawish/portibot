from flask import Flask

# Import all blueprints
from app.routes.home import home
from app.routes.upload import upload


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_pyfile("config.py")

    app.register_blueprint(home)
    app.register_blueprint(upload)

    return app
