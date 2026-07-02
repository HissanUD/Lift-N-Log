class ServiceError(Exception):
    """Base class for errors raised by the service layer."""


class NotFoundError(ServiceError):
    """Raised when a requested resource does not exist or is not visible to the user."""


class ConflictError(ServiceError):
    """Raised when a request conflicts with existing data."""


class ForbiddenError(ServiceError):
    """Raised when the user is authenticated but not allowed to perform an action."""


class AuthenticationError(ServiceError):
    """Raised when credentials are missing or invalid."""
