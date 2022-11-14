import unittest

from aiosqs.parser import parse_xml_result_response
from aiosqs.tests.utils import load_fixture


class SendMessageTestCase(unittest.TestCase):
    action = "SendMessage"

    def test_send_message_ok(self):
        res = parse_xml_result_response(
            action=self.action,
            body=load_fixture("send_message.xml"),
        )
        self.assertEqual(
            res,
            {
                "MessageId": "acdf9b7f-a639-4a5b-9557-b4de52a56d01",
                "MD5OfMessageBody": "a88e5d79dc2948e662b90dc2857ba05c",
            },
        )
