from aiosqs.exceptions import SQSErrorResponse
from aiosqs.tests.cases import ActionTestCase


class ReceiveMessageTestCase(ActionTestCase):
    action = "ReceiveMessage"

    def test_no_messages(self):
        res = self.parseXMLResponse("receive_message_empty.xml")
        self.assertIsNone(res)

    def test_one_message(self):
        res = self.parseXMLResponse("receive_message.xml")
        self.assertEqual(
            res,
            [
                {
                    "MD5OfBody": "96db854b55b71e6b6298e93df0b6a176",
                    "Body": '{"test": 1}',
                    "ReceiptHandle": "1668283200-5c88d474-84c6-48c9-a713-0fb01b556d37",
                    "MessageId": "5c88d474-84c6-48c9-a713-0fb01b556d37",
                }
            ],
        )

    def test_parse_oneline_xml(self):
        res = self.parseXMLResponse("receive_message_ugly.xml")
        self.assertEqual(
            res,
            [
                {
                    "MD5OfBody": "cc12d89c4c6a34a4d8b78f970cd75534",
                    "Body": '{"external_id": 29, "market": "usdtrub", "side": "sell", "amount": "16.05"}',
                    "ReceiptHandle": "1669388400-f96963bf-3f5f-40e8-8df2-9ce9ff90adf8",
                    "MessageId": "f96963bf-3f5f-40e8-8df2-9ce9ff90adf8",
                },
            ],
        )

    def test_many_messages(self):
        res = self.parseXMLResponse("receive_messages.xml")
        self.assertEqual(
            res,
            [
                {
                    "MD5OfBody": "03ed928b62aee0c18f15dc123c695de9",
                    "Body": '{"test": 1, "external_id": 5555}',
                    "ReceiptHandle": "1668283200-b0eef428-d880-46fd-9c88-58882a421937",
                    "MessageId": "b0eef428-d880-46fd-9c88-58882a421937",
                },
                {
                    "MD5OfBody": "a88e5d79dc2948e662b90dc2857ba05c",
                    "Body": '{"test": 2, "external_id": 4444}',
                    "ReceiptHandle": "1668283200-0f8509ff-53fd-40ca-88c9-a3c8de61421c",
                    "MessageId": "0f8509ff-53fd-40ca-88c9-a3c8de61421c",
                },
                {
                    "MD5OfBody": "4078ede2743c523f62a4925e5ff90518",
                    "Body": '{"test": 3, "external_id": 3333}',
                    "ReceiptHandle": "1668283200-230c49a3-da11-40c1-a001-83fdf7767d82",
                    "MessageId": "230c49a3-da11-40c1-a001-83fdf7767d82",
                },
                {
                    "MD5OfBody": "a88e5d79dc2948e662b90dc2857ba05c",
                    "Body": '{"test": 4, "external_id": 2222}',
                    "ReceiptHandle": "1668283200-4ae4625c-0b91-4de4-833e-3847106606ef",
                    "MessageId": "4ae4625c-0b91-4de4-833e-3847106606ef",
                },
                {
                    "MD5OfBody": "03ed928b62aee0c18f15dc123c695de9",
                    "Body": '{"test": 5, "external_id": 1111}',
                    "ReceiptHandle": "1668283200-70616444-2a79-4f7b-8656-bbd48a546d60",
                    "MessageId": "70616444-2a79-4f7b-8656-bbd48a546d60",
                },
            ],
        )
        self.assertEqual(len(res), 5)

    def test_unknown_error(self):
        with self.assertRaises(SQSErrorResponse) as e:
            self.parseXMLResponse("error_500.xml")
        exception = e.exception
        self.assertEqual(exception.request_id, "9ae1448a-3d1c-4b7f-b699-f6407e9dc5f2")
        self.assertEqual(exception.error.type, "Sender")
        self.assertEqual(exception.error.code, "InternalFailure")
        self.assertEqual(
            exception.error.message,
            "The request processing has failed because of an unknown error, exception or failure.",
        )
