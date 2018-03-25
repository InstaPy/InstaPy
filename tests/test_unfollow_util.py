from unittest.mock import MagicMock, Mock, patch

from selenium.common.exceptions import NoSuchElementException

from instapy.unfollow_util import follow_given_user_followers, get_given_user_followers


class TestFollowGivenUserFollowers:

    def test_with_missing_count():
        """ensure follower count error returns empty"""
        webdriver = MagicMock()
        webdriver.find_element_by_xpath.side_effect = NoSuchElementException
        params = [MagicMock()] * 11
        res = follow_given_user_followers(webdriver, *params)
        assert len(res) == 0

    def test_with_no_followers():
        """ensure follower count is not zero"""
        webdriver = MagicMock()
        webdriver.find_element_by_xpath.return_value = Mock(text='0')
        params = [MagicMock()] * 11
        res = follow_given_user_followers(webdriver, *params)
        assert len(res) == 0

    def test_with_missing_link():
        """ensure follower link error returns empty"""
        webdriver = MagicMock()
        webdriver.find_element_by_xpath.return_value = Mock(text='123')
        webdriver.find_elements_by_xpath.side_effect = BaseException
        params = [MagicMock()] * 11
        res = follow_given_user_followers(webdriver, *params)
        assert len(res) == 0


class TestGetGivenUserFollowers:

    @patch('instapy.unfollow_util.scroll_bottom')
    @patch('instapy.unfollow_util.sleep')
    def test_following_link_is_lowercase(self, sleep, scroll_bottom):
        browser = MagicMock()
        browser.find_element_by_xpath.side_effect = [Mock(text='123'), MagicMock(), MagicMock()]
        res = get_given_user_followers(browser, 'FoOb2r', 10, [], MagicMock(), False, MagicMock())
        assert not res
        assert 'foob2r' in browser.find_element_by_xpath.call_args_list[1][0][0]

    @patch('instapy.unfollow_util.scroll_bottom')
    @patch('instapy.unfollow_util.sleep')
    def test_following_link_returns_on_fail(self, sleep, scroll_bottom):
        browser = MagicMock()
        browser.find_element_by_xpath.side_effect = [Mock(text='123'), NoSuchElementException()]
        logger = MagicMock()
        res = get_given_user_followers(browser, 'FoOb2r', 10, [], MagicMock(), False, logger)
        assert not res
        assert logger.error.call_count == 1
