class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class NotFoundError(AppError):
    def __init__(self, message: str = "Recurso no encontrado"):
        super().__init__(message, status_code=404)


class ValidationError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class ConflictError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=409)
