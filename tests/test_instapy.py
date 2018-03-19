from unittest.mock import patch

import pytest

from instapy.instapy import InstaPy, InstaPyError


def test_like_by_users_with_no_usernames():
    """test no inputs returns instance without errors"""
    instapy = InstaPy(selenium_local_session=False)
    res = instapy.like_by_users([])
    assert isinstance(res, InstaPy)


@patch('instapy.instapy.load_follow_restriction')
def test_set_use_clarifai_raises_on_windows(load_follow_restriction):
    """windows not supported"""
    instapy = InstaPy(selenium_local_session=False)
    with patch('instapy.instapy.os'):
        with pytest.raises(InstaPyError):
            instapy.set_use_clarifai()
