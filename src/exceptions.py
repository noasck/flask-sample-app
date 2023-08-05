"""Custom service exceptions."""


class BaseServiceError(Exception):

    """Custom service exception."""

    def __init__(self, msg: str, errors: dict[str, str] | None = None) -> None:
        """
        Instanciate exception.

        Args:
            msg: human-readable message.
            errors: human-readable .
        """
        super().__init__(msg)
        if errors is not None and type(errors) is not dict:
            msg = f"Invalid type for argument: errors: {type(errors)}"
            raise TypeError(msg)
        self.errors = errors


class DBError(BaseServiceError):

    """Postgres DB operation exception."""
