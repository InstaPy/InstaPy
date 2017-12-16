from instapy import InstaPy

insta_username = ""
insta_password = ""

session = InstaPy(username=insta_username, password=insta_password)

# set up all the settings
session.login()

userFollowlist = ["oprah"]
for user in userFollowlist:
    session.get_follow_list_from_user(following=False, followers=True, username=user)

# end the bot session
session.end()
