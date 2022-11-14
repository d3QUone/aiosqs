from dataclasses import dataclass


@dataclass
class ErrorData:
    type: str
    code: str
    message: str


class SQSClientBaseError(Exception):
    """Generic error, including transportation errors."""


class SQSErrorResponse(SQSClientBaseError):
    """ErrorResponse XML from SQS service."""

    def __init__(self, error: ErrorData, request_id: str):
        self.error = error
        self.request_id = request_id
