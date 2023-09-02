"""Persistent psycopg connection pool."""
import atexit
import functools
import threading

import psycopg
import psycopg_pool

from src.exceptions import DBError

from .config import config


class _ConnectionPool:

    """Thread safe psycopg3 singleton connection poll."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls) -> "_ConnectionPool":
        if cls._instance is None:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._init()
        return cls._instance

    def handle_reconnection_error(self, *args, **_) -> None:
        """Close pool on reconnection error & send notification."""
        self.pool.close()

        raise DBError(
            msg="PG db reconnection error.",
            errors={"context": args},
        )

    def _init(self) -> None:
        """Instanciate connection pool."""
        self.pool = psycopg_pool.ConnectionPool(
            psycopg.conninfo.make_conninfo(**config.postgres_conn_info),
            min_size=1,
            max_size=config.postgres_pool_size,
            max_waiting=5,
            timeout=20,
            kwargs={"autocommit": True},
            reconnect_failed=self.handle_reconnection_error,
        )

        atexit.register(self.pool.close)


def db_query(func: callable) -> callable:
    """Injects db cursor with no transaction."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> any:
        """Acquire and inject autocommiting cursor."""
        try:
            with _ConnectionPool().pool.connection() as connection, connection.cursor() as cursor:
                kwargs["cursor"] = cursor
                return func(*args, **kwargs)
        except psycopg.Error as error:
            raise DBError(
                msg="Database exception during query execution.",
                errors={"diag": error.diag},
            ) from error

    return wrapper


def db_command(func: callable) -> callable:
    """Injects db cursor, wrapped in transaction."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> any:
        """Acquire and inject cursor with transaction."""
        try:
            with _ConnectionPool().pool.connection() as connection:
                try:
                    with connection.transaction(), connection.cursor() as cursor:
                        kwargs["cursor"] = cursor
                        return func(*args, **kwargs)
                except BaseException:
                    connection.rollback()
                    raise
        except psycopg.Error as error:
            raise DBError(
                msg="Database exception during transaction.",
                errors={"diag": error.diag},
            ) from error

    return wrapper
