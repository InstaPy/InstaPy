from instapy import InstaPy
from random import shuffle
import time
insta_username = 'none'
insta_password = 'none!'

session = InstaPy(username=insta_username, password=insta_password, selenium_local_session=False)
session.read_likes_statistics()
session.read_follows_statistics()
#session.end()
