import unittest
from example import clean_string_list


class TestSendTransfer(unittest.TestCase):
    def test_clean_string_list(self):
        self.assertEqual(clean_string_list(["a", "b", "c"]), ["a", "b", "c"])
        self.assertEqual(clean_string_list("a b"), ["a", "b"])
        self.assertEqual(clean_string_list(None), [])
        self.assertEqual(clean_string_list(""), [])
        self.assertEqual(clean_string_list("A"), ["A"])

    # def test_send_transfer(self):
    #    self.assertEqual(send_transfer(), "Transfer sent successfully")


if __name__ == "__main__":
    unittest.main()
