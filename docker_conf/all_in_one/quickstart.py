from instapy import InstaPy

# Write your automation here
# Stuck ? Look at the github page or the examples in the examples folder

dont_like = ['food', 'girl', 'hot']
ignore_words = ['pizza']
friend_list = ['friend1', 'friend2', 'friend3']

# If you want to enter your Instagram Credentials directly just enter
# username=<your-username-here> and password=<your-password> into InstaPy
# e.g like so InstaPy(username="instagram", password="test1234")

InstaPy() \
    .login() \
    .set_relationship_bounds(enabled=True, \
                 potency_ratio=-1.21, \
                  delimit_by_numbers=True, \
                   max_followers=4590, \
                    max_following=5555, \
                     min_followers=45, \
                      min_following=77) \
    .set_do_comment(True, percentage=10) \
    .set_comments(['Cool!', 'Awesome!', 'Nice!']) \
    .set_dont_include(friend_list) \
    .set_dont_like(dont_like) \
    .set_ignore_if_contains(ignore_words) \
    .like_by_tags(['dog', '#cat'], amount=100) \
    .end()
