class AppError(Exception):
    status_code = 400
    message = "Application error"

    def __init__(self, message: str | None = None):
        super().__init__(message or self.message)
        self.detail = message or self.message


class DailyGoalAlreadyExists(AppError):
    status_code = 409
    message = "Only one daily goal per project per day"