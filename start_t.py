import os
import yaml
from instapy import InstaPy
from instapy.util import smart_run

# Importing datafile
current_path = os.path.abspath(os.path.dirname(__file__))
data = yaml.safe_load(open("%s/data.yaml" %(current_path) ))

# username = os.environ['IG_USER']
# password = os.environ['IG_PASS']
skip_friends_interaction = bool(os.environ['SKIP_FRIENDS_INTERACTION'])
skip_hashtags_interaction = bool(os.environ['SKIP_HASHTAGS_INTERACTION'])
skip_locations_interaction = bool(os.environ['SKIP_LOCATIONS_INTERACTION'])
skip_follow_unfollow = False #bool(os.environ['SKIP_FOLLOW_UNFOLLOW'])

# Setting data
creds = data["creds"]
hashtags = os.environ['HASHTAGS'].split(" ")[1:-1]
exceptions = os.environ['EXCEPTIONS'].split(" ")[1:-1]
friends = os.environ['LOCATIONS'].split(" ")[1:-1]
brands = os.environ['FRIENDS'].split(" ")[1:-1]
interests = os.environ['BRANDS'].split(" ")[1:-1]
artists = os.environ['INTERESTS'].split(" ")[1:-1]
locations = os.environ['ARTISTS'].split(" ")[1:-1]

# Comments
comments = [
  u"🔥🔥🔥",
  u"✨✨✨✨",
  u"⚡️️️️️️️⚡️️️️️️️⚡️️️️️️️",
  u"🙌🏼 🙌🏼",
  u"😻"
]


# ###############################
# # Interact with close friends #
# # - likes
# if skip_friends_interaction:
#   print('⚡️ Skipping liking friends posts')
# else:
#   print('❤️ Showing friends some love')
#   friend_list = InstaPy(username=creds['user'], password=creds['pass'],
#                         selenium_local_session=False, disable_image_load=True)
#   friend_list.set_selenium_remote_session(selenium_url='http://selenium:4444/wd/hub')
#   friend_list.login()
#   friend_list.set_skip_users(skip_private=False)
#   friend_list.set_relationship_bounds(enabled=True, potency_ratio=0.4)
#   friend_list.set_do_like(True, percentage=80)
#   friend_list.interact_by_users(friends, amount=2, randomize=False)
#   friend_list.end()


#########################################
# Interact with high profiles by hashtag #
# - likes
# - comments
bot = InstaPy(username=creds['user'], password=creds['pass'],
              selenium_local_session=False, disable_image_load=True)
bot.set_selenium_remote_session(selenium_url='http://selenium:4444/wd/hub')

# Don't bother friends
bot.set_dont_include(friends)

# Don't get banned 
bot.set_quota_supervisor(enabled=True, sleep_after=["likes", "comments_d", "follows", "unfollows", "server_calls_h"],
                        sleepyhead=True, stochastic_flow=True, notify_me=True, peak_likes=(57, 585),
                        peak_comments=(21, 182), peak_follows=(48, None), peak_unfollows=(35, 402),
                        peak_server_calls=(None, 4700))

# Login
bot.login()

# Exceptions
bot.set_dont_like(exceptions)

# # Comment
# bot.set_comments(comments)
# bot.set_do_comment(enabled=True, percentage=50)

# if skip_hashtags_interaction:
#   print('⚡️ Skipping interaction based on hashtags')
# else:
#   print('🏗 Building hashtags network')
#   # Smart hashtags
#   bot.set_smart_hashtags(hashtags, limit=4, sort='top', log_tags=True)

#   # Setting bounds
#   bot.set_relationship_bounds(enabled=True, potency_ratio=1.5, delimit_by_numbers=True,
#                               max_followers=99999999, max_following=5000,
#                               min_followers=700, min_following=0, min_posts=10)

#   # Like
#   bot.like_by_tags(amount=20, use_smart_hashtags=True)


# ########################
# # Interact by location #
# # - likes
# if skip_friends_interaction:
#   print('⚡️ Skipping interaction based on locations')
# else:
#   print('🏗  Building locations network')
#   # Netherlands
#   bot.like_by_locations(netherlands, amount=2)


######################################
# Follow/Unfollow flow plus interact  #
# - likes
# - comments
if skip_follow_unfollow:
  print('⚡️ Skipping follow/unfollow')
else:
  print('🏔 ⛏ Mining followers')
  bot.set_relationship_bounds(enabled=True, potency_ratio=1, delimit_by_numbers=True,
                              min_followers=250, min_following=50, min_posts=30)

  ## Don't be an asshole config ##

  # Setting blacklist
  bot.set_blacklist(enabled=True, campaign='blacklist')

  # Dont bother nice people
  bot.set_dont_include(friends+brands+interests+artists)

  # Exclude private or accounts without profile picture
  bot.set_skip_users(skip_private=True, private_percentage=100,
                    skip_no_profile_pic=True, skip_business=False,)

  # UNFOLLOW
  # People that didn't followed back in the last 48hs
  bot.set_blacklist(enabled=False, campaign='blacklist')
  # bot.unfollow_users(amount=90, InstapyFollowed=(True, "nonfollowers"), style="FIFO", unfollow_after=12*60*60, sleep_delay=601)

  # CLEANUP
  bot.unfollow_users(amount=500, InstapyFollowed=(True, "all"), style="FIFO", sleep_delay=601) 

# Closing sessions
bot.end()
