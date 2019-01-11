import json

### INSTRUCTIONS ###
'''
Change all settings and actions
Use https://www.instagram.com/explore/locations/ for location-IDs
'''

### GENERAL SETTINGS ###
insta_username = 'name'
insta_password = 'password'

# Devices for push notifications: pushover.net
devices = 'oneplus3t'

global_tags = ['']

mail_recp = 'mail'

### SETTINGS ###
# friends = json.load(open(insta_username + '_followings.json'))

set_comments = {
    'comments': ['Awesome!', 'Very lovely', 'Love it!', 'Nicey!',
                 'Great picture :)', 'Dope picture']
}

set_do_comment = {
    'enabled': True,
    'percentage': 10
}

set_do_follow = {
    'enabled': True,
    'percentage': 25,
    'times': 2
}

set_do_like = {
    'enabled': True,
    'percentage': 25
}

set_user_interact = {
    'amount': 2,
    'percentage': 50,
    'randomize': True,
    'media': 'Photo'  # or 'Video'
}

set_dont_unfollow_active_users = {
    'enabled': False,
    'posts': 5
}

set_relationship_bounds = {
    'enabled': True,
    'potency_ratio': None,
    'delimit_by_numbers': True,
    'min_followers': 150,
    'max_followers': 12000,
    'min_following': None,
    'max_following': 900
}

set_delimit_liking = {
    'enabled': False,
    'min': None,
    'max': None
}

set_delimit_commenting = {
    'enabled': False,
    'min': None,
    'max': None
}

set_dont_like = {
    'dontlikelist': ['follow', 'like']
}

set_ignore_users = {
    'ignoreuserslist': ['']
}

set_ignore_if_contains = {
    'ignoreifcontainslist': ['']
}

set_dont_include = {
    'source': 'file',
    'dontincludefilename': 'followings.json',
    'dontincludelist': ['']
}

set_simulation = {
    'enabled': True,
    'percentage': 10
}

### ACTIONS ###
follow_by_list = {
    'enabled': False,
    'followlist': [''],
    'times': 1,
    'randomize': True,
    'sleep_delay': 600,
    'interact': False
}

follow_user_followers = {
    'enabled': False,
    'followlist': [''],
    'amount': 3,
    'randomize': True,
    'sleep_delay': 600,
    'interact': False
}

follow_user_following = {
    'enabled': False,
    'followlist': [''],
    'amount': 1,
    'randomize': True,
    'sleep_delay': 600,
    'interact': False
}

follow_by_tags = {
    'enabled': True,
    'tags': ['marketing'],
    'amount': 5,
    'randomize': False,
    'skip_top_posts': True,
    'media': 'Photo'
}

follow_likers = {
    'enabled': False,
    'followlist': [''],
    'photos_grab_amount': 2,
    'follow_likers_per_photo': 3,
    'randomize': True,
    'sleep_delay': 600,
    'interact': 600
}

follow_commenters = {
    'enabled': False,
    'followlist': [''],
    'amount': 10,
    'daysold': 30,
    'max_pic': 100,
    'randomize': True,
    'sleep_delay': 600,
    'interact': False
}

interact_by_users = {
    'enabled': False,
    'interactlist': [''],
    'amount': 2,
    'randomize': True,
    'media': 'Photo'
}

interact_user_following = {
    'enabled': False,
    'interactlist': [''],
    'amount': 2,
    'randomize': True,
}

interact_user_followers = {
    'enabled': False,
    'interactlist': [''],
    'amount': 2,
    'randomize': True,
}

interact_by_URL = {
    'enabled': False,
    'urls': [''],
    'randomize': True,
    'interact': False
}

comment_by_locations = {
    'enabled': False,
    'locations': [''],
    'amount': 20,
    'skip_top_posts': True,
    'media': 'Photo'
}

like_by_tags = {
    'enabled': True,
    'tags': ['marketing'],
    'amount': 5,
    'randomize': True,
    'interact': False
}

like_by_feed = {
    'enabled': False,
    'amount': 20,
    'unfollow': True,
    'sleep_delay': 600,
    'interact': False
}

like_by_locations = {
    'enabled': False,
    'locations': [''],
    'amount': 20,
    'skip_top_posts': True
}

unfollow_users = {
    'enabled': False,
    'method': 'all',  # or instapyfollowed or customlist
    'amount': 5,
    'sleep_delay': 600,
    'style': 'FIFO',  # or 'LIFO' or 'RANDOM'
    'unfollow_after': 60 * 60 * 12,

    # 'customList': ["user_1", "user_2", "user_49", "user332", "user50921",
    # "user_n"],
    # 'setting': 'all', # or 'nonfollowers

    'InstaPyFollowed': 'all'  # or 'nonfollowers

    # 'nonFollowers': True,

    # 'allFollowing': True
}
