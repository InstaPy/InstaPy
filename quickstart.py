# imports
from instapy import InstaPy
from instapy import smart_run


# login credentials
insta_username = 'p14test'
insta_password = 'azerty1234'

comments = ['Nice shot! @{}',
        'I love your profile! @{}',
        'Your feed is an inspiration :thumbsup:',
        'Just incredible :open_mouth:',
        'What camera did you use @{}?',
        'Love your posts @{}',
        'Looks awesome @{}',
        'Getting inspired by you @{}',
        ':raised_hands: Yes!',
        'I can feel your passion @{} :muscle:']

# get an InstaPy session!
# set headless_browser=True to run InstaPy in the background
session = InstaPy(username=insta_username,
                  password=insta_password,
                  headless_browser=False,
                  want_check_browser=False)

with smart_run(session):
  """ Activity flow """		
  # general settings		
  session.set_dont_include(["friend1", "friend2", "friend3"])		
  
  # activity
  tag_list = open("taglist.txt").read().split(',')
  print(tag_list)


# like, follow, follow then unfollow
session.like_by_tags(tag_list, amount=10)




# Joining Engagement Pods
session.set_do_comment(enabled=True, percentage=35)
session.set_comments(comments)
session.join_pods(topic='sports', engagement_mode='no_comments')