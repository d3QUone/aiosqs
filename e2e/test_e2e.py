import unittest
import logging
from urllib.parse import quote_plus

from dotenv import dotenv_values

from aiosqs import SQSClient, SQSErrorResponse


class E2ETestCase(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        config = dotenv_values(".env")
        cls.region_name = config["AWS_REGION_NAME"]
        cls.aws_access_key_id = config["AWS_ACCESS_KEY_ID"]
        cls.aws_secret_access_key = config["AWS_SECRET_ACCESS_KEY"]
        cls.host = config["AWS_HOST"]
        cls.queue_name = config["AWS_QUEUE_NAME"]

    async def asyncSetUp(self):
        await super().asyncSetUp()

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.CRITICAL)

        self.client = SQSClient(
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            host=self.host,
            verify_ssl=False,
            logger=logger,
            quote_via=quote_plus,
        )

    async def asyncTearDown(self):
        await self.client.close()

    async def test_get_queue_url(self):
        response = await self.client.get_queue_url(queue_name=self.queue_name)
        queue_url = response["QueueUrl"]
        self.assertTrue(queue_url.endswith(self.queue_name), msg=queue_url)

    async def test_call_unknown_queue_name(self):
        with self.assertRaises(SQSErrorResponse) as e:
            await self.client.get_queue_url(queue_name="ErrorDoesNotExistName")
        exception = e.exception
        self.assertEqual(exception.error.type, "Sender")
        self.assertEqual(exception.error.code, "AWS.SimpleQueueService.NonExistentQueue")
        self.assertEqual(exception.error.message, "The specified queue doesn't exist.")

    async def test_send_message_with_raw_text(self):
        response = await self.client.get_queue_url(queue_name=self.queue_name)
        queue_url = response["QueueUrl"]

        message_body = "a     b    c     d"
        try:
            response = await self.client.send_message(
                queue_url=queue_url,
                message_body=message_body,
            )
            self.assertEqual(set(response.keys()), {"MessageId", "MD5OfMessageBody"})
        except SQSErrorResponse as e:
            self.fail(f"Recieved error: {e.error}")

        response = await self.client.receive_message(
            queue_url=queue_url,
            max_number_of_messages=1,
            visibility_timeout=60,
        )
        self.assertTrue(len(response) > 0)

        message = response[0]
        receipt_handle = message["ReceiptHandle"]
        self.assertEqual(message["Body"], message_body)

        response = await self.client.delete_message(
            queue_url=queue_url,
            receipt_handle=receipt_handle,
        )
        self.assertIsNone(response)
