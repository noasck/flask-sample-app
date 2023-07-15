"""Main flow."""
from .utils.config import config, APP_NAME, AllowedEnvs
from loguru import logger
from flask import Flask


def create_app() -> Flask:
    """Application factory."""
    app = Flask(APP_NAME)
    app.config.update(
        DEBUG=config.env is AllowedEnvs.dev,
        TESTING=config.env is AllowedEnvs.test,
    )
    return app

def main():
    create_app().run(
        host=config.flask_host,
        port=config.flask_port,
        load_dotenv=False,
    )