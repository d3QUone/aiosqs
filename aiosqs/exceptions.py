from dataclasses import dataclass


@dataclass
class ErrorData:
    type: str
    code: str
    message: str


class SQSClientBaseError(Exception):
    """Generic error, including transportation errors.
    Full list of raw errors:
    https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/CommonErrors.html
    """


class SQSErrorResponse(SQSClientBaseError):
    """ErrorResponse XML from SQS service."""

    def __init__(self, error: ErrorData, request_id: str):
        self.error = error
        self.request_id = request_id
