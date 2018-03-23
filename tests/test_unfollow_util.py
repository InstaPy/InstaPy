from unittest.mock import MagicMock, Mock

from selenium.common.exceptions import NoSuchElementException

from instapy.unfollow_util import follow_given_user_followers


def test_follow_given_user_followers_with_missing_count():
    """ensure follower count error returns empty"""
    webdriver = MagicMock()
    webdriver.find_element_by_xpath.side_effect = NoSuchElementException
    params = [MagicMock()] * 11
    res = follow_given_user_followers(webdriver, *params)
    assert len(res) == 0


def test_follow_given_user_followers_with_no_followers():
    """ensure follower count is not zero"""
    webdriver = MagicMock()
    webdriver.find_element_by_xpath.return_value = Mock(text='0')
    params = [MagicMock()] * 11
    res = follow_given_user_followers(webdriver, *params)
    assert len(res) == 0


def test_follow_given_user_followers_with_missing_link():
    """ensure follower link error returns empty"""
    webdriver = MagicMock()
    webdriver.find_element_by_xpath.return_value = Mock(text='123')
    webdriver.find_elements_by_xpath.side_effect = BaseException
    params = [MagicMock()] * 9
    res = follow_given_user_followers(webdriver, 'foo', 10, *params)
    assert len(res) == 0
