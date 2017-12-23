from instapy import InstaPy

with open('./logs/user.txt', 'r') as file:
    insta_username = file.readline()
    print(insta_username)
with open('./logs/password.txt', 'r') as file:
    insta_password = file.readline()

session = InstaPy(username=insta_username, password=insta_password, proxy_address='149.202.180.55', proxy_port=3128)
print("1")

# set up all the settings
session.login()
#session.get_follow_list_from_user(following=True, followers=False)
#session.get_follow_list_from_user(following=False, followers=True)

userFollowinglist = ["taircohenn"]
for user in userFollowinglist:
    session.get_follow_list_from_user(following=True, followers=False, username=user)

# end the bot session
session.end()
