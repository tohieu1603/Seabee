"""
Custom exceptions and error handlers
"""
from ninja.errors import HttpError


class PermissionDenied(HttpError):
    """Permission denied exception"""
    def __init__(self, message: str = "Permission denied"):
        super().__init__(403, message)


class ResourceNotFound(HttpError):
    """Resource not found exception"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(404, message)


class BadRequest(HttpError):
    """Bad request exception"""
    def __init__(self, message: str = "Bad request"):
        super().__init__(400, message)


class Unauthorized(HttpError):
    """Unauthorized exception"""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(401, message)


class ValidationError(HttpError):
    """Validation error exception"""
    def __init__(self, message: str = "Validation error", errors: dict = None):
        self.errors = errors or {}
        super().__init__(422, message)
