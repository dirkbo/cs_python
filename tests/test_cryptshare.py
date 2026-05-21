import os
import unittest
from datetime import datetime
from unittest.mock import Mock, patch

from dotenv import load_dotenv
import requests

from cryptshare import CryptshareClient
from cryptshare.validators import CryptshareValidators


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

    def testSubject(self):
        self.assertTrue(self.cls.is_valid_transfer_subject("Test Subject"))
        self.assertFalse(self.cls.is_valid_transfer_subject("Test, Subject"))
        self.assertFalse(self.cls.is_valid_transfer_subject("Test< Subject"))
        self.assertFalse(self.cls.is_valid_transfer_subject("Test> Subject"))
        self.assertFalse(self.cls.is_valid_transfer_subject("Test\\ Subject"))
        self.assertFalse(self.cls.is_valid_transfer_subject("Test# Subject"))
        self.assertFalse(self.cls.is_valid_transfer_subject("Test[ Subject"))
        self.assertFalse(self.cls.is_valid_transfer_subject("Test] Subject"))
        self.assertFalse(self.cls.is_valid_transfer_subject("Test{ Subject"))
        self.assertFalse(self.cls.is_valid_transfer_subject("Test} Subject"))
        self.assertTrue(self.cls.is_valid_transfer_subject("Test| Subject"))
        self.assertTrue(self.cls.is_valid_transfer_subject("Test^ Subject"))
        self.assertFalse(self.cls.is_valid_transfer_subject("Test% Subject"))
        self.assertFalse(self.cls.is_valid_transfer_subject("Test$ Subject"))
        self.assertFalse(self.cls.is_valid_transfer_subject("Test~ Subject"))


