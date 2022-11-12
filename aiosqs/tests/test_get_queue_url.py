import unittest

from aiosqs.parser import parse_xml_result_response
from aiosqs.tests.utils import load_fixture


class GetQueueUrlTestCase(unittest.TestCase):
    action = "GetQueueUrl"

    def test_get_queue_url(self):
        res = parse_xml_result_response(
            action=self.action,
            body=load_fixture("get_queue_url.xml"),
        )
        self.assertEqual(
            res,
            {
                "QueueUrl": "http://sqs.mcs.mail.ru/account123/example_queue",
            },
        )
