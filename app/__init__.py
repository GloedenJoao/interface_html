import os
from flask import Flask

from .database import init_database
from .routes import register_routes


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")
    database_path = os.path.join(os.path.dirname(__file__), "data", "flights.sqlite")
    app.config["DATABASE_PATH"] = database_path
    init_database(database_path)
    register_routes(app)
    return app


app = create_app()

