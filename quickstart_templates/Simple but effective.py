"""
This template is written by @zackvega

What does this quickstart script aim to do?
- This is my simple but effective script.
"""


from instapy import InstaPy
from instapy.util import smart_run



insta_username = ''
insta_password = ''

# get a session!
session = InstaPy(username=insta_username,
                  password=insta_password,
                  headless_browser=True,
                  multi_logs=True)


# let's go! :>
with smart_run(session):
    # general settings
    session.set_relationship_bounds(enabled=True,
                                     potency_ratio=None,
                                     delimit_by_numbers=True,
                                      max_followers=6000,
                                      max_following=3000,
                                      min_followers=30,
                                      min_following=30)
    session.set_user_interact(amount=2, randomize=True, percentage=30, media='Photo')
    session.set_do_like(enabled=True, percentage=100)
    session.set_do_comment(enabled=True, percentage=5)
    session.set_comments(['Nice shot! @{}', 'I love your profile! @{}', '@{} Love it!', '@{} :heart::heart:',
                            '@{}:revolving_hearts::revolving_hearts:', '@{}:fire::fire::fire:'], media='Photo')

    # unfollow activity
    session.unfollow_users(amount=126, nonFollowers=True, style="RANDOM", unfollow_after=42*60*60, sleep_delay=300)

    # follow activity
    ammount_number=500
    session.follow_user_followers(['chrisburkard','danielkordan'], amount=ammount_number, randomize=False, interact=True, sleep_delay=240)
