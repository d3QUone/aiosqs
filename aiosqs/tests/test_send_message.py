from aiosqs.exceptions import SQSErrorResponse
from aiosqs.tests.cases import ActionTestCase


class SendMessageTestCase(ActionTestCase):
    action = "SendMessage"

    def test_send_message_ok(self):
        res = self.parseXMLResponse("send_message.xml")
        self.assertEqual(
            res,
            {
                "MessageId": "acdf9b7f-a639-4a5b-9557-b4de52a56d01",
                "MD5OfMessageBody": "a88e5d79dc2948e662b90dc2857ba05c",
            },
        )

    def test_signature_does_not_match(self):
        with self.assertRaises(SQSErrorResponse) as e:
            self.parseXMLResponse("error_signature.xml")
        exception = e.exception
        self.assertEqual(exception.request_id, "f679cf26-effe-5e59-81ca-92cf5c4c713b")
        self.assertEqual(exception.error.type, "Sender")
        self.assertEqual(exception.error.code, "SignatureDoesNotMatch")
