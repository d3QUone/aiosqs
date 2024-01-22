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
