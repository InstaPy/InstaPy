from instapy import InstaPy
from random import shuffle
from instapy.unfollow_util import dump_follow_restriction
import pickle
import sys
import json

unfollowlist = []

def load_follow_restriction():
    """Loads the saved """
    with open('./logs/following/taircohenn.json') as followResFile:
        return json.load(followResFile)

with open('./logs/following/'+'taircohenn', 'rb') as input:
    original_all_following = pickle.load(input)
with open('./logs/following/'+'taircohennCurr', 'rb') as input:
    curr_all_following = pickle.load(input)

jsonunf = load_follow_restriction()
jsonunfkeys_set = set(jsonunf.keys()) # all following since beginning of automation
curr_all_following_set = set(curr_all_following) # currently capture of following
original_all_following_set = set(original_all_following) # original captured following of user

non_original_following = curr_all_following_set - original_all_following_set # remove all original from current
if len(jsonunfkeys_set & original_all_following_set) == 0: # validate no original found in all
    common = jsonunfkeys_set & non_original_following
    common_list = list(common)
    print(len(common))
    with open('./logs/following/taircohennRm', 'wb') as output:
        pickle.dump(common_list, output, pickle.HIGHEST_PROTOCOL)

    with open('./logs/following/' + 'taircohenn' + '_followedPool.csv', 'a+') as followPool:
        for user in common_list:
                followPool.write(user + ",\n")



quit()

with open('./logs/user.txt', 'r') as file:
    insta_username = file.readline()
    print(insta_username)
with open('./logs/password.txt', 'r') as file:
    insta_password = file.readline()
with open('./logs/following/'+insta_username, 'rb') as input:
    original_all_following = pickle.load(input)
print ("original_all_following users to ignore", len(original_all_following))
print("1")

session = InstaPy(username=insta_username, password=insta_password)
session.login()
session.set_blacklist(enabled=True, campaign='General')
session.set_dont_include(original_all_following)

session.unfollow_users(amount=40, onlyInstapyFollowed=True, from_file='logs/following/taircohennRm', onlyInstapyMethod='FIFO', sleep_delay=600)
session.end()