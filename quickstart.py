# pylint: disable=C0103
import datetime
import random
from instapy import InstaPy
from instapy.time_util import sleep

insta_username = ''
insta_password = ''

# if you want to run this script on a server, 
# simply add nogui=True to the InstaPy() constructor
session = InstaPy(username=insta_username, password=insta_password)
session.login()

amountLike = random.randint(10, 30)
unfollowUserFollow = random.randint(20, 30)
followbyLikes = random.randint(10, 20)

session.set_interaction_limits(likes=15, comments=25, follows=10, unfollows=30, server_calls=1000)
session.set_upper_follower_count(limit=2500)
session.set_blacklist(enabled=True, campaign='mezar_campaign')
session.set_do_follow(enabled=True, percentage=followbyLikes, times=2)
#session.unfollow_users(amount=unfollowUserFollow, onlyNotFollowMe=True)
session.set_dont_like(['pizza', 'girl', 'nsfw'])
# do the actual liking
session.like_by_tags(['like4like'], amount=amountLike)

# end the bot session
session.end()