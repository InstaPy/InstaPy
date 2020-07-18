import unittest
import logging
from instapy.comment_util import *

# Note: This file is using a different name scheme than existing tests
# so that unittest can be run with -p *_tests.py to discover all compatible tests in the tests directory


class BrowserMock:
    def __init__(self, caption=None, first_comment=None, comment_count=0):
        self.caption = caption
        self.first_comment = first_comment
        self.comment_count = comment_count

    def execute_script(self, script, *kwargs):
        if "edge_media_preview_comment.count" in script:
            return self.comment_count
        if ".graphql.shortcode_media.comments_disabled" in script:
            return False
        elif "edge_media_to_caption.edges[0]['node']['text']" in script:
            return self.caption
        elif "edge_media_to_parent_comment.edges[0]['node']['text']" in script:
            return self.first_comment
        else:
            raise ValueError("Unexpected script")


class CommentsUtilTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_verify_mandatory_words(self):
        browser = BrowserMock(caption="a B c D e F g", comment_count=5)
        mandatory_comments_words = []
        comments = [
            {"mandatory_words": ["x", "y", "z"], "comments": ["1"]},
            {"mandatory_words": [["x", "y", "z"], "v"], "comments": ["2"]},
            {"mandatory_words": [["a", "b", "d"], "v"], "comments": ["3"]},
            {"mandatory_words": [["a", "z", ["d", "x"]], "v"], "comments": ["4"]},
            {"mandatory_words": [["a", "f", "e"]], "comments": ["5"]},
            {"mandatory_words": ["a", "B", "z"], "comments": ["6"]},
            {"comments": ["9"]},
        ]

        (
            commenting_approved,
            selected_comments,
            disapproval_reason,
        ) = verify_mandatory_words(mandatory_comments_words, comments, browser, logging)
        self.assertTrue(commenting_approved)
        self.assertEqual(["3"], selected_comments)

        comments = [
            {"mandatory_words": ["x", "y", "z"], "comments": ["1"]},
            {"mandatory_words": [["x", "y", "z"], "v"], "comments": ["2"]},
            {"mandatory_words": [["a", "b", "z"], "v"], "comments": ["3"]},
            {"mandatory_words": [["a", "z", ["d", "x"]], "v"], "comments": ["4"]},
            {"mandatory_words": [["a", "f", "e"]], "comments": ["5"]},
            {"mandatory_words": ["a", "B", "z"], "comments": ["6"]},
            {"comments": ["9"]},
        ]
        (
            commenting_approved,
            selected_comments,
            disapproval_reason,
        ) = verify_mandatory_words(mandatory_comments_words, comments, browser, logging)
        self.assertTrue(commenting_approved)
        self.assertEqual(["5"], selected_comments)

        comments = [
            {"mandatory_words": ["x", "y", "z"], "comments": ["1"]},
            {"mandatory_words": [["x", "y", "z"], "v"], "comments": ["2"]},
            {"mandatory_words": [["a", "b", "z"], "v"], "comments": ["3"]},
            {"mandatory_words": [["a", "z", ["d", "x"]], "v"], "comments": ["4"]},
            {"mandatory_words": [["a", "f", "z"]], "comments": ["5"]},
            {"mandatory_words": ["a", "B", "z"], "comments": ["6"]},
            {"comments": ["9"]},
        ]
        (
            commenting_approved,
            selected_comments,
            disapproval_reason,
        ) = verify_mandatory_words(mandatory_comments_words, comments, browser, logging)
        self.assertTrue(commenting_approved)
        self.assertEqual(["6"], selected_comments)

        comments = [
            {"mandatory_words": ["x", "y", "z"], "comments": ["1"]},
            {"mandatory_words": [["x", "y", "z"], "v"], "comments": ["2"]},
            {"mandatory_words": [["a", "b", "z"], "v"], "comments": ["3"]},
            {"mandatory_words": [["a", "z", ["d", "x"]], "v"], "comments": ["4"]},
            {"mandatory_words": [["a", "f", "z"]], "comments": ["5"]},
            {"mandatory_words": ["x", "Y", "z"], "comments": ["6"]},
            {"comments": ["9"]},
        ]
        (
            commenting_approved,
            selected_comments,
            disapproval_reason,
        ) = verify_mandatory_words(mandatory_comments_words, comments, browser, logging)
        self.assertTrue(commenting_approved)
        self.assertEqual(["9"], selected_comments)

        comments = [
            {"mandatory_words": ["x", "y", "z"], "comments": ["1"]},
            {"mandatory_words": [["x", "y", "z"], "v"], "comments": ["2"]},
            {"mandatory_words": [["a", "b", "z"], "v"], "comments": ["3"]},
            {"mandatory_words": [["a", "z", ["d", "x"]], "v"], "comments": ["4"]},
            {"mandatory_words": [["a", "f", "z"]], "comments": ["5"]},
            {"mandatory_words": ["x", "Y", "z"], "comments": ["6"]},
        ]
        (
            commenting_approved,
            selected_comments,
            disapproval_reason,
        ) = verify_mandatory_words(mandatory_comments_words, comments, browser, logging)
        self.assertFalse(commenting_approved)
        self.assertEqual([], selected_comments)
