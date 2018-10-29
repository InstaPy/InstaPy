"""
This template is written by @jeremycjang

What does this quickstart script aim to do?
- Here's the configuration I use the most.

NOTES:
- Read the incredibly amazing advices & ideas from my experience at the end of this file :> 
"""


import time
import os
from tempfile import gettempdir
from instapy import InstaPy
from instapy.util import smart_run
from selenium.common.exceptions import NoSuchElementException



insta_username = 'username'
insta_password = 'password'

# get a session!
session = InstaPy(username=insta_username,
                  password=insta_password,
                  use_firefox=True,
                  page_delay=20,
                  bypass_suspicious_attempt=False,
                  nogui=False,
                  multi_logs=True)


# let's go! :>
with smart_run(session):
    # settings
    """ I don't use relationship bounds, but messed with it before and had some arbitrary numbers here
    """
    session.set_relationship_bounds(enabled=False,
                                     potency_ratio=-1.21,
                                     delimit_by_numbers=True,
                                      max_followers=99999999,
                                      max_following=5000,
                                      min_followers=70,
                                      min_following=10)
    """ Create a blacklist campaign to avoid bot interacting with users again. I never turn this off
    """
    session.set_blacklist(enabled=True, campaign='blacklist')
    session.set_do_like(enabled=True, percentage=100)
    session.set_do_comment(enabled=True, percentage=100)
    session.set_comments([':thumbsup:', ':raising_hands:', 'comment3'], media='Photo')
    session.set_comments(['comment4', ':smiling_face_with_sunglasses: :thumbsup:', ':comment6'], media='Video')
    #session.set_dont_include(['friend1', 'friend2', 'friend3'])
    session.set_dont_like(['#naked', '#sex', '#fight'])
    session.set_user_interact(amount=1, randomize=False, percentage=50)
    session.set_simulation(enabled=True)
    

    # activity
    
    """ First follow user followers leaves comments on these user's posts...
    """
    session.follow_user_followers(['user1', 'user2', 'user3'], amount=125, randomize=False, interact=True, sleep_delay=600)

    """ Second follow user follows doesn't comment on users' posts...
    """
    session.follow_user_followers(['user4', 'user5'], amount=50, randomize=False, interact=False, sleep_delay=600)

    """ Unfollow amount intentionally set higher than follow amount to catch accounts that were not unfollowed last run.
        Blacklist set to false as this seems to allow more users to get unfollowed for whatever reason.
    """
    session.set_blacklist(enabled=False, campaign='blacklist')
    session.unfollow_users(amount=1000, InstapyFollowed=(True,"all"), style="FIFO", unfollow_after=None, sleep_delay=600)




"""
EXTRA NOTES:

1-) A blacklist is used and never turned off so as to never follow the same user twice (unless their username is changed)

2-) The program is set to follow 475 people because this is the largest amount I've found so far that can be followed, commented on and unfollowed successfully within 24 hours. This can be customized of course, but please let me know if anyone's found a larger amount that can be cycled in 24 hours~

3-) Running this program every day, the program never actually follows a full 475 people because it doesn't grab enough links or grabs the links of people that have been followed already.

4-) I still have never observed the `media` parameter within `set comments` do anything, so a random comment from the 6 gets picked regardless of the media type

5-) For unknown reasons, the program will always prematurely end the unfollow portion without unfollowing everyone. More on this later

6-) I use two ```follow_user_followers``` sessions because I believe the comments I use are only well-received by the followers of users in the first ```follow_user_followers``` action.

7-) Linux PRO-tip: This is a really basic command line syntax that I learned yesterday, but less technical people may not have know about it as well. using `&&` in terminal, you can chain InstaPy programs! if you send:

```
python InstaPyprogram1 && python InstaPyprogram2
```

The shell will interpret it as "Run the InstaPyprogram1, then once it successfully completes immediately run InstaPyprogram2".
Knowing this, my workaround for the premature unfollow actions ending is to chain my template with another program that only has the unfollow code. There's no limit to how many programs you can chain with `&&`, so you can use your imagination on what can be accomplished :)


Hope this helps! Open to any feedback and improvements anyone can suggest ^.^
"""



