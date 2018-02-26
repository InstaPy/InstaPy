from instapy import InstaPy

insta_username = ''
insta_password = ''

# set headless_browser=True if you want to run InstaPy on a server
try:
    # set these if you're locating the library in the /usr/lib/pythonX.X/ directory
    # Settings.database_location = '/path/to/instapy.db'
    # Settings.browser_location = '/path/to/chromedriver'
    
    session = InstaPy(username=insta_username,
                      password=insta_password,
                      headless_browser=False,
                      multi_logs=True)
    session.login()

    # settings
    # session.set_upper_follower_count(limit=2500)
    # session.set_do_comment(True, percentage=10)
    # session.set_comments(['aMEIzing!', 'So much fun!!', 'Nicey!'])
    # session.set_dont_include(['friend1', 'friend2', 'friend3'])
    # session.set_dont_like(['pizza', 'girl'])

    # actions
    # session.like_by_tags(['natgeo'], amount=1)
    # session.follow_user_followers(['yyoga'], amount=10, randomize=False, sleep_delay=60)
    session.set_user_interact(amount=5, randomize=True, percentage=100, media='Photo')
    session.follow_user_followers(['yyoga'], amount=100, randomize=True, sleep_delay=60, interact=True)


finally:
    # end the bot session
    session.end()
