from unittest import mock

import psycopg
import pytest

from .db import _ConnectionPool, db_command, db_query


def test_ConnectionPool_singleton():
    """Test positive case _ConnectionPool is singleton."""
    mock_conn = mock.MagicMock()

    def mock_init(self):
        self.pool = mock_conn

    with mock.patch.object(
        _ConnectionPool,
        "_init",
        mock_init,
    ):
        assert _ConnectionPool() is _ConnectionPool()
        assert _ConnectionPool().pool == mock_conn

    # IMPORTANT: teardown mock of _ConnectionPool

    _ConnectionPool._instance = None


@pytest.mark.integrity()
def test_ConnectionPool_connect():
    """Positive case: open connection pool to test db."""
    with _ConnectionPool().pool.connection() as conn:
        res = conn.execute("SELECT 42;")
        assert res.fetchone()[0] == 42


@pytest.mark.integrity()
def test_db_query():
    """Test positive case: db_query decorator."""

    @db_query
    def read_42(cursor: psycopg.Cursor):
        """Dummy service method."""
        return cursor.execute("select 42;").fetchone()[0]

    assert read_42() == 42


@pytest.mark.integrity()
def test_db_command():
    """Test positive case: db_command decorator."""

    @db_command
    def write_row_in_test_table(row: dict, *, cursor: psycopg.Cursor):
        """Write a single row in test table."""
        cursor.execute(
            """
                INSERT INTO "test_table" VALUES (1, %(value)s);
            """,
            row,
        )
        return True

    @db_command
    def read_rows_in_test_table(*, cursor: psycopg.Cursor):
        """Read all rows in test table."""
        return cursor.execute("SELECT * FROM test_table;").fetchall()

    assert write_row_in_test_table(row={"value": "aboba"})

    assert len(read_rows_in_test_table()) == 1
    assert read_rows_in_test_table()[0][1] == "aboba"
