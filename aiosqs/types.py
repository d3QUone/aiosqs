import logging
from typing import Union, TypedDict, List

LoggerType = Union[logging.Logger, logging.LoggerAdapter]


class GetQueueUrlResponse(TypedDict):
    QueueUrl: str


class SendMessageResponse(TypedDict):
    MessageId: str
    MD5OfMessageBody: str


class Message(TypedDict):
    MessageId: str
    ReceiptHandle: str
    Body: str
    MD5OfBody: str


ReceiveMessageResponse = Union[List[Message], None]
