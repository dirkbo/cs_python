import inspect
import os
import sys
import unittest
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

# To work from tests folder, parent folder is added to path
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from cryptshare import CryptshareClient, CryptshareValidators


class TestCryptshareValidators(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestCryptshareValidators, self).__init__(*args, **kwargs)
        self.cls = CryptshareValidators()

    def test_class(self):
        self.assertTrue(isinstance(self.cls, CryptshareValidators))

    def test_email_validation(self):
        self.assertTrue(self.cls.is_valid_email("test@example.com"))
        self.assertFalse(self.cls.is_valid_email("testexample.com"))
        self.assertFalse(self.cls.is_valid_email("test@example"))
        self.assertFalse(self.cls.is_valid_email("testexample"))
        self.assertFalse(self.cls.is_valid_email("test@example."))
        self.assertFalse(self.cls.is_valid_email("@example.com"))
        self.assertFalse(self.cls.is_valid_email("test@.com"))
        self.assertTrue(self.cls.is_valid_email_or_blank(""))
        self.assertFalse(self.cls.is_valid_email_or_blank("test@exa,ple.com"))
        self.assertTrue(self.cls.is_valid_email_or_blank("test@example.com"))
        self.assertFalse(self.cls.is_valid_email(""))

    def test_server_validation(self):
        self.assertTrue(self.cls.is_valid_server_url("http://example.com"))
        self.assertTrue(self.cls.is_valid_server_url("https://example.com"))
        self.assertTrue(self.cls.is_valid_server_url("http://example.com:8080"))
        self.assertTrue(self.cls.is_valid_server_url("https://example.com:8080"))
        self.assertFalse(self.cls.is_valid_server_url("example.com"))
        self.assertFalse(self.cls.is_valid_server_url(""))
        self.assertFalse(self.cls.is_valid_server_url("http://example"))

    def test_tracking_id_validation(self):
        self.assertTrue(self.cls.is_valid_tracking_id_or_blank(""))
        self.assertTrue(self.cls.is_valid_tracking_id_or_blank("20240522-065711-H8UoUSI6"))

        self.assertFalse(self.cls.is_valid_tracking_id_or_blank("52345678-561234-1234567"))
        self.assertFalse(self.cls.is_valid_tracking_id_or_blank("12345678-561234-1234567a"))
        self.assertFalse(self.cls.is_valid_tracking_id_or_blank("12345678-561234-12345678 "))
        self.assertFalse(self.cls.is_valid_tracking_id_or_blank("123A5678-561234-12345678 "))
        self.assertFalse(self.cls.is_valid_tracking_id_or_blank("123A5678-123A56-12345678 "))
        self.assertFalse(self.cls.is_valid_tracking_id_or_blank("12345678-561234-12345678a"))
        self.assertFalse(self.cls.is_valid_tracking_id_or_blank("12345678-561234-12345678a"))
        self.assertFalse(self.cls.is_valid_tracking_id_or_blank("12345678-561234-12345678a"))
        self.assertFalse(self.cls.is_valid_tracking_id("12345678-561234-12345678"))
        self.assertFalse(self.cls.is_valid_tracking_id("12345678-561234-1234567"))
        self.assertFalse(self.cls.is_valid_tracking_id(""))
        self.assertFalse(self.cls.is_valid_tracking_id("12345678-123456-1234567a"))
        self.assertFalse(self.cls.is_valid_tracking_id("12345678-123456-12345678 "))
        self.assertFalse(self.cls.is_valid_tracking_id("12345678-123456-12345678a"))
        self.assertFalse(self.cls.is_valid_tracking_id("12345678-123456-12345678a"))
        self.assertFalse(self.cls.is_valid_tracking_id("12345678-123456-12345678a"))

        self.assertFalse(self.cls.is_valid_tracking_id_or_blank("20240522-065711-1234567"))
        self.assertTrue(self.cls.is_valid_tracking_id_or_blank("20240522-065711-1234567a"))
        self.assertFalse(self.cls.is_valid_tracking_id_or_blank("20240522-065711-12345678 "))
        self.assertFalse(self.cls.is_valid_tracking_id_or_blank("20240522-06A711-12345678"))
        self.assertFalse(self.cls.is_valid_tracking_id_or_blank("202A0522-065711-12345678"))
        self.assertFalse(self.cls.is_valid_tracking_id_or_blank("20240522-065711-12345678a"))
        self.assertFalse(self.cls.is_valid_tracking_id_or_blank("20240522-065711-12345678a"))
        self.assertFalse(self.cls.is_valid_tracking_id_or_blank("20240522-065711-12345678a"))
        self.assertTrue(self.cls.is_valid_tracking_id("20240522-065711-12345678"))
        self.assertFalse(self.cls.is_valid_tracking_id("20240522-065711-1234567"))
        self.assertTrue(self.cls.is_valid_tracking_id("20240522-065711-1234567a"))
        self.assertFalse(self.cls.is_valid_tracking_id("20240522-065711-12345678 "))
        self.assertFalse(self.cls.is_valid_tracking_id("20240522-065711-12345678a"))
        self.assertFalse(self.cls.is_valid_tracking_id("20240522-065711-12345678a"))
        self.assertFalse(self.cls.is_valid_tracking_id("20240522-065711-12345678a"))

    def test_transfer_id(self):
        self.assertTrue(self.cls.is_valid_transfer_id("1234567890"))
        self.assertTrue(self.cls.is_valid_transfer_id("123A567B90"))
        self.assertFalse(self.cls.is_valid_transfer_id("12345678a01"))
        self.assertFalse(self.cls.is_valid_transfer_id(""))
        self.assertFalse(self.cls.is_valid_transfer_id("12345A78 "))
        self.assertFalse(self.cls.is_valid_transfer_id("1234567"))

    def test_verification_code(self):
        self.assertTrue(self.cls.is_valid_verification_code("1234567890"))
        self.assertTrue(self.cls.is_valid_verification_code("123A567B90"))
        self.assertFalse(self.cls.is_valid_verification_code(""))
        self.assertFalse(self.cls.is_valid_verification_code("12345678a01"))
        self.assertFalse(self.cls.is_valid_verification_code("12345A78 "))
        self.assertFalse(self.cls.is_valid_verification_code("1234567"))


