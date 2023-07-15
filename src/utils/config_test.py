import pytest
import os

from .config import _Config, ConfigParser, AllowedEnvs, _APP_ENV_PREFIX, APP_NAME
from pydantic import ValidationError


@pytest.fixture
def config_class():  # noqa
    """Get config class with no instance created"""
    _Config._instance = None
    return _Config


def test_config_singleton(config_class):
    """Test positive case: singleton instance."""
    assert config_class() is config_class()


def test_ConfigParser_works():
    """Test positive case: serialize envs."""
    envs = {
        env.replace(_APP_ENV_PREFIX, ""): value
        for env, value in os.environ.items()
        if env.startswith(APP_NAME.upper())
    }
    parsed = ConfigParser(**envs)
    assert parsed
    assert parsed.env is AllowedEnvs.test
    assert type(parsed.flask_port) == int


def test_ConfigParser_required_fields():
    """Test negative case: fields are not specified."""
    with pytest.raises(ValidationError) as err:
        ConfigParser()

    assert all([err["msg"] == "Field required" for err in err.value.errors()])
