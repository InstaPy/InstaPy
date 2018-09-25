""" Quickstart script for InstaPy usage """
# imports
from instapy import InstaPy
from instapy.util import smart_run



# login credentials
insta_username = ''
insta_password = ''

# get an InstaPy session!
session = InstaPy(username=insta_username,
                  password=insta_password,
                   headless_browser=False,
                    multi_logs=True)


with smart_run(session):
    """ Activity flow """
    # settings
    session.set_quota_supervisor(enabled=True,
                                  sleep_after=["likes"],
                                   peak_likes=(66, 700),
                                   peak_server_calls=(None, 4500))
    session.set_relationship_bounds(enabled=True,
                                     potency_ratio=1.07,
                                      delimit_by_numbers=True,
                                       max_followers=4590,
                                       max_following=5555,
                                        min_followers=45,
                                        min_following=77)
    session.set_dont_include(["friend1", "friend2", "friend3"])
    session.set_dont_like(["pizza", "#store"])
    session.set_do_comment(True, percentage=14)
    session.set_comments(["Brilliant",
                          "So wonderful!",
                          "Extraordinarily good.",
                          "A way so marvelous..",
                          "Literally a breathtaking capture!",
                          "You have a gallery so neat!",
                          "You are a sharp shooter, @{}!"])

    # actions
    session.like_by_tags(["natgeo"], amount=10)



