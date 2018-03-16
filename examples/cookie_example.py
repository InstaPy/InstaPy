"""Example Case of the Script"""
from instapy import InstaPy

# if you don't provide arguments, the script will look for INSTA_USER and INSTA_PW in the environment
session = InstaPy(username='test', password='test')

"""Load cookie or login"""
# logs you in with the a cookie (cookies.pkl must exist)
if not session.load_cookies():
    session.login()

""""Do something"""
# likes a given amount of posts on your feed, taking into account settings of commenting, like restrictions etc
session.like_by_feed(amount=100)
# can also randomly skips posts to be liked
session.like_by_feed(amount=100, randomize=True)
# if it comes across some posts I declared as inappropriate it will automatically unfollow its author user
session.like_by_feed(amount=100, randomize=True, unfollow=True)
# visits the author's profile page of a certain post and likes a given number of his pictures, then returns to feed
session.like_by_feed(amount=100, randomize=True, unfollow=True, interact=True)

"""Save cookie"""
# saves cookie to cookies.pkl
session.save_cookies()

"""Ending the script"""
# clears all the cookies, deleting you password and all information from this session
session.end()
