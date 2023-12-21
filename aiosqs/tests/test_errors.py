import unittest

from aiosqs.exceptions import SQSErrorResponse
from aiosqs.parser import parse_xml_result_response
from aiosqs.tests.utils import load_fixture


class ErrorsTestCase(unittest.TestCase):
    def test_delete_message_error(self):
        with self.assertRaises(SQSErrorResponse) as e:
            parse_xml_result_response(
                action="DeleteMessage",
                body=load_fixture("error.xml"),
            )
        exception = e.exception
        self.assertEqual(exception.request_id, "42d59b56-7407-4c4a-be0f-4c88daeea257")
        self.assertEqual(exception.error.type, "Sender")
        self.assertEqual(exception.error.code, "InvalidParameterValue")
        self.assertEqual(
            exception.error.message,
            (
                "Value (quename_nonalpha) for parameter QueueName is invalid.\n         "
                "Must be an alphanumeric String of 1 to 80 in length."
            ),
        )

    def test_unknown_error(self):
        with self.assertRaises(SQSErrorResponse) as e:
            parse_xml_result_response(
                action="ReceiveMessage",
                body=load_fixture("error_500.xml"),
            )
        exception = e.exception
        self.assertEqual(exception.request_id, "9ae1448a-3d1c-4b7f-b699-f6407e9dc5f2")
        self.assertEqual(exception.error.type, "Sender")
        self.assertEqual(exception.error.code, "InternalFailure")
        self.assertEqual(
            exception.error.message,
            "The request processing has failed because of an unknown error, exception or failure.",
        )

    def test_signature_does_not_match(self):
        with self.assertRaises(SQSErrorResponse) as e:
            parse_xml_result_response(
                action="SendMessage",
                body=load_fixture("error_signature.xml"),
            )
        exception = e.exception
        self.assertEqual(exception.request_id, "f679cf26-effe-5e59-81ca-92cf5c4c713b")
        self.assertEqual(exception.error.type, "Sender")
        self.assertEqual(exception.error.code, "SignatureDoesNotMatch")
