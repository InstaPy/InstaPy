"""
This template is written by @loopypanda

What does this quickstart script aim to do?
- My settings is for running InstaPY 24/7 with approximately 1400
follows/day - 1400 unfollows/day running follow until reaches 7500 and than
switch to unfollow until reaches 0.
"""

from instapy import InstaPy
from instapy.util import smart_run

# get a session!
session = InstaPy(username='', password='')

# let's go! :>
with smart_run(session):
    # general settings

    # session.set_relationship_bounds(enabled=True,
    # delimit_by_numbers=False, max_followers=12000, max_following=4500,
    # min_followers=35, min_following=35)
    # session.set_user_interact(amount=2, randomize=True, percentage=100,
    # media='Photo')
    session.set_do_follow(enabled=True, percentage=100)
    session.set_do_like(enabled=True, percentage=100)
    # session.set_comments(["Cool", "Super!"])
    # session.set_do_comment(enabled=False, percentage=80)
    # session.set_user_interact(amount=2, randomize=True, percentage=100,
    # media='Photo')

    # activity

    # session.interact_user_followers(['user1', 'user2', 'user3'],
    # amount=8000, randomize=True)
    # session.follow_user_followers(['user1', 'user2', 'user3'],
    # amount=8000, randomize=False, interact=True)
    # session.unfollow_users(amount=7500, nonFollowers=True, style="RANDOM",
    # unfollow_after=42*60*60, sleep_delay=3)
    session.like_by_tags(['???'], amount=8000)
