from instapy import InstaPy

insta_username = 'cycling_apparel'
insta_password = 'psek62'

# if you want to run this script on a server,
# simply add nogui=True to the InstaPy() constructor
session = InstaPy(username=insta_username, password=insta_password)
session.login()

# set up all the settings
session.set_dont_like(['pizza', 'girl'])

# do the actual liking
session.set_do_follow(enabled=True, percentage=100, times=2)

session.like_by_tags(['roadcycling'], amount=10)

# end the bot session
session.end()
