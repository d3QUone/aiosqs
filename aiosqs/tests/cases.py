import unittest

from aiosqs.parser import parse_xml_result_response
from aiosqs.tests.fixtures import load_fixture


class ActionTestCase(unittest.TestCase):
    maxDiff = None
    action: str = None

    def parseXMLResponse(self, fixture_name: str):
        self.assertIsNotNone(self.action)
        res = parse_xml_result_response(
            action=self.action,
            body=load_fixture(fixture_name),
        )
        return res
