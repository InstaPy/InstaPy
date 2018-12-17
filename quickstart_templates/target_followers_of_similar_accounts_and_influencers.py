"""
This template is written by @Nuzzo235

What does this quickstart script aim to do?
- This script is targeting followers of similar accounts and influencers.
- This is my starting point for a conservative approach: Interact with the audience of influencers in your niche with the help of 'Target-Lists' and 'randomization'.

NOTES:
- For the ease of use most of the relevant data is retrieved in the upper part.
"""


import random
from instapy import InstaPy
from instapy.util import smart_run



# login credentials
insta_username = 'username'
insta_password = 'password'

# restriction data
dont_likes = ['#exactmatch', '[startswith', ']endswith', 'broadmatch']
ignore_users = ['user1', 'user2', 'user3']

""" Prevent commenting on and unfollowing your good friends (the images will still be liked)...
"""
friends = ['friend1', 'friend2', 'friend3']

""" Prevent posts that contain...
"""
ignore_list = []

# TARGET data
""" Set similar accounts and influencers from your niche to target...
"""
targets = ['user1', 'user2', 'user3']

""" Skip all business accounts, except from list given...
"""
target_business_categories = ['category1', 'category2', 'category3']

# COMMENT data
comments = ['comment1', 'comment2', 'comment3']

# get a session!
session = InstaPy(username=insta_username,
                      password=insta_password,
                        headless_browser=True,
                          disable_image_load=True,
                            multi_logs=True)

# let's go! :>
with smart_run(session):
    # HEY HO LETS GO
    # general settings
    session.set_dont_include(friends)
    session.set_dont_like(dont_likes)
    session.set_ignore_if_contains(ignore_list)
    session.set_ignore_users(ignore_users)
    session.set_simulation(enabled=True)
    session.set_relationship_bounds(enabled=True,
                                     potency_ratio=None,
                                     delimit_by_numbers=True,
                                      max_followers=7500,
                                      max_following=3000,
                                      min_followers=25,
                                      min_following=25,
                                      min_posts=10)

    session.set_skip_users(skip_private=True,
                            skip_no_profile_pic=True,
                             skip_business=True,
                             dont_skip_business_categories=[target_business_categories])

    session.set_user_interact(amount=3, randomize=True, percentage=80, media='Photo')
    session.set_do_like(enabled=True, percentage=90)
    session.set_do_comment(enabled=True, percentage=15)
    session.set_comments(comments, media='Photo')
    session.set_do_follow(enabled=True, percentage=40, times=1)


    # activities

    # FOLLOW+INTERACTION on TARGETED accounts
    """ Select users form a list of a predefined targets...
    """
    number = random.randint(3, 5)
    random_targets = targets

    if len(targets) <= number:
        random_targets = targets

    else:
        random_targets = random.sample(targets, number)

    """ Interact with the chosen targets...
    """
    session.follow_user_followers(random_targets, amount=random.randint(30,60), randomize=True, sleep_delay=600, interact=True)


    # UNFOLLOW activity
    """ Unfollow nonfollowers after one day...
    """
    session.unfollow_users(amount=random.randint(75,100), InstapyFollowed=(True, "nonfollowers"), style="FIFO", unfollow_after=24*60*60, sleep_delay=600)

    """ Unfollow all users followed by InstaPy after one week to keep the following-level clean...
    """
    session.unfollow_users(amount=random.randint(75,100), InstapyFollowed=(True, "all"), style="FIFO", unfollow_after=168*60*60, sleep_delay=600)



"""
Have fun while optimizing for your purposes, Nuzzo
"""
