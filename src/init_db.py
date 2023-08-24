"""Wait for database to be started and apply migrations."""
import pathlib
import sys
from time import sleep

import psycopg
from loguru import logger
from yoyo import get_backend, read_migrations

from utils.config import Envs, config


def wait_for_db() -> None:
    """Wait for database to be started."""
    for _i in range(5):
        try:
            sleep(0.5)
            conn = psycopg.connect(
                psycopg.conninfo.make_conninfo(**config.postgres_conn_info),
                autocommit=True,
            )
            conn.execute("SELECT 42;").fetchone()

        except:  # noqa: E722
            logger.exception("Database is not available")


def apply_migrations() -> None:
    """Apply yoyo migrations."""
    backend = get_backend(
        "postgresql+psycopg://{user}:{password}@{host}:{port}/{dbname}".format(
            **config.postgres_conn_info,
        ),
    )
    migrations = read_migrations(
        str(pathlib.Path(__file__).parent.joinpath(pathlib.Path("migrations")).absolute()),
    )

    with backend.lock():
        if config.env == Envs.test:
            # Rollback all migrations
            backend.rollback_migrations(backend.to_rollback(migrations))

        # Apply any outstanding migrations
        backend.apply_migrations(backend.to_apply(migrations))


if __name__ == "__main__":
    wait_for_db()
    apply_migrations()
    sys.exit(0)
