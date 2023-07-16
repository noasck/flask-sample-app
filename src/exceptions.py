class BaseServiceException(Exception):
    """Custom service exception."""

    def __init__(self, msg: str, exc_info: dict[str, str] = None) -> None:
        """
        Instanciate exception.
        
        Arguments:
            msg: human-readable message.
            errors: human-readable .
        """
        super().__init__(msg)
        if exc_info is not None and type(exc_info) is not dict:
            raise TypeError("Invalid type for argument: errors: {}".format(
                type(exc_info),
            ))
        self.errors = exc_info


class DBException(BaseServiceException):
    """Postgres DB operation exception."""
    pass