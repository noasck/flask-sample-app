"""Fixtures and configurations."""
import pytest
import textwrap
import psycopg
from .utils.db import _ConnectionPool


@pytest.fixture(autouse=True)
def clear_tables(request) -> psycopg.Cursor:
    """Set up & tear down test database. Works only on integration tests."""
    if "integrity" in request.keywords:
        conn = _ConnectionPool()
        conn.pool.close()
        _ConnectionPool._instance = None
