"""Config."""
import threading
import os
from loguru import logger
import sys
from pydantic.dataclasses import dataclass, ConfigDict
from pydantic import field_validator, FieldValidationInfo, ValidationError
from enum import Enum

APP_NAME = "accounting_app"
_APP_ENV_PREFIX = APP_NAME.upper() + "_"


class AllowedEnvs(Enum):
    """Allowed ENV and FLASK_ENV values."""

    dev = "development"
    prod = "production"
    test = "testing"


@dataclass(
    config=ConfigDict(
        extra="ignore",
        alias_generator=lambda x: x.upper(),
    ),
)
class ConfigParser:
    """Pass lowercased envs names below."""

    env: AllowedEnvs
    dsn: str
    flask_host: str
    flask_port: int

    @field_validator("env")
    @classmethod
    def validate_env(cls, v: str, info: FieldValidationInfo):
        """Validate env is one of allowed."""
        return AllowedEnvs(v)


class _Config(object):
    """
    Thread safe singleton.

    Reads config and sets up logger after config is readed.
    Logger sinks are saved in self._logger_sinks dictionary.
    Uppercased APP_NAME used as prefix for envs.
    """

    _instance = None
    _lock = threading.Lock()

    # Logger sinks are analogs to default logger handlers.
    # For every output source should be 1 sink.
    # Sinks could be removed from any place in the code:
    #     logger.remove(_Config._logger_sinks["<SINK NAME>"])
    _logger_sinks = {}

    def __new__(cls):
        """Aquire lock and create instance per thread."""
        if cls._instance is None:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Parse configuration."""
        try:
            # Reading environmental variables
            # with APP_NAME + _ prefix.
            # Passing to serializer without prefix.
            self.config = ConfigParser(
                **{
                    env.replace(_APP_ENV_PREFIX, ""): value
                    for env, value in os.environ.items()
                    if env.startswith(APP_NAME.upper())
                },
            )
        except ValidationError as exc:
            for error in exc.errors():
                logger.error(
                    "Invalid config: {}. Reason: {}.",
                    error.get("loc", ["NA"])[0],
                    error.get("msg", "NA"),
                )
            raise exc
        except BaseException as exc:
            logger.exception("Unknown exception during config parsing.")
            raise exc

        # Set up logger. Remove defaults:
        logger.remove()
        # If env TEST or DEV: log to STDERR
        # If env PROD or DEV: log to FILE
        if self.config.env in (AllowedEnvs.test, AllowedEnvs.dev):
            self._logger_sinks["stderr"] = logger.add(
                sys.stderr,
                level="TRACE",
                backtrace=True,
                diagnose=True,
                format="<green>{time:HH:mm:ss.SS}</green>"
                " | <level>{level: <8}</level> | "
                "<blue>{file}</blue>:<m>{line}</m> - "
                "<level>{message}</level> -- <b>{extra}</b>",
            )
        if self.config.env in (AllowedEnvs.prod, AllowedEnvs.dev):
            self._logger_sinks["file"] = logger.add(
                f"logs/{APP_NAME}_{{time}}.log",
                compression="zip",
                rotation="12:00",
                level="INFO",
                serialize=True,
                backtrace=False,
                diagnose=False,
                format="",
            )

        logger.info("Logger set up successfully")
        logger.info("Configuration read successfully.")


config = _Config().config
