class MaxPointsError(Exception):
    def __init__(sel, message):
        super().__init__(message)

class InsufficientPointsError(Exception):
    def __init__(sel, message):
        super().__init__(message)