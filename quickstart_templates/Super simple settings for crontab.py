"""
This template is written by @Edhim

What does this quickstart script aim to do?
- I am using simple settings for my personal account with a crontab each 3H, it's been working since 5 months with no problem.
"""


import os
from instapy import InstaPy
from instapy.util import smart_run



# get a session!
session = InstaPy(username='', password='')


# let's go! :>
with smart_run(session):
    # settings
    session.set_relationship_bounds(enabled=False,
                                     potency_ratio=-1.21,
                                     delimit_by_numbers=True,
                                      max_followers=4590,
                                      max_following=5555,
                                      min_followers=45,
                                      min_following=77)
    session.set_do_comment(True, percentage=50)
    session.set_comments(['aMazing!', 'So cool!!', 'Nice!', 'wow looks nice!', 'this is awesome!'])

    # activity
    session.like_by_tags(['xxx', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx', 'xxx'], amount=8, skip_top_posts=True)



