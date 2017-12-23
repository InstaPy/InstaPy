from instapy import InstaPy

insta_username = ""
insta_password = ""

session = InstaPy(username=insta_username, password=insta_password)

# set up all the settings
session.login()

userFollowinglist = ["oprah"]
for user in userFollowinglist:
    session.get_follow_list_from_user(following=True, followers=False, username=user)

# end the bot session
session.end()
