""" Quickstart script for InstaPy usage """

# imports
from instapy import InstaPy
from instapy import smart_run
from instapy import set_workspace


# set workspace folder at desired location (default is at your home folder)
set_workspace(path=None)

user="contacting.john.doe"
pw="ThisIsJohnDoe"

# get an InstaPy session!
session = InstaPy(username=user, password=pw)

with smart_run(session):
    """ Activity flow """
    # general settings
    session.set_dont_include(["friend1", "friend2", "friend3"])

    # activity
    session.set_user_interact(amount=3, randomize=True, percentage=100,
                              media='Photo')
    session.set_simulation(enabled=False)
    session.set_do_like(enabled=True, percentage=100)
    session.set_ignore_users([])
    session.set_do_comment(enabled=True, percentage=35)
    session.set_do_follow(enabled=True, percentage=25, times=1)
    session.set_comments([])
    session.set_ignore_if_contains([])
    session.set_action_delays(enabled=True, like=40)
    session.interact_user_followers(['vegan'], amount=340)