class TestCryptshareNotificationMessage(unittest.TestCase):
    def test_notification_message(self):
        from cryptshare.notification_message import CryptshareNotificationMessage

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
        from cryptshare.notification_message import CryptshareNotificationMessage
        from cryptshare.sender import CryptshareSender
        from cryptshare.transfer_security_mode import (
            CryptshareTransferSecurityMode,
            OneTimePaswordSecurityModes,
        )
        from cryptshare.transfer_settings import CryptshareTransferSettings

        sender = CryptshareSender("Test Sender", "+1 234 567890", "test@example.com")
        notification = CryptshareNotificationMessage("A subject", "A notification message")
        security_mode = CryptshareTransferSecurityMode(password="password")
        self.assertEqual(security_mode.mode, OneTimePaswordSecurityModes.MANUAL)
        self.assertEqual(
            security_mode.data(),
            {"name": "ONE_TIME_PASSWORD", "config": {"passwordMode": "MANUAL", "password": "password"}},
        )
        security_mode = CryptshareTransferSecurityMode(mode=OneTimePaswordSecurityModes.NONE)
        self.assertEqual(security_mode.mode, OneTimePaswordSecurityModes.NONE)
        self.assertEqual(security_mode.data(), {"name": "ONE_TIME_PASSWORD", "config": {"passwordMode": "NONE"}})
        security_mode = CryptshareTransferSecurityMode(password="")
        self.assertEqual(security_mode.mode, OneTimePaswordSecurityModes.GENERATED)
        self.assertEqual(security_mode.data(), {"name": "ONE_TIME_PASSWORD", "config": {"passwordMode": "GENERATED"}})
        security_mode = CryptshareTransferSecurityMode(password="password", mode=OneTimePaswordSecurityModes.GENERATED)
        self.assertEqual(security_mode.mode, OneTimePaswordSecurityModes.GENERATED)
        self.assertEqual(
            security_mode.data(),
            {"name": "ONE_TIME_PASSWORD", "config": {"passwordMode": "GENERATED", "password": "password"}},
        )

        now = datetime.now()
        settings = CryptshareTransferSettings(
            sender,
            notification_message=notification,
            security_mode=security_mode,
            expiration_date=now,
        )

        timestr = now.astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")

        expiration_date = timestr[:-2] + ":" + timestr[-2:]

        self.assertEqual(
            settings.format_expiration_date(),
            expiration_date,
        )  # Maybe problems with DST?

        self.assertDictEqual(
            settings.data(),
            {
                "notificationMessage": notification.data(),
                "securityMode": security_mode.data(),
                "sender": sender.data(),
                "expirationDate": settings.expiration_date_str,
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
        self.assertEqual(settings.expiration_date, now)
        self.assertDictEqual(
            settings.data(),
            {
                "notificationMessage": notification.data(),
                "securityMode": security_mode.data(),
                "sender": sender.data(),
                "expirationDate": settings.expiration_date_str,
                "senderLanguage": "de",
                "sendDownloadSummary": False,
            },
        )


class TestCryptshareTransferPolicy(unittest.TestCase):
    def test_transfer_policy_settings_access(self):
        from cryptshare.transfer_policy import CryptshareTransferPolicy

        policy = CryptshareTransferPolicy(
            {
                "allowed": True,
                "settings": {
                    "maxRetentionPeriod": 7,
                    "sendUploadSummaryDefault": True,
                    "someNewSettingFromFutureApi": "enabled",
                },
            }
        )

        self.assertEqual(policy.maximum_retention_time, 7)
        self.assertTrue(policy.get_setting("sendUploadSummaryDefault"))
        self.assertTrue(policy.get_setting("send_upload_summary_default"))
        self.assertEqual(policy.get_setting("some_new_setting_from_future_api"), "enabled")
        self.assertEqual(policy.send_upload_summary_default, True)
        self.assertEqual(policy.some_new_setting_from_future_api, "enabled")


class TestCryptshareDownload(unittest.TestCase):
    def test_download_zip_info_supports_include_exclude_file_ids(self):
        from urllib.parse import parse_qs, urlparse

        client = CryptshareClient("https://example.com")
        download = client.download_transfer("1234567890", "secret")
        path = download.download_zip_info(include_file_ids=["f1", "f2"], exclude_file_ids=["f3"])
        parsed_query = parse_qs(urlparse(path).query)
        self.assertEqual(parsed_query.get("password"), ["secret"])
        self.assertEqual(parsed_query.get("includedFileIds"), ["f1,f2"])
        self.assertEqual(parsed_query.get("excludedFileIds"), ["f3"])


class TestCryptsharePollingApis(unittest.TestCase):
    def test_sender_polling_uses_new_endpoint_with_fallback(self):
        client = CryptshareClient("https://example.com")
        client.set_sender("sender@example.com")
        with patch.object(
            client,
            "_request",
            side_effect=[requests.HTTPError("404 Error"), [{"trackingId": "20240522-065711-1234567a"}]],
        ) as request_mock:
            response = client.get_sender_transfers(fields=["status", "sender.name"], limit=10, offset=2)
            self.assertEqual(response, [{"trackingId": "20240522-065711-1234567a"}])
            self.assertEqual(request_mock.call_count, 2)
            self.assertTrue(request_mock.call_args_list[0].args[1].endswith("/transfers/sender"))
            self.assertTrue(request_mock.call_args_list[1].args[1].endswith("/transfers"))
            self.assertEqual(
                request_mock.call_args_list[0].kwargs.get("params"),
                {"fields": "status,sender.name", "limit": 10, "offset": 2},
            )

    def test_recipient_polling_endpoint(self):
        client = CryptshareClient("https://example.com")
        client.set_sender("sender@example.com")
        with patch.object(client, "_request", return_value=[]) as request_mock:
            client.get_recipient_transfers(
                recipient_email="recipient@example.com",
                fields=["status", "sender.name", "sender.phone"],
                limit=5,
                offset=1,
            )
            self.assertTrue(request_mock.call_args.args[1].endswith("/recipient@example.com/transfers/recipient"))
            self.assertEqual(
                request_mock.call_args.kwargs.get("params"),
                {"fields": "status,sender.name,sender.phone", "limit": 5, "offset": 1},
            )

    def test_transfer_status_passes_fields_to_transfer_status_endpoint(self):
        client = CryptshareClient("https://example.com")
        client.set_sender("sender@example.com")
        client.set_client_id("client-id")
        with patch(
            "cryptshare.transfer.CryptshareTransfer.get_transfer_status",
            return_value={"status": {"state": "ACTIVE"}},
        ) as status_mock:
            result = client.transfer_status(
                transfer_tracking_id="20240522-065711-1234567a",
                fields=["status", "sender.name", "sender.phone"],
            )
            self.assertEqual(result, {"status": {"state": "ACTIVE"}})
            self.assertEqual(status_mock.call_args.kwargs.get("fields"), ["status", "sender.name", "sender.phone"])


class TestCryptshareApiRequests(unittest.TestCase):
    def test_handle_response_uses_plain_text_error_message(self):
        from cryptshare.api_requests import CryptshareApiRequests

        handler = CryptshareApiRequests()
        response = Mock()
        response.status_code = 404
        response.content = b"not-json-message"
        response.text = "Transfer no longer exists"
        response.headers = {}

        with self.assertRaises(requests.HTTPError) as exc:
            handler._handle_response(response)
        self.assertIn("Transfer no longer exists", str(exc.exception))


class TestCryptshareServerSide(unittest.TestCase):
    def test_server_side(self):
        load_dotenv()
        cryptshare_server = os.getenv("CRYPTSHARE_SERVER", "https://beta.cryptshare.com")
        if not cryptshare_server:
            self.skipTest("CRYPTSHARE_SERVER is not set")

        client = CryptshareClient(cryptshare_server)
        client.request_client_id()
        self.assertIsNotNone(client.header.client_id)
        self.assertIsInstance(client.get_human_readable_password_rules(), list)


class TestCryptshareClient(unittest.TestCase):
    def test_cryptshare_client(self):
        with self.assertRaises(ValueError):
            CryptshareClient("htp://example.com")
        client = CryptshareClient(
            os.getenv("CRYPTSHARE_SERVER", "https://beta.cryptshare.com"), target_api_version="1.9"
        )
        self.assertEqual(client._target_api_version, "1.9")
        self.assertEqual(client.server, os.getenv("CRYPTSHARE_SERVER", "https://beta.cryptshare.com"))
        client.server = os.getenv("CRYPTSHARE_SERVER", "https://beta.cryptshare.com")
        self.assertEqual(client.server, os.getenv("CRYPTSHARE_SERVER", "https://beta.cryptshare.com"))
        self.assertFalse(client.exists_client_id())
        client.reset_headers()
        client.request_client_id()
        self.assertIsNotNone(client.header.client_id)
        client.cors("localhost")
        password = client.get_password()
        self.assertTrue(client.is_valid_password(password))
        self.assertIsInstance(client.get_imprint(), dict)
        self.assertIsInstance(client.get_terms_of_use(), dict)
        self.assertIsInstance(client.get_available_languages(), list)
        self.assertTrue(client.exists_client_id())
        self.assertEqual(client.client_store_path, "client_store.json")
        self.assertEqual(client.server_client_store_path, f"client_store_{client.server_hash}.json")
        self.assertEqual(client.get_verification_from_store(email="example@example.com"), "")
        client.set_sender(
            "example@example.com",
            "Test Sender",
            "+1 234 567890",
        )
        self.assertEqual(client.sender_email, "example@example.com")
        self.assertIsInstance(client.get_emails(), list)

    def test_default_target_api_version(self):
        from cryptshare.base_client import CURRENT_MAXIMUM_TARGET_API_VERSION

        client = CryptshareClient("https://example.com")
        self.assertEqual(CURRENT_MAXIMUM_TARGET_API_VERSION, "1.15")
        self.assertEqual(client._target_api_version, "1.15")


if __name__ == "__main__":

    unittest.main()
