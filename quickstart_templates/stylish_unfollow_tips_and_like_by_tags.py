"""
This template is written by @Nocturnal-2

What does this quickstart script aim to do?
- I do some unfollow and like by tags mostly

NOTES:
- I am an one month old InstaPy user, with a small following. So my numbers in settings are bit conservative.
"""

from instapy import InstaPy
from instapy.util import smart_run

# get a session!
session = InstaPy(username='', password='')

# let's go! :>
with smart_run(session):
    """ Start of parameter setting """
    # don't like if a post already has more than 150 likes
    session.set_delimit_liking(enabled=True, max=150, min=0)

    # don't comment if a post already has more than 4 comments
    session.set_delimit_commenting(enabled=True, max=4, min=0)

    """I used to have potency_ratio=-0.85 and max_followers=1200 for set_relationship_bounds()
        Having a stricter relationship bound to target only low profiles users was not very useful,
        as interactions/sever calls ratio was very low. I would reach the server call threshold for
        the day before even crossing half of the presumed safe limits for likes, follow and comments (yes,
        looks like quiet a lot of big(bot) managed accounts out there!!).
        So I relaxed it a bit to -0.50 and 2000 respectively.
    """
    session.set_relationship_bounds(enabled=True,
                                    potency_ratio=-0.50,
                                    delimit_by_numbers=True,
                                    max_followers=2000,
                                    max_following=3500,
                                    min_followers=25,
                                    min_following=25)
    session.set_do_comment(True, percentage=20)
    session.set_do_follow(enabled=True, percentage=20, times=2)
    session.set_comments(['Amazing!', 'Awesome!!', 'Cool!', 'Good one!',
                          'Really good one', 'Love this!', 'Like it!', 'Beautiful!', 'Great!'])
    session.set_sleep_reduce(200)

    """ Get the list of non-followers
        I duplicated unfollow_users() to see a list of non-followers which I run once in a while when I time
        to review the list
    """
    # session.just_get_nonfollowers()

    # my account is small at the moment, so I keep smaller upper threshold
    session.set_quota_supervisor(enabled=True,
                                 sleep_after=["likes", "comments_d", "follows", "unfollows", "server_calls_h"],
                                 sleepyhead=True, stochastic_flow=True, notify_me=True,
                                 peak_likes=(100, 700),
                                 peak_comments=(25, 200),
                                 peak_follows=(48, 125),
                                 peak_unfollows=(35, 400),
                                 peak_server_calls=(None, 3000))
    """ End of parameter setting """

    """ Actions start here """
    # Unfollow users
    """ Users who were followed by InstaPy, but not have followed back will be removed in
        One week (168 * 60 * 60)
        Yes, I give a liberal one week time to follow [back] :)
    """
    session.unfollow_users(amount=25, InstapyFollowed=(True, "nonfollowers"), style="RANDOM",
                           unfollow_after=168 * 60 * 60,
                           sleep_delay=600)

    # Remove specific users immediately
    """ I use InstaPy only for my personal account, I sometimes use custom list to remove users who fill up my feed
        with annoying photos
    """
    # custom_list = ["sexy.girls.pagee", "browneyedbitch97"]
    #
    # session.unfollow_users(amount=20, customList=(True, custom_list, "all"), style="RANDOM",
    #                        unfollow_after=1 * 60 * 60, sleep_delay=200)

    # Like by tags
    """ I mostly use like by tags. I used to use a small list of targeted tags with a big 'amount' like 300
        But that resulted in lots of "insufficient links" messages. So I started using a huge list of tags with
        'amount' set to something small like 50. Probably this is not the best way to deal with "insufficient links"
        message. But I feel it is a quick work around.
    """

    session.like_by_tags(['tag1', 'tag2', 'tag3', 'tag4'], amount=300)

"""
-- REVIEWS --

@uluQulu:
- @Nocturnal-2, your template looks stylish, thanks for preparing it.

@nocturnal-2:
- I think it is good opportunity to educate and get educated [using templates of other people] :) ...

"""
