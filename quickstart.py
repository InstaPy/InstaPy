from instapy import InstaPy

# Write your automation here
# Stuck?
#   Look at the github page
#   or the examples in the examples folder

ignore_users = ['enemy1', 'enemy2']
friend_list = ['friend1', 'friend2', 'friend3']
dont_like = ['food', 'girl', 'hot']
like_anyway = ['pizza']

# If you want to enter your Instagram Credentials directly just enter
# username=<your-username-here> and password=<your-password> into InstaPy
# e.g
# InstaPy(username="instagram", password="test1234") \
InstaPy() \
    .login() \
    .set_ignore_users(ignore_users) \
    .set_follower_limit(0, 1500) \
    .set_follow_rate() \
    .set_comment_rate() \
    .set_comments() \
    .set_dont_comment_users(friend_list) \
    .set_dont_like(dont_like) \
    .set_like_anyway(like_anyway) \
    .set_like_tags(["#landscape"]) \
    .set_like_media("Photo") \
    .like_images(amount=50) \
    .end()
