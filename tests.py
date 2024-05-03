import unittest
from datetime import datetime, timedelta

from cryptshare.helpers import clean_string_list, clean_expiration


class TestSendTransfer(unittest.TestCase):
    def test_clean_string_list(self):
        self.assertEqual(clean_string_list(["a", "b", "c"]), ["a", "b", "c"])
        self.assertEqual(clean_string_list("a b"), ["a", "b"])
        self.assertEqual(clean_string_list(None), [])
        self.assertEqual(clean_string_list(""), [])
        self.assertEqual(clean_string_list("A"), ["A"])

    def test_clean_expiration(self):
        now = datetime.now()
        default_days = 2
        self.assertEqual(clean_expiration("tomorrow").date(), (now + timedelta(days=1)).date())
        self.assertEqual(
            clean_expiration("", default_days=default_days).date(), (now + timedelta(days=default_days)).date()
        )
        default_days = 4
        self.assertEqual(
            clean_expiration(None, default_days=default_days).date(), (now + timedelta(days=default_days)).date()
        )
        self.assertEqual(clean_expiration("1d").date(), (now + timedelta(days=1)).date())
        self.assertEqual(clean_expiration("1w").date(), (now + timedelta(weeks=1)).date())
        self.assertEqual(clean_expiration("1m").date(), (now + timedelta(weeks=4)).date())
        self.assertEqual(clean_expiration("2024-01-01").date(), datetime(2024, 1, 1).date())
        self.assertEqual(clean_expiration("1.1.2024").date(), datetime(2024, 1, 1).date())
        self.assertEqual(clean_expiration("01.01.2024").date(), datetime(2024, 1, 1).date())
        self.assertEqual(clean_expiration("1.1.2024 12:12:12").date(), datetime(2024, 1, 1).date())
        self.assertEqual(clean_expiration("01.01.2024 12:12:12").date(), datetime(2024, 1, 1).date())
        self.assertEqual(clean_expiration("1.1.2024 12:12:12+0000").date(), datetime(2024, 1, 1).date())

    # def test_send_transfer(self):
    #    self.assertEqual(send_transfer(), "Transfer sent successfully")


if __name__ == "__main__":
    unittest.main()
