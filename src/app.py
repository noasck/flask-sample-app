"""Main flow."""
from flask import Flask

from .utils.config import APP_NAME, AllowedEnvs, config


def create_app() -> Flask:
    """Application factory."""
    app = Flask(APP_NAME)
    app.config.update(
        DEBUG=config.env is AllowedEnvs.dev,
        TESTING=config.env is AllowedEnvs.test,
    )
    return app


def run() -> None:
    """Run application for development."""
    create_app().run(
        host=config.flask_host,
        port=config.flask_port,
        load_dotenv=False,
    )
