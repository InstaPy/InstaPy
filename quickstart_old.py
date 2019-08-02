from instapy import InstaPy

session = InstaPy(username='', password='',)

session.login()

#Interact with the people that a given user is following
#set_do_comment, set_do_follow and set_do_like are applicable
session.set_lower_follower_count(limit=70)
session.set_upper_follower_count(limit=900)
session.set_user_interact(amount=4, random=False, percentage=100, media='Photo')
session.set_do_follow(enabled=True, percentage=10)
session.set_do_like(enabled=True, percentage=100)
session.set_comments(['Epic', 'Radical', 'Dope',])
session.set_do_comment(enabled=True, percentage=25)
session.interact_user_followers(['', '', '', '', ''], amount=10, random=False,)


session.like_by_feed(amount=50, randomize=False, unfollow=False, interact=True)
session.set_user_interact(amount=3, random=False, percentage=25, media='Photo')

session.unfollow_users(amount=10, onlyInstapyFollowed = True, onlyInstapyMethod = 'FIFO' )
session.set_unfollow_active_users(enabled=False, posts=5)
session.end( )
