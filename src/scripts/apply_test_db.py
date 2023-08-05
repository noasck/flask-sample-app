"""Apply dummy sql scripts."""

from loguru import logger
from psycopg import connect

from src.utils.config import config

sql_commands: list[str] = [
    """
        CREATE DATABASE t_accounting OWNER batya;
    """,
    """
        CREATE TABLE ;
    """,
]


def run() -> None:
    """Apply dummy sql scripts."""
    conn = connect(config.dsn)
    try:
        for command in sql_commands:
            conn.execute(command)
            logger.info(f"Executed: {command}")
    except:  # noqa: E722
        logger.exception("Shit happened!!!")


if __name__ == "__main__":
    run()
