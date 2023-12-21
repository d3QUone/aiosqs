import unittest
import re
import logging

import ddt
from aioresponses import aioresponses

from aiosqs.exceptions import SQSErrorResponse
from aiosqs.client import SQSClient
from aiosqs.tests.utils import load_fixture


@ddt.ddt(testNameFormat=ddt.TestNameFormat.INDEX_ONLY)
class ClientTestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.CRITICAL)

        self.client = SQSClient(
            aws_access_key_id="access_key_id",
            aws_secret_access_key="secret_access_key",
            region_name="us-west-2",
            host="mocked_amazon_host.com",
            timeout_sec=0,
            logger=logger,
        )

    async def asyncTearDown(self):
        await self.client.close()

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
