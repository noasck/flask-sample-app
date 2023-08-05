"""Config."""
import os
import sys
import threading
from enum import Enum
from typing import ClassVar

from loguru import logger
from pydantic import ValidationError, field_validator
from pydantic.dataclasses import ConfigDict, dataclass

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
    def validate_env(cls, v: str) -> AllowedEnvs:
        """Validate env is one of allowed."""
        return AllowedEnvs(v)


class _Config:

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
    _logger_sinks: ClassVar[dict[str, int]] = {}

    def __new__(cls) -> "_Config":
        """Aquire lock and create instance per thread."""
        if cls._instance is None:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance.__init()
        return cls._instance

    def __init(self) -> None:
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
            raise
        except BaseException:
            logger.exception("Unknown exception during config parsing.")
            raise

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
