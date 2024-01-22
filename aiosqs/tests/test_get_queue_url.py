from aiosqs.exceptions import SQSErrorResponse
from aiosqs.tests.cases import ActionTestCase


class GetQueueUrlTestCase(ActionTestCase):
    action = "GetQueueUrl"

    def test_get_queue_url(self):
        res = self.parseXMLResponse("get_queue_url.xml")
        self.assertEqual(
            res,
            {
                "QueueUrl": "http://sqs.mcs.mail.ru/account123/example_queue",
            },
        )

    def test_response_with_namespace(self):
        res = self.parseXMLResponse("get_queue_url_namespace.xml")
        self.assertEqual(
            res,
            {
                "QueueUrl": "http://sqs.mcs.mail.ru/account123/example_queue",
            },
        )

    def test_queue_not_found(self):
        with self.assertRaises(SQSErrorResponse) as e:
            self.parseXMLResponse("get_queue_url_not_exists_yandex_cloud.xml")
        exception = e.exception
        self.assertEqual(exception.error.type, "Sender")
        self.assertEqual(exception.error.code, "AWS.SimpleQueueService.NonExistentQueue")
        self.assertEqual(exception.error.message, "The specified queue doesn't exist.")
