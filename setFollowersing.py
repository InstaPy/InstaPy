from instapy import InstaPy
from random import shuffle
import time

with open('./logs/user.txt', 'r') as file:
    insta_username = file.readline()
    print(insta_username)
with open('./logs/password.txt', 'r') as file:
    insta_password = file.readline()

session = InstaPy(username=insta_username, password=insta_password)
print("1")

# set up all the settings
session.login()
session.getFollowerList_user(following=True, followers=False)
session.getFollowerList_user(following=False, followers=True)

# end the bot session
session.end()
