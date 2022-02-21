"""Custom exceptions for the server."""
from typing import Optional


class Error(Exception):
    """
    Custom error class.

    Attributes:
        message - explanation of the error
    """

    default_message: str = ''

    def __init__(self, message: Optional[str] = None, *args: object) -> None:
        """Save initial variables."""
        self.message: str = message if message else self.default_message
        super().__init__(message, *args)


class NotMovableError(Error):
    """Exception raises when a object can not be moved."""

    default_message: str = 'The object cannot be moved.'


class NotRotableError(Error):
    """Exception raises when a object can not be rotated."""

    default_message: str = 'The object cannot be rotated.'
