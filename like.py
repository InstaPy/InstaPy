""" Quickstart script for InstaPy usage """

# imports
from instapy import InstaPy
from instapy import smart_run
from instapy import set_workspace
import xanadyCred
import random

# login credentials
insta_username = xanadyCred.username
insta_password = xanadyCred.password

# set workspace folder at desired location (default is at your home folder)
set_workspace(path=None)

# get an InstaPy session!
# set headless_browser=True to run InstaPy in the background
session = InstaPy(username=insta_username,
                  password=insta_password,
                  headless_browser=True,
                  nogui=True)

with smart_run(session):
    # activity
    session.like_by_tags(["siouxfalls"], amount=10)
    session.like_by_feed(amount=20, randomize=True, unfollow=False, interact=True)
    session.like_by_locations(['213512618'], amount=10, skip_top_posts=True)

    #stories
    session.set_do_story(enabled=True, percentage=70, simulate=True)
    session.story_by_tags(['siouxfalls'])
