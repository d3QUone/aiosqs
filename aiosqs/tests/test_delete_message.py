import unittest

from aiosqs.parser import parse_xml_result_response
from aiosqs.tests.utils import load_fixture


class DeleteMessageTestCase(unittest.TestCase):
    action = "DeleteMessage"

    def test_delete_message_ok(self):
        res = parse_xml_result_response(
            action=self.action,
            body=load_fixture("delete_message.xml"),
        )
        self.assertIsNone(res)
