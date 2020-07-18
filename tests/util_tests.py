import unittest
from instapy.util import evaluate_mandatory_words

# Note: This file is using a different name scheme than existing tests
# so that unittest can be run with -p *_tests.py to discover all compatible tests in the tests directory


class UtilsTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_evaluate_mandatory_words(self):
        text = "a b c d e f g"

        self.assertTrue(evaluate_mandatory_words(text, ["a", "B", "c"]))
        self.assertTrue(evaluate_mandatory_words(text, ["a", "B", "z"]))
        self.assertTrue(evaluate_mandatory_words(text, ["x", "B", "z"]))
        self.assertFalse(evaluate_mandatory_words(text, ["x", "y", "z"]))
        self.assertTrue(evaluate_mandatory_words(text, [["a", "f", "e"]]))
        self.assertTrue(evaluate_mandatory_words(text, ["a", ["x", "y", "z"]]))
        self.assertTrue(evaluate_mandatory_words(text, [["x", "y", "z"], "a"]))
        self.assertFalse(evaluate_mandatory_words(text, [["x", "y", "z"], "v"]))
        self.assertTrue(evaluate_mandatory_words(text, [["a", "b", "d"], "v"]))
        self.assertTrue(evaluate_mandatory_words(text, [["a", "b", ["d", "x"]], "v"]))
        self.assertFalse(evaluate_mandatory_words(text, [["a", "z", ["d", "x"]], "v"]))
        self.assertTrue(evaluate_mandatory_words(text, [["a", "b", [["d", "e"], "x"]]]))
        self.assertFalse(
            evaluate_mandatory_words(text, [["a", "b", [["d", "z"], "x"]]])
        )
