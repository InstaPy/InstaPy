# unfollow session!
# ------------------------------------->

# import instapy and add credentials
# ------------------------------------->
from instapy import InstaPy
from instapy.util import smart_run
import json

# importing all settings from settings.json
# ----------------------->
with open('settings.json') as settings_file:
    settings = json.load(settings_file)

# unfollow after settings
# ---------------------->
unfollow_after = 4*24*60*60
# unfollow_after = None # if you dont like to use the unfollow after feature

# get an InstaPy session!
# set headless_browser=True to run InstaPy in the background
# ------------------------------------->
session = InstaPy(username=settings['credentials']['username'], password=settings['credentials']['password'], headless_browser=False)

# Fire up Session!
# ------------------->
with smart_run(session):


    # Remove outgoing follow requests
    # Remove outgoing unapproved follow requests from private accounts
    # ------------------------------>
    # session.remove_follow_requests(amount=200, sleep_delay=400)

    # Don't unfollow active users
    # Prevents unfollow followers who have liked one of your latest 5 posts
    # ------------------------------>
    session.set_dont_unfollow_active_users(enabled=True, posts=5)

    # https://github.com/timgrossmann/InstaPy#unfollowing
    # if you like to unfollow only the users followed by InstaPy WHO do not follow you back, use the track- "nonfollowers";
    # session.unfollow_users(amount=300, InstapyFollowed=(True, "nonfollowers"), style="FIFO", unfollow_after=unfollow_after, sleep_delay=400)

    # Unfollow the users WHO do not follow you back:
    session.unfollow_users(amount=500, nonFollowers=True, style="RANDOM", unfollow_after=unfollow_after, sleep_delay=400)
