import unittest
import re
import logging
import urllib.parse

import ddt
from freezegun import freeze_time
from aioresponses import aioresponses

from aiosqs.exceptions import SQSErrorResponse
from aiosqs.client import SQSClient
from aiosqs.tests.fixtures import load_fixture


@ddt.ddt(testNameFormat=ddt.TestNameFormat.INDEX_ONLY)
class DefaultClientTestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.CRITICAL)

        self.client = SQSClient(
            aws_access_key_id="access_key_id",
            aws_secret_access_key="secret_access_key",
            region_name="us-west-2",
            host="mocked_amazon_host.com",
            timeout_sec=0,
            logger=self.logger,
        )

    async def asyncTearDown(self):
        await self.client.close()

    async def test_signature_with_quote_via(self):
        params = {
            "Action": "SendMessage",
            "DelaySeconds": 0,
            "MessageBody": "a     b    c     d",
            "QueueUrl": "http://host.com/internal/tests",
            "Version": "2012-11-05",
        }
        with freeze_time("2022-03-07T11:30:00.0000"):
            signed_request = self.client.build_signed_request(params=params)

        self.assertEqual(
            signed_request.headers,
            {
                "x-amz-date": "20220307T113000Z",
                "Authorization": "AWS4-HMAC-SHA256 Credential=access_key_id/20220307/us-west-2/sqs/aws4_request, SignedHeaders=host;x-amz-date, Signature=7d7ae7f85d3175f61e5256ed560c7b284491f767b9c352d1231f92ec04043d8e",
                "content-type": "application/x-www-form-urlencoded",
            },
        )
        self.assertEqual(
            signed_request.querystring,
            "Action=SendMessage&DelaySeconds=0&MessageBody=a%20%20%20%20%20b%20%20%20%20c%20%20%20%20%20d&QueueUrl=http%3A%2F%2Fhost.com%2Finternal%2Ftests&Version=2012-11-05",
        )

    @aioresponses()
    async def test_is_context_manager(self, mock):
        mock.get(
            url=re.compile(r"https://mocked_amazon_host.com"),
            status=200,
            body=load_fixture("get_queue_url.xml"),
        )

        async with SQSClient(
            aws_access_key_id="access_key_id",
            aws_secret_access_key="secret_access_key",
            region_name="us-west-2",
            host="mocked_amazon_host.com",
            timeout_sec=0,
        ) as client:
            response = await client.get_queue_url(queue_name="mocked_queue_name")
            self.assertEqual(response, {"QueueUrl": "http://sqs.mcs.mail.ru/account123/example_queue"})

    @ddt.data(
        ("error_invalid_access_key.xml", "key_id is invalid"),
        ("error_invalid_secret_key.xml", "The security token included in the request is invalid."),
    )
    @ddt.unpack
    @aioresponses()
    async def test_invalid_auth_keys(self, fixture_name: str, error_message: str, mock):
        mock.get(
            url=re.compile(r"https://mocked_amazon_host.com"),
            status=403,
            body=load_fixture(fixture_name),
        )

        with self.assertRaises(SQSErrorResponse) as e:
            await self.client.get_queue_url(queue_name="mocked_queue_name")
        exception = e.exception
        self.assertEqual(exception.error.type, "Sender")
        self.assertEqual(exception.error.code, "InvalidClientTokenId")
        self.assertEqual(exception.error.message, error_message)


@ddt.ddt(testNameFormat=ddt.TestNameFormat.INDEX_ONLY)
class IAMAuthTestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.CRITICAL)

        self.client = SQSClient(
            aws_access_key_id="access_key_id",
            aws_secret_access_key="secret_access_key",
            region_name="us-west-2",
            host="mocked_amazon_host.com",
            timeout_sec=0,
            logger=self.logger,
            aws_session_token="session_token_123",
        )

    async def asyncTearDown(self):
        await self.client.close()

    def test_session_token_in_headers(self):
        params = {
            "Action": "SendMessage",
            "DelaySeconds": 0,
            "MessageBody": "test message",
            "QueueUrl": "http://host.com/queue",
            "Version": "2012-11-05",
        }
        with freeze_time("2022-03-07T11:30:00.0000"):
            signed_request = self.client.build_signed_request(params=params)

        # Verify session token is in headers
        self.assertIn("x-amz-security-token", signed_request.headers)
        self.assertEqual(signed_request.headers["x-amz-security-token"], "session_token_123")

    def test_session_token_in_signature(self):
        params = {
            "Action": "SendMessage",
            "MessageBody": "test",
            "QueueUrl": "http://host.com/queue",
        }
        with freeze_time("2022-03-07T11:30:00.0000"):
            signed_request = self.client.build_signed_request(params=params)

        # Verify session token is included in signed headers
        self.assertIn("x-amz-security-token", signed_request.headers["Authorization"])

    @aioresponses()
    async def test_invalid_session_token(self, mock):
        mock.get(
            url=re.compile(r"https://mocked_amazon_host.com"),
            status=403,
            body=load_fixture("error_invalid_session_token.xml"),
        )

        with self.assertRaises(SQSErrorResponse) as e:
            await self.client.get_queue_url(queue_name="test_queue")

        exception = e.exception
        self.assertEqual(exception.error.type, "Sender")
        self.assertEqual(exception.error.code, "InvalidSecurityToken")
        self.assertEqual(exception.error.message, "The provided security token is invalid.")

    @aioresponses()
    async def test_signature_mismatch(self, mock):
        mock.get(
            url=re.compile(r"https://mocked_amazon_host.com"),
            status=403,
            body=load_fixture("error_signature.xml"),
        )

        with self.assertRaises(SQSErrorResponse) as e:
            await self.client.send_message(queue_url="https://sqs.us-east-1.amazonaws.com/queue", message_body="test message")

        exception = e.exception
        self.assertEqual(exception.error.type, "Sender")
        self.assertEqual(exception.error.code, "SignatureDoesNotMatch")
        self.assertIn("The request signature we calculated does not match", exception.error.message)


class VKClientTestCase(DefaultClientTestCase):
    async def asyncSetUp(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.CRITICAL)

        self.client = SQSClient(
            aws_access_key_id="access_key_id",
            aws_secret_access_key="secret_access_key",
            region_name="us-west-2",
            host="mocked_amazon_host.com",
            timeout_sec=0,
            logger=self.logger,
            quote_via=urllib.parse.quote_plus,
        )

    async def test_signature_with_quote_via(self):
        params = {
            "Action": "SendMessage",
            "DelaySeconds": 0,
            "MessageBody": "a     b    c     d",
            "QueueUrl": "http://host.com/internal/tests",
            "Version": "2012-11-05",
        }

        with freeze_time("2022-03-07T11:30:00.0000"):
            signed_request = self.client.build_signed_request(params=params)

        self.assertEqual(
            signed_request.headers,
            {
                "x-amz-date": "20220307T113000Z",
                "Authorization": "AWS4-HMAC-SHA256 Credential=access_key_id/20220307/us-west-2/sqs/aws4_request, SignedHeaders=host;x-amz-date, Signature=0c36e0d3f62bd7ecb7e78ffe09fbd1224b7f850f3b4f13c7fc82e516fc7f2c57",
                "content-type": "application/x-www-form-urlencoded",
            },
        )
        self.assertEqual(
            signed_request.querystring,
            "Action=SendMessage&DelaySeconds=0&MessageBody=a+++++b++++c+++++d&QueueUrl=http%3A%2F%2Fhost.com%2Finternal%2Ftests&Version=2012-11-05",
        )
