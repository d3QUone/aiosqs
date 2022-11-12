import unittest

from aiosqs.parser import parse_xml_result_response
from aiosqs.tests.utils import load_fixture


class ReceiveMessageTestCase(unittest.TestCase):
    maxDiff = None
    action = "ReceiveMessage"

    def test_no_messages(self):
        res = parse_xml_result_response(
            action=self.action,
            body=load_fixture("receive_message_empty.xml"),
        )
        self.assertIsNone(res)

    def test_one_message(self):
        res = parse_xml_result_response(
            action=self.action,
            body=load_fixture("receive_message.xml"),
        )
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

    def test_many_messages(self):
        res = parse_xml_result_response(
            action=self.action,
            body=load_fixture("receive_messages.xml"),
        )
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
