""" Quickstart script for InstaPy usage """

# imports
from instapy import InstaPy, set_workspace, smart_run

# set workspace folder at desired location (default is at your home folder)
set_workspace(path=None)

# get an InstaPy session!
session = InstaPy()

with smart_run(session):
    # general settings
    session.set_dont_include(["friend1", "friend2", "friend3"])

    # activity
    session.like_by_tags(["natgeo"], amount=10)
