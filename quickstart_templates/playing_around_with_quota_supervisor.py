"""
This template is written by @boldestfortune

What does this quickstart script aim to do?
- Just started playing around with Quota Supervisor, so I'm still tweaking these settings
"""

import random
from instapy import InstaPy
from instapy.util import smart_run

# get a session!
session = InstaPy(username='', password='')

# let's go! :>
with smart_run(session):
    # general settings
    session.set_quota_supervisor(enabled=True, sleep_after=["server_calls_h"], sleepyhead=True, stochastic_flow=True,
                                 notify_me=True,
                                 peak_likes=(57, 585), peak_follows=(48, None), peak_unfollows=(35, 402),
                                 peak_server_calls=(500, None))
    session.set_relationship_bounds(enabled=True,
                                    potency_ratio=-1.3,
                                    delimit_by_numbers=True,
                                    max_followers=10000,
                                    max_following=15000,
                                    min_followers=75,
                                    min_following=75)
    session.set_do_comment(False, percentage=10)
    session.set_comments(['aMEIzing!', 'So much fun!!', 'Nicey!'])
    session.set_use_clarifai(enabled=True, api_key='')
    session.clarifai_check_img_for(
        ['nsfw', 'gay', 'hijab', 'niqab', 'religion', 'shirtless', 'fitness', 'yamaka', 'rightwing'], comment=False)
    session.set_dont_like(
        ['dick', 'squirt', 'gay', 'homo', '#fit', '#fitfam', '#fittips', '#abs', '#kids', '#children', '#child',
         '[nazi',
         'jew', 'judaism', '[muslim', '[islam', 'bangladesh', '[hijab', '[niqab', '[farright', '[rightwing',
         '#conservative', 'death', 'racist'])
    session.set_do_follow(enabled=True, percentage=25, times=2)

    # like by tags activity
    session.set_smart_hashtags(['interiordesign', 'artshow', 'restaurant', 'artist', 'losangeles', 'newyork', 'miami'],
                               limit=10, sort='random', log_tags=True)
    session.set_dont_like(['promoter', 'nightclub'])
    session.set_delimit_liking(enabled=True, max=1005, min=10)
    session.like_by_tags(amount=random.randint(1, 15), use_smart_hashtags=True)

    # interact user followers activity
    session.set_user_interact(amount=5, randomize=True, percentage=50, media='Photo')
    session.set_do_follow(enabled=True, percentage=70)
    session.set_do_like(enabled=True, percentage=70)
    session.set_comments([u"👍"])
    session.set_do_comment(enabled=True, percentage=30)
    session.interact_user_followers([''], amount=random.randint(1, 10), randomize=True)

    # unfollow activity
    session.set_dont_unfollow_active_users(enabled=True, posts=3)
    session.unfollow_users(amount=random.randint(30, 100), InstapyFollowed=(True, "all"), style="FIFO",
                           unfollow_after=90 * 60 * 60, sleep_delay=501)
