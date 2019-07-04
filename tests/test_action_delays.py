from instapy import util


def test_default_values_returned():
    assert util.get_action_delay("like") == 2
    assert util.get_action_delay("comment") == 2
    assert util.get_action_delay("follow") == 3
    assert util.get_action_delay("unfollow") == 10
