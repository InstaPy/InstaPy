"""Example Case of the Script"""
from instapy import InstaPy

try:
    # if you don't provide arguments, the script will look for INSTA_USER and INSTA_PW in the environment
    session = InstaPy(username='test', password='test',multi_logs=True)

    """Logging in"""
    # logs you in with the specified username and password
    session.login()

    """Comment util"""

    session.set_do_comment(enabled=True, percentage=25)
    session.set_comments(['Awesome', 'Really Cool', 'I like your stuff'])

    """Follow util"""
    # default enabled=False, follows ~ every 10th user from the images
    session.set_do_follow(enabled=True, percentage=10)

    session.set_use_clarifai(enabled=False)

    """Like util"""
    # searches the description and owner comments for the given words
    # and won't like the image if one of the words are in there
    session.set_dont_like(['food', 'eat', 'meal'])
    # will ignore the don't like if the description contains
    # one of the given words
    session.set_ignore_if_contains(['glutenfree', 'french', 'tasty'])

    """Different tasks"""
    # you can put in as much tags as you want, likes 100 of each tag
    session.like_by_tags(['#test'], amount=100)
    # you can also set to like a specific media (Photo / Video)
    session.like_by_tags(['#test'], amount=10, media='Photo')

    """"Like by feed"""
    # likes a given amount of posts on your feed, taking into account settings of commenting, like restrictions etc
    session.like_by_feed(amount=100)




    session.unfollow_users(
        amount=10)  # unfollows 10 of the accounts your following -> instagram will only unfollow 10 before you'll be 'blocked
    #  for 10 minutes' (if you enter a higher number than 10 it will unfollow 10, then wait 10 minutes and will continue then)


finally:
    """Ending the script"""
    # clears all the cookies, deleting you password and all information from this session
    session.end()
