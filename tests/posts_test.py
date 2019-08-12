#!/usr/bin/env python3
"""
Tests related to comments
"""

import os
from instapy import InstaPy, smart_run
from instapy.models import Post, Comment, User

def test_values(link, session):
    post = Post(link=link)

    assert type(post.count_likes(session)) == int, "Like count should be a number"
    assert type(post.count_comments(session)) == int, "Comment count should be a number"


def test_user(link, session):
    post = Post(link=link)
    user = post.get_user(session)

    assert type(user) == User, "Post user should be a User objects"

def test_comments(link, session):
    post = Post(link=link)
    comments = post.get_comments(session, offset=3, limit=None, randomize=False)

    for comment in comments:
        assert type(comment) == Comment, "Comments should be a set of Comment objects"


def test_likers(link, session):
    post = Post(link=link)

    likers = post.get_likers(session, offset=2, limit=10)
    for liker in likers:
        assert type(liker) == User, "Likers should be a set of User objects"


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
        test_values("https://www.instagram.com/p/B04q16ZHd-X/", session)
        test_user("https://www.instagram.com/p/B04q16ZHd-X/", session)
        # test_comments("https://www.instagram.com/p/B04q16ZHd-X/", session)
        # test_likers("https://www.instagram.com/p/B04q16ZHd-X/", session)

    print("[+] all tests done")
