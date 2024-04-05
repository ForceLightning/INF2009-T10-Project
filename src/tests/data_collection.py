"""Runs tests on the data collection methods in util/wifi_bt_processing.py.
"""

import os
import unittest

from util.wifi_bt_processing import parse_wifi_data, parse_bt_data


class TestDataCollectionMethods(unittest.TestCase):
    """Test case for data collection methods."""

    def test_bt_parse(self):
        """Tests the parsing of bluetooth data from a file."""
        bt_data = os.path.join(os.path.dirname(__file__), "test_data/bt_data.txt")
        with open(bt_data, "r", encoding="utf-8") as f:
            test_data = f.read()
        self.assertEqual(parse_bt_data(test_data.splitlines()), 21)

    def test_wifi_parse(self):
        """Tests the parsing of wifi data from a preformatted string."""
        test_data = r""":EC\:08\:6B\:62\:EC\:6F:ap_1:97
 :30\:23\:03\:47\:90\:F7:ap_2:89
 :E8\:9F\:80\:F0\:54\:57:ap_3:80
 :EE\:9F\:80\:F0\:54\:57:ap_4:80
 :84\:D8\:1B\:27\:44\:EF:ap_5:22
 :DF\:F8\:2E\:51\:44\:EF:ap_6:21
 :84\:D8\:1B\:27\:44\:EC:ap_7:55
        """
        test_output = [
            (r"EC\:08\:6B\:62\:EC\:6F", "ap_1", 97),
            (r"30\:23\:03\:47\:90\:F7", "ap_2", 89),
            (r"E8\:9F\:80\:F0\:54\:57", "ap_3", 80),
            (r"EE\:9F\:80\:F0\:54\:57", "ap_4", 80),
            (r"84\:D8\:1B\:27\:44\:EC", "ap_7", 55),
        ]
        self.assertEqual(parse_wifi_data(test_data.splitlines()), test_output)


def suite() -> unittest.TestSuite:
    """Returns a test suite for data collection methods.

    :return: Test suite for data collection methods
    :rtype: unittest.TestSuite
    """
    s = unittest.TestSuite()
    s.addTest(TestDataCollectionMethods("test_bt_parse"))
    s.addTest(TestDataCollectionMethods("test_wifi_parse"))
    return s


if __name__ == "__main__":
    unittest.main()
