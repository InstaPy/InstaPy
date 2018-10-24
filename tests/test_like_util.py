from unittest.mock import MagicMock, patch

from instapy.like_util import check_link


class TestCheckLink:

    @patch('instapy.like_util.sleep')
    def test_inappropriate_text_on_dont_like(self, sleep):
        """when inappropriate the message is returned"""
        browser = MagicMock()
        browser.execute_script.side_effect = [
            [{'media': {'is_video': False, 'owner': {'username': 'john'}, 'caption': '#f\xf6o'}}],
            '']
        inappropriate, user_name, is_video, reason = check_link(
            browser, MagicMock(), ['#f'], [], MagicMock(), MagicMock(), MagicMock(),
            None, None, MagicMock())
        assert inappropriate is True
