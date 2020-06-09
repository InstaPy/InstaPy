import unittest
import logging
from instapy.comment_util import *

class BrowserMock:
    def __init__(self, caption=None, first_comment=None, comment_count=0):
        self.caption = caption
        self.first_comment = first_comment
        self.comment_count = comment_count

    def execute_script(self, script, *kwargs):
        if 'edge_media_preview_comment.count' in script:
            return self.comment_count
        if ".graphql.shortcode_media.comments_disabled" in script:
            return False
        elif "edge_media_to_caption.edges[0]['node']['text']" in script:
            return self.caption
        elif "edge_media_to_parent_comment.edges[0]['node']['text']" in script:
            return self.first_comment
        else:
            raise ValueError('Unexpected script')


class CommentsUtilTests(unittest.TestCase):
    def setUp(self):
        pass

    def test1(self):
        browser = BrowserMock(
            caption="\xe2\x81\xa0\nI'm in awe of the beauty of these glaciers.\xe2\x81\xa0\n. \xe2\x81\xa0\n.\xe2\x81\xa0\n.\xe2\x81\xa0\n#travel #wanderlust #adventure #icelandtravel #travelphotography #landscape #visiticeland #explore #globalwarming #photography #naturephotography #wheniniceland #landscapephotography #beautifuldestinations #traveling #neverstopexploring #nature #naturelovers #outdoors #visualsoflife #stayandwander #wanderlusting #traveltheworld #seetheworld #travelblogger #travelgram #iceland #glacier #hiking #ice",
            comment_count=5
        )
        mandatory_comments_words = []
        comments = [
            {'mandatory_words': ["icecave", "ice_cave"], 'comments': ["Nice shot. Ice caves are amazing", "Cool. Aren't ice caves just amazing?"]},
            {'mandatory_words': [["iceland", "winter"]], 'comments': ["Great shot. I just love Iceland in the winter", "Cool. Can't beat iceland in winter"]},
            {'mandatory_words': [["iceland", "waterfall"]], 'comments': ["Nice shot. I just love the waterfalls in Iceland", "Nothing like waterfalls in Iceland", "Nice waterfall!"]},
            {'mandatory_words': [["landscape", "sunset"]], 'comments': ["Lovely sunset", "Very nice sunset"]},
            {'mandatory_words': ["landscape", "waterfall"], 'comments': ["Nice waterfall", "What a lovely waterfall"]},
            {'mandatory_words': [["landscape", "glacier"]], 'comments': ["Nice shot. I just love glaciers!", "Love it. Ain't glaciers just great?"]},
            {'mandatory_words': [["landscape", "mountain"]], 'comments': ["Nice shot!", "Great shot", "very nice", u"👏👏👏"]},
            {'mandatory_words': [["landscape", "milkyway"], ["iceland", "milkyway"]], 'comments': ["Nice shot! The night sky is amazing", "Great shot. Love the milky way", "very nice"]},
            {'comments': ["Very nice!", "Great shot", "very nice", u"👏👏👏"]}
        ]

        (commenting_approved, selected_comments, disapproval_reason, ) = verify_mandatory_words(mandatory_comments_words, comments, browser, logging)
        self.assertEqual(commenting_approved, True)
        self.assertEqual(selected_comments, ["Nice shot. I just love glaciers!", "Love it. Ain't glaciers just great?"])
        # process_comments
