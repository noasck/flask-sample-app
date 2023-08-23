"""Main flow."""

from flask import Flask

from .utils.config import APP_NAME, Envs, config
from .utils.db import apply_migrations


def create_app() -> Flask:
    """Application factory."""
    # CREATE FLASK APPLICATION
    app = Flask(APP_NAME)
    app.config.update(
        DEBUG=config.env is Envs.dev,
        TESTING=config.env is Envs.test,
    )
    return app


def run() -> None:
    """Run application for development."""
    apply_migrations()
    create_app().run(
        host=config.flask_host,
        port=config.flask_port,
        load_dotenv=False,
    )