class TestCryptshareNotificationMessage(unittest.TestCase):
    def test_notification_message(self):
        from cryptshare.CryptshareNotificationMessage import (
            CryptshareNotificationMessage,
        )

        subject = "A subject"
        text = "A notification message for the recipient of the Transfer"
        message = CryptshareNotificationMessage(
            subject=subject,
            body=text,
        )
        self.assertEqual(message.data(), {"subject": subject, "body": text})
        self.assertEqual(message.language, "en")

        message = CryptshareNotificationMessage()
        self.assertEqual(message.data(), {"subject": "", "body": ""})
        self.assertEqual(message.language, "en")

        self.assertIsNone(message.detect_language())


class TestCryptshareTransferSettings(unittest.TestCase):
    def test_transfer_settings(self):
        from cryptshare import CryptshareSender
        from cryptshare.CryptshareNotificationMessage import (
            CryptshareNotificationMessage,
        )
        from cryptshare.CryptshareTransferSecurityMode import (
            CryptshareTransferSecurityMode,
        )
        from cryptshare.CryptshareTransferSettings import CryptshareTransferSettings

        sender = CryptshareSender("Test Sender", "+1 234 567890", "test@example.com")
        notification = CryptshareNotificationMessage("A subject", "A notification message")
        security_mode = CryptshareTransferSecurityMode(password="password")
        now = datetime.now()
        settings = CryptshareTransferSettings(
            sender,
            notification_message=notification,
            security_mode=security_mode,
            expiration_date=now,
        )

        timestamp = datetime(2024, 1, 1, 12, 12, 12)
        timestr = datetime(2024, 1, 1, 12, 12, 12).astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")

        expiration_date = timestr[:-2] + ":" + timestr[-2:]

        self.assertEqual(
            settings.format_expiration_date(timestamp),
            expiration_date,
        )  # Maybe problems with DST?

        self.assertDictEqual(
            settings.data(),
            {
                "notificationMessage": notification.data(),
                "securityMode": security_mode.data(),
                "sender": sender.data(),
                "expirationDate": settings.format_expiration_date(now),
            },
        )

        settings = CryptshareTransferSettings(
            sender,
            notification_message=notification,
            security_mode=security_mode,
            expiration_date=now,
            senderLanguage="de",
            sendDownloadSummary=False,
        )
        self.assertDictEqual(
            settings.data(),
            {
                "notificationMessage": notification.data(),
                "securityMode": security_mode.data(),
                "sender": sender.data(),
                "expirationDate": settings.format_expiration_date(now),
                "senderLanguage": "de",
                "sendDownloadSummary": False,
            },
        )


class TestCryptshareServerSide(unittest.TestCase):
    def test_server_side(self):
        load_dotenv()
        cryptshare_server = os.getenv("CRYPTSHARE_SERVER", None)
        if not cryptshare_server:
            self.skipTest("CRYPTSHARE_SERVER is not set")

        client = CryptshareClient(cryptshare_server)
        client.request_client_id()
        self.assertIsNotNone(client.header.client_id)


class TestCryptshareClient(unittest.TestCase):
    def test_cryptshare_client(self):
        client = CryptshareClient(os.getenv("CRYPTSHARE_SERVER", "https://beta.cryptshare.com"))
        self.assertEqual(client._server, os.getenv("CRYPTSHARE_SERVER", "https://beta.cryptshare.com"))
        client.request_client_id()
        self.assertIsNotNone(client.header.client_id)
        client.cors("localhost")


if __name__ == "__main__":
    unittest.main()
