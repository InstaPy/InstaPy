from instapy import InstaPy
import schedule
import time
from time import sleep
import sys

# insta_username = 'futiconaki'
# insta_password = 'al7217'
#
# def job():
#     try:
#         session = InstaPy(username=insta_username, password=insta_password)
#         session.login()
#
#         # set up all the settings
#         session.set_upper_follower_count(limit=2500)
#         session.set_do_follow(enabled=True, percentage=10)
#         session.set_do_comment(True, percentage=2)
#         session.set_comments(['love it!'])
#         session.set_dont_include(['friend1', 'friend2', 'friend3'])
#         session.set_dont_like(['nsfw', 'hot', 'sexy'])
#
#         # do the actual liking
#         session.like_by_tags(['realestate', 'estate'], amount=100)
#
#         # end the bot session
#         session.end()
#     except:
#         import traceback
#         print(traceback.format_exc())
#
# schedule.every().day.at("13:16").do(job)
# schedule.every().day.at("16:22").do(job)
#
# while True:
#     schedule.run_pending()
#     time.sleep(1)

users = [
    {'insta_username': 'dianederoyan', 'insta_password': 'al7217'},
    {'insta_username': 'futiconaki', 'insta_password': 'al7217'}
]

username = users[int(sys.argv[1])]['insta_username']
password = users[int(sys.argv[1])]['insta_password']

session = InstaPy(
    username=username,
    password=password,
    custom_user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_1 like Mac OS X) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0 Mobile/15C153 Safari/604.1",
    )

session.login()

# set up all the settings
session.set_upper_follower_count(limit=2500)
session.set_do_follow(enabled=True, percentage=10)
session.set_do_comment(True, percentage=2)
session.set_comments(['love it!'])
session.set_dont_include(['friend1', 'friend2', 'friend3'])
session.set_dont_like(['nsfw', 'hot', 'sexy'])
session.unfollow_users(amount=8, onlyNotFollowMe=True, sleep_delay=70)
session.set_dont_unfollow_active_users(enabled=True, posts=5)
session.set_fan_accounts(['futiconaki'], username)

# do the actual liking
session.like_by_tags(['realestate', 'estate'], amount=100)

# end the bot session
session.end()

