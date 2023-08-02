"""Apply dummy sql scripts."""
from psycopg import connect
from typing import Optional, List
from loguru import logger

from ..utils.config import config


sql_commands: List[str] = [
    """
        CREATE DATABASE t_accounting OWNER batya;
    """,
    """
        CREATE TABLE ;
    """,
]


def run(scripts: Optional[List[str]] = None):
    """Apply dummy sql scripts."""
    conn = connect(config.dsn)
    try:
        for command in sql_commands:
            conn.execute(command)
            logger.info("Executed: {}".format(command))
    except:
        logger.exception("Shit happened!!!")


if __name__ == "__main__":
    run()