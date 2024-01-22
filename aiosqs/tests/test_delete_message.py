from aiosqs.exceptions import SQSErrorResponse
from aiosqs.tests.cases import ActionTestCase


class DeleteMessageTestCase(ActionTestCase):
    action = "DeleteMessage"

    def test_delete_message_ok(self):
        res = self.parseXMLResponse("delete_message.xml")
        self.assertIsNone(res)

    def test_delete_message_error(self):
        with self.assertRaises(SQSErrorResponse) as e:
            self.parseXMLResponse("error.xml")
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
