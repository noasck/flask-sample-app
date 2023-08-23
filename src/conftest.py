"""Fixtures and configurations."""

import psycopg
import psycopg_pool
import pytest
from loguru import logger
from psycopg import IsolationLevel, connect, conninfo, sql

from .utils.config import config
from .utils.db import _ConnectionPool

TEST_DB_PREFIX = "test_"


@pytest.fixture(autouse=True)
def clear_tables(request: pytest.FixtureRequest) -> psycopg.Cursor:
    """Set up & tear down test database. Works only on integration tests."""
    if "integrity" in request.keywords:
        conn = _ConnectionPool()
        conn.pool.close()

        recreate_test_db()

        dbname = config.postgres_conn_info["dbname"]
        test_dbname = TEST_DB_PREFIX + dbname
        test_conninfo = {
            **config.postgres_conn_info,
            "dbname": test_dbname,
        }

        conn.pool = psycopg_pool.ConnectionPool(
            conninfo.make_conninfo(**test_conninfo),
            max_size=5,
            max_waiting=5,
            timeout=10,
            kwargs={"autocommit": True},
        )

        yield conn

    else:
        yield None


def recreate_test_db() -> None:
    """Apply dummy sql scripts."""
    # connecting to default database:
    conn = connect(psycopg.conninfo.make_conninfo(**config.postgres_conn_info), autocommit=True)
    conn.isolation_level = IsolationLevel.SERIALIZABLE
    dbname = config.postgres_conn_info["dbname"]
    test_dbname = TEST_DB_PREFIX + dbname
    try:
        # Dropping all active connections to TEST_DB
        conn.execute(
            """
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = %s;
        """,
            (test_dbname,),
        )
        # Recreating
        conn.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(test_dbname)))
        conn.execute(
            sql.SQL("CREATE DATABASE {} TEMPLATE {};").format(
                sql.Identifier(test_dbname),
                sql.Identifier(dbname),
            ),
        )

        logger.info(f"Executed: CREATE DATABASE {test_dbname};")
    except Exception:
        conn.rollback()
        logger.exception("Shit happened!!!")
        raise
    conn.close()
