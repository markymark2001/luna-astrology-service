class AstrologyServiceException(Exception):
    """Base exception for astrology service."""

    code: str = "ASTROLOGY_ERROR"

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class InvalidBirthDataException(AstrologyServiceException):
    """Exception raised for invalid birth data."""

    code: str = "INVALID_BIRTH_DATA"

    def __init__(self, message: str = "Invalid birth data provided"):
        super().__init__(message, status_code=400)


class ChartCalculationException(AstrologyServiceException):
    """Exception raised when chart calculation fails."""

    code: str = "CHART_CALCULATION_FAILED"

    def __init__(self, message: str = "Failed to calculate birth chart"):
        super().__init__(message, status_code=500)
