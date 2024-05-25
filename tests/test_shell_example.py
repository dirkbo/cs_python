import os
import unittest
from datetime import datetime, timedelta

from dotenv import load_dotenv

from cryptshare import CryptshareValidators
from examples.shell_example.helpers import ExtendedCryptshareValidators
from test_cryptshare import TestCryptshareValidators


class TestExtendedCryptshareValidators(TestCryptshareValidators):
    def __init__(self, *args, **kwargs):
        super(TestCryptshareValidators, self).__init__(*args, **kwargs)
        self.cls = ExtendedCryptshareValidators()

    def test_class(self):
        self.assertTrue(issubclass(self.cls.__class__, CryptshareValidators))
        self.assertTrue(isinstance(self.cls, ExtendedCryptshareValidators))

    def test_clean_string_list(self):
        self.assertEqual(self.cls.clean_string_list(["a", "b", "c"]), list(("a", "b", "c")))
        self.assertEqual(self.cls.clean_string_list("a b"), ["a", "b"])
        self.assertEqual(self.cls.clean_string_list(None), [])
        self.assertEqual(self.cls.clean_string_list(""), [])
        self.assertEqual(self.cls.clean_string_list("A"), ["A"])
        self.assertEqual(self.cls.clean_string_list("A"), ["A"])
        self.assertEqual(self.cls.clean_string_list(1), [])
        self.assertEqual(self.cls.clean_string_list((1, 2, 3)), ["1", "2", "3"])
        self.assertEqual(self.cls.clean_string_list({1: "2", 2: "2", "3": "3"}), ["1", "2", "3"])
        self.assertEqual(self.cls.clean_string_list({1, 2, 3}), ["1", "2", "3"])

    def test_clean_expiration(self):
        now = datetime.now()
        default_days = 2
        self.assertEqual(
            self.cls.clean_expiration("tomorrow").date(), (now + timedelta(days=1)).date()
        )
        self.assertEqual(self.cls.clean_expiration(now).date(), now.date())
        self.assertEqual(
            self.cls.clean_expiration("", default_days=default_days).date(),
            (now + timedelta(days=default_days)).date(),
        )
        default_days = 4
        self.assertEqual(
            self.cls.clean_expiration(None, default_days=default_days).date(),
            (now + timedelta(days=default_days)).date(),
        )
        self.assertEqual(self.cls.clean_expiration("1d").date(), (now + timedelta(days=1)).date())
        self.assertEqual(self.cls.clean_expiration("1w").date(), (now + timedelta(weeks=1)).date())
        self.assertEqual(self.cls.clean_expiration("1m").date(), (now + timedelta(weeks=4)).date())
        self.assertEqual(
            self.cls.clean_expiration("2024-01-01").date(), datetime(2024, 1, 1).date()
        )
        self.assertEqual(
            self.cls.clean_expiration("2024-01-01 ").date(), datetime(2024, 1, 1).date()
        )
        self.assertEqual(
            self.cls.clean_expiration("2024-01-21T13:01").date(), datetime(2024, 1, 21).date()
        )
        self.assertEqual(self.cls.clean_expiration("1.1.2024").date(), datetime(2024, 1, 1).date())
        self.assertEqual(
            self.cls.clean_expiration("01.01.2024").date(), datetime(2024, 1, 1).date()
        )
        self.assertEqual(
            self.cls.clean_expiration("1.1.2024 12:12:12").date(), datetime(2024, 1, 1).date()
        )
        self.assertEqual(
            self.cls.clean_expiration("1.1.2024T12:12:12+0200").date(), datetime(2024, 1, 1).date()
        )
        self.assertEqual(
            self.cls.clean_expiration("1.1.2024T12:12:12 +0200").date(), datetime(2024, 1, 1).date()
        )
        self.assertEqual(
            self.cls.clean_expiration("01.01.2024 12:12:12").date(), datetime(2024, 1, 1).date()
        )
        self.assertEqual(
            self.cls.clean_expiration("1.1.2024 12:12:12+0000").date(), datetime(2024, 1, 1).date()
        )
        self.assertEqual(
            self.cls.clean_expiration("2024-01-01T08:01:55+0200").date(),
            datetime(2024, 1, 1).date(),
        )
        with self.assertRaises(ValueError):
            self.cls.clean_expiration("20sdgdfgdfghdsghf0")

    def test_is_valid_multiple_emails(self) -> None:
        self.assertTrue(self.cls.is_valid_multiple_emails(""))
        self.assertTrue(self.cls.is_valid_multiple_emails("test@example.com"))
        self.assertTrue(self.cls.is_valid_multiple_emails("test@example.com example@example.com"))
        self.assertFalse(self.cls.is_valid_multiple_emails("test.com"))

    def test_is_valid_expiration(self) -> None:
        now = datetime.now()
        self.assertTrue(self.cls.is_valid_expiration(now))
        self.assertFalse(self.cls.is_valid_expiration(""))
        self.assertFalse(self.cls.is_valid_expiration("20sdgdfgdfghdsghf0"))

    def test_twilio_sms_is_configured(self) -> None:
        load_dotenv()
        twilio_account = os.getenv("TWILIO_ACCOUNT_SID", False)
        twilio_aut = os.getenv("TWILIO_AUTH_TOKEN", False)
        twilio_phone = os.getenv("TWILIO_SENDER_PHONE", False)
        if twilio_account and twilio_aut and twilio_phone:
            self.assertTrue(self.cls.twilio_sms_is_configured())
        else:
            self.assertFalse(self.cls.twilio_sms_is_configured())


if __name__ == "__main__":
    unittest.main()
