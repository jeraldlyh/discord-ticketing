class MaxPointsError(Exception):
    def __init__(self, message):
        super().__init__(message)


class InsufficientPointsError(Exception):
    def __init__(self, message):
        super().__init__(message)


class NotFoundError(Exception):
    def __init__(self, message):
        super().__init__(message)
