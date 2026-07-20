class AppException(Exception):
    status_code = 500

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class ValidationException(AppException):
    status_code = 400


class AuthenticationException(AppException):
    status_code = 401


class AuthorizationException(AppException):
    status_code = 403


class ResourceNotFoundException(AppException):
    status_code = 404


class ConflictException(AppException):
    status_code = 409