class AppError(Exception):
    """Base application exception."""
    pass


class ResourceNotFound(AppError):
    """Raised when a resource cannot be found."""
    pass


class ValidationError(AppError):
    """Raised when user input is invalid."""
    pass


class UnauthorizedError(AppError):
    """Raised when authentication fails."""
    pass