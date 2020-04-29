import unittest

from instapy import util


class TestFileHandling(unittest.TestCase):
    """Unit tests for file_handling function"""

    # list of expected entries
    global expected_entries
    expected_entries = ["photography", "portrait", "minimalistic"]

    def test_valid_entries(self):
        """Check file_handling with valid entries"""
        actual_entries = util.file_handling("tests/resources/valid_target_list.txt")
        self.assertListEqual(actual_entries, expected_entries)

    def test_invalid_entries(self):
        """Check file_handling with invalid entries"""
        actual_entries = util.file_handling("tests/resources/invalid_target_list.txt")
        self.assertListEqual(actual_entries, expected_entries)

    def test_invalid_filepath(self):
        """Check whether it raises an exception when the filepath is invalid"""
        actual_entries = util.file_handling("invalid_filepath")
        self.assertListEqual(actual_entries, ["FileNotFoundError"])
