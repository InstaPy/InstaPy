from __future__ import with_statement
from instapy import InstaPy
import schedule
import time
from time import sleep
import sys
import signal, time
from contextlib import contextmanager
from getuser import get_one_user

user = get_one_user()

session = InstaPy(
    username=user['username'],
    password=user['password'],
    custom_user_agent=user['useragent'],
    headless_browser=user['headless_browser']
    )

session.login()

# set up all the settings
session.set_upper_follower_count(limit=user['follower_upper_limit'])
session.set_lower_follower_count(limit=user['follower_lower_limit'])
session.set_do_follow(enabled=user['do_follow'], percentage=user['follow_percentage'])
session.set_do_comment(user['do_comment'], percentage=user['comment_percentage'])
session.set_comments(user['comments'])
session.set_dont_like(user['dont_like'])
session.unfollow_users(amount=user['unfollow_count'], onlyInstapyFollowed=True, onlyNotFollowMe=True, sleep_delay=60)
session.set_dont_unfollow_active_users(enabled=True, posts=5)
# session.set_fan_accounts(['futiconaki'], username)
session.interact_by_users(user['fans'], amount=5, randomize=True, media='Photo')


# do the actual liking
session.like_by_tags(user['tags'], amount=user['like_by_tags'])

# end the bot session
session.end()