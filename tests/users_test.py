#!/usr/bin/env python3
"""
Tests related to users
"""

import os
from instapy import InstaPy, smart_run
from instapy.models import Post, Comment, User

def test_init(link, name, session):
    link_user = User(link=link)
    name_user = User(name=name)

    assert link_user.link == name_user.link, "Initialization with link or name should be equal"


def test_values(link, session):
    user = User(link=link)
    user.populate(session)
    user.refresh(session)

    assert type(user.post_count) == int, "Post count should be a number"
    assert type(user.follower_count) == int, "Follower count should be a number"
    assert type(user.following_count) == int, "Following count should be a number"


def test_follow(link, session):
    user = User(link=link)

    following = user.follow(session)
    unfollowing = user.unfollow(session)

    assert following, "State should be True after following"
    assert unfollowing, "State should be False after unfollowing"


def test_following(link, session):
    user = User(link=link)

    following = user.get_following(session, offset=2, limit=10)

    for followed in following:
        assert type(followed) == User, "Following should be a set of User objects"


def test_followers(link, session):
    user = User(link=link)

    followers = user.get_followers(session, offset=2, limit=10)
    for follower in followers:
        assert type(follower) == User, "Followers should be a set of User objects"



if __name__ == "__main__":
    """ Main entry point for tests """
    username = os.environ["INSTAGRAM_USERNAME"]
    password = os.environ["INSTAGRAM_PASSWORD"]

    session = InstaPy(
        username=username,
        password=password,
        headless_browser=False,
        show_logs=True
    )

    with smart_run(session):
        # test_init("https://www.instagram.com/nathanleeallen/", "nathanleeallen", session)
        # test_values("https://www.instagram.com/nathanleeallen/", session)
        # test_follow("https://www.instagram.com/nathanleeallen/", session)

        test_following("https://www.instagram.com/nathanleeallen/", session)

        test_followers("https://www.instagram.com/nathanleeallen/", session)

    print("[+] all tests done")
