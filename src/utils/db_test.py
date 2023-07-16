import pytest
import psycopg_pool

from unittest import mock

from .db import db_command, db_query, _ConnectionPool
from ..exceptions import DBException


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
def test_ConnectionPool_create():
    """Positive case: open connection pool to test db."""
    with _ConnectionPool().pool.connection() as conn:
        res = conn.execute("SELECT 42;")
        assert res.fetchone()[0] == 42
 