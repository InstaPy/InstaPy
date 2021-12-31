""" Quickstart script for InstaPy usage """

# imports
from instapy import InstaPy
from instapy import smart_run
from instapy import set_workspace


# set workspace folder at desired location (default is at your home folder)
set_workspace(path=None)

# get an InstaPy session!
your_username = ' ' #input your username here
your_password = ' ' #input your password here

session = InstaPy(username = your_username,
                  password = your_password,
                  headless_browser = False) #headless browser if set True will run without displaying mozilla firefox in background


with smart_run(session):
    # general settings
    session.set_dont_include(["friend1", "friend2", "friend3"])

    # activity
    session.like_by_tags(["natgeo"], amount=10)
