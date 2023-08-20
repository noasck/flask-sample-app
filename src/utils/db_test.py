import pytest
import psycopg_pool
import psycopg

from unittest import mock

from .db import db_command, db_query, _ConnectionPool
from ..exceptions import DBError


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


@pytest.mark.integrity
def test_ConnectionPool_connect():
    """Positive case: open connection pool to test db."""
    with _ConnectionPool().pool.connection() as conn:
        res = conn.execute("SELECT 42;")
        assert res.fetchone()[0] == 42


@pytest.mark.integrity
def test_db_query():
    """Test positive case: db_query decorator."""

    @db_query
    def read_42(cursor: psycopg.Cursor):
        """Dummy service method."""
        return cursor.execute("select 42;").fetchone()[0]

    assert read_42() == 42
