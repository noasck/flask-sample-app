"""Persistent psycopg connection pool."""
import threading
import psycopg
import functools
import psycopg_pool
from .config import config
from ..exceptions import DBException
import atexit


class _ConnectionPool():
    """Thread safe psycopg3 singleton connection poll."""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None: 
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._init()
        return cls._instance

    def handle_reconnection_error(self, *args, **kwargs):
        """Close pool on reconnection error & send notification."""
        self.pool.close()

        raise DBException(
            msg="PG db reconnection error.",
            exc_info={"context": args}
        )

    def _init(self):
        """Instanciate connection pool."""
        self.pool = psycopg_pool.ConnectionPool(
            config.dsn,
            max_size=20,
            max_waiting=5,
            timeout=20,
            kwargs={"autocommit": True},
            reconnect_failed=self.handle_reconnection_error,
        )

        atexit.register(self.pool.close)


def db_query(func: callable) -> callable:
    """Injects db cursor with no transaction."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """Acquire and inject autocommiting cursor."""
        try:
            with _ConnectionPool().pool.connection() as connection:
                with connection.cursor() as cursor:
                    kwargs["cursor"] = cursor
                    return func(*args, **kwargs)
        except psycopg.Error as error:
            raise DBException(
                msg="Database exception during query execution.",
                exc_info={"diag": error.diag},
            ) from error
    return wrapper


def db_command(func: callable) -> callable:
    """Injects db cursor, wrapped in transaction."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """Acquire and inject cursor with transaction."""
        try:
            with _ConnectionPool().pool.connection() as connection:
                try:
                    with connection.transaction():
                        with connection.cursor() as cursor:
                            kwargs["cursor"] = cursor
                            return func(*args, **kwargs)
                except BaseException as error:
                    connection.rollback()
                    raise error
        except psycopg.Error as error:
            raise DBException(
                msg="Database exception during transaction.",
                exc_info={"diag": error.diag},
            ) from error
    return wrapper
