"""
Basic logic took from official examples:
https://docs.aws.amazon.com/general/latest/gr/sigv4-signed-request-examples.html
"""
import asyncio
import datetime
import urllib.parse
from logging import getLogger
from typing import Dict, Optional, List, Union, Callable, NamedTuple

import aiohttp

from aiosqs.encryption import get_signature_key, hmac_sha256_hexdigest, sha256_hexdigest
from aiosqs.exceptions import SQSClientBaseError
from aiosqs.types import LoggerType, GetQueueUrlResponse, ReceiveMessageResponse, SendMessageResponse
from aiosqs.parser import parse_xml_result_response

default_logger = getLogger(__name__)


class SignedRequest(NamedTuple):
    headers: Dict
    querystring: str


class SQSClient:
    algorithm = "AWS4-HMAC-SHA256"
    default_timeout_sec = 10

    def __init__(
        self,
        region_name: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        host: str,
        timeout_sec: Optional[int] = None,
        logger: Optional[LoggerType] = None,
        verify_ssl: Optional[bool] = None,
        quote_via: Optional[Callable] = None,
        aws_session_token: Optional[str] = None,
    ):
        self.service_name = "sqs"
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_session_token = aws_session_token
        # It's your host including region (if related), e.g. "sqs.us-west-2.amazonaws.com"
        self.host = host
        self.endpoint_url = f"https://{host}"
        self.verify_ssl = verify_ssl

        self.logger = logger or default_logger
        self.timeout = aiohttp.ClientTimeout(total=timeout_sec or self.default_timeout_sec)
        self.session = aiohttp.ClientSession(timeout=self.timeout)

        # It's possible to have differen quoting logic for different SQS providers.
        # By default Amazon SQS uses `urllib.parse.quote`, so no extra customizations are required.
        # Related issue: https://github.com/d3QUone/aiosqs/issues/13
        self.quote_via = quote_via or urllib.parse.quote

    async def close(self):
        await self.session.close()
        # https://docs.aiohttp.org/en/stable/client_advanced.html#graceful-shutdown
        await asyncio.sleep(0.25)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def build_signed_request(self, params: Dict) -> SignedRequest:
        # Create a date for headers and the credential string
        t = datetime.datetime.utcnow()
        amz_date = t.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = t.strftime("%Y%m%d")  # Date w/o time, used in credential scope

        # Create canonical URI--the part of the URI from domain to query string (use '/' if no path)
        canonical_uri = "/"

        # Create the canonical query string. Important notes:
        # - Query string values must be URL-encoded (space=%20).
        # - The parameters must be sorted by name.
        canonical_querystring = urllib.parse.urlencode(query=list(sorted(params.items())), quote_via=self.quote_via)

        # Create the canonical headers and signed headers.
        canonical_headers = f"host:{self.host}\nx-amz-date:{amz_date}\n"

        # Create the list of signed headers.
        signed_headers = "host;x-amz-date"

        # Add session token if present
        if self.aws_session_token:
            canonical_headers += f"x-amz-security-token:{self.aws_session_token}\n"
            signed_headers += ";x-amz-security-token"

        # Create payload hash. For GET requests, the payload is an empty string ("").
        payload_hash = sha256_hexdigest("")

        # Combine elements to create canonical request.
        canonical_request = "\n".join(
            [
                "GET",
                canonical_uri,
                canonical_querystring,
                canonical_headers,
                signed_headers,
                payload_hash,
            ]
        )

        credential_scope = f"{date_stamp}/{self.region_name}/{self.service_name}/aws4_request"

        string_to_sign = "\n".join(
            [
                self.algorithm,
                amz_date,
                credential_scope,
                sha256_hexdigest(canonical_request),
            ]
        )

        signing_key = get_signature_key(
            aws_secret_access_key=self.aws_secret_access_key,
            date_stamp=date_stamp,
            region_name=self.region_name,
            service_name=self.service_name,
        )
        signature = hmac_sha256_hexdigest(key=signing_key, msg=string_to_sign)

        authorization_header = f"{self.algorithm} Credential={self.aws_access_key_id}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"

        # The request can include any headers, but MUST include "host", "x-amz-date",
        # and (for this scenario) "Authorization". "host" and "x-amz-date" must
        # be included in the canonical_headers and signed_headers. Order here is not significant.
        headers = {
            "x-amz-date": amz_date,
            "Authorization": authorization_header,
            "content-type": "application/x-www-form-urlencoded",
        }

        if self.aws_session_token:
            headers["x-amz-security-token"] = self.aws_session_token

        return SignedRequest(
            headers=headers,
            querystring=canonical_querystring,
        )

    async def request(self, params: Dict) -> Union[Dict, List, None]:
        params["Version"] = "2012-11-05"
        signed_request = self.build_signed_request(params=params)
        url = f"{self.endpoint_url}?{signed_request.querystring}"

        try:
            response = await self.session.get(
                url=url,
                headers=signed_request.headers,
                verify_ssl=self.verify_ssl,
            )
        except Exception as e:
            self.logger.error("SQS request error: %s", e)
            raise SQSClientBaseError

        try:
            response_body = await response.text()
        except aiohttp.ContentTypeError as e:
            self.logger.error("SQS API encoding error: %s", e)
            raise SQSClientBaseError

        if not response.ok:
            status_code = response.status
            self.logger.error(f"SQS API error: status_code=%s, body=%s", status_code, response_body)

            if "ErrorResponse" in response_body:
                return parse_xml_result_response(action=params["Action"], body=response_body, logger=self.logger)

            raise SQSClientBaseError

        return parse_xml_result_response(action=params["Action"], body=response_body, logger=self.logger)

    async def get_queue_url(self, queue_name: str) -> GetQueueUrlResponse:
        params = {
            "Action": "GetQueueUrl",
            "QueueName": queue_name,
        }
        return await self.request(params=params)

    async def send_message(
        self,
        queue_url: str,
        message_body: str,
        delay_seconds: int = 0,
        message_group_id: str = None,
        message_deduplication_id: str = None,
    ) -> SendMessageResponse:
        """https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_SendMessage.html"""
        params = {
            "Action": "SendMessage",
            "DelaySeconds": delay_seconds,
            "MessageBody": message_body,
            "QueueUrl": queue_url,
        }
        # Only for FIFO queues
        if message_group_id:
            params["MessageGroupId"] = message_group_id
        if message_deduplication_id:
            params["MessageDeduplicationId"] = message_deduplication_id
        return await self.request(params=params)

    async def receive_message(
        self,
        queue_url: str,
        max_number_of_messages: int,
        visibility_timeout: int,
        wait_time_seconds: int = 0,
    ) -> ReceiveMessageResponse:
        params = {
            "Action": "ReceiveMessage",
            "QueueUrl": queue_url,
            "MaxNumberOfMessages": max_number_of_messages,
            # The duration (in seconds) that the received messages are hidden from subsequent retrieve requests after
            # being retrieved by a ReceiveMessage request.
            "VisibilityTimeout": visibility_timeout,
            # The duration (in seconds) for which the call waits for a message to arrive in the queue before returning.
            # If a message is available, the call returns sooner than WaitTimeSeconds. If no messages are available
            # and the wait time expires, the call returns successfully with an empty list of messages.
            "WaitTimeSeconds": wait_time_seconds,
        }
        return await self.request(params=params)

    async def delete_message(self, queue_url: str, receipt_handle: str) -> None:
        params = {
            "Action": "DeleteMessage",
            "QueueUrl": queue_url,
            "ReceiptHandle": receipt_handle,
        }
        return await self.request(params=params)
