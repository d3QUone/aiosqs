import unittest
import re

from aioresponses import aioresponses

from aiosqs.client import SQSClient
from aiosqs.tests.utils import load_fixture


class ClientTestCase(unittest.IsolatedAsyncioTestCase):
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
