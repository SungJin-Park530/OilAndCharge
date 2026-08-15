from flask import Flask

from app.config import Config
from app.fuel.routes import fuel_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(fuel_bp)

    return app
