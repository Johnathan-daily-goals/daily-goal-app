class AppError(Exception):
    status_code = 400
    message = "Bad request"

    def __init__(self, message: str | None = None):
        super().__init__(message)
        if message:
            self.message = message


class ConflictError(AppError):
    status_code = 409
    message = "Conflict"


class DailyGoalAlreadyExists(ConflictError):
    message = "Only one daily goal per project per day"