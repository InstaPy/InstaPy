
from instapy import InstaPy
from instapy.monkey_patcher import patch_all

#
# use_firefox=True : Switches the browser from Chrome to Firefox/Geckodriver
#                    which might be better on ARM based systems
#                    The default value is False
#
# page_delay=25 : Tells the WebDriver to poll the DOM for a certain amount of time
#                 when trying to find any element (or elements) not immediately available.
#                 The default setting is 25.
#
# set_switch_language(False) : Firefox on english operating systems already defaults to english.
#                              Set to True if the language seen in the login page is anything but English.
#                              The default value is True
#

# Patch ActionChain to reslove MoveTargetOutOfBoundsException issue ref: #803
patch_all()


InstaPy(username='test', password='test', use_firefox=True, page_delay=25)\
    .set_switch_language(False)\
    .login()\
    .set_do_comment(True, percentage=10) \
    .set_comments(['Cool!', 'Awesome!', 'Nice!']) \
    .set_dont_include(['friend1', 'friend2', 'friend3']) \
    .set_dont_like(['food', 'girl', 'hot']) \
    .like_by_tags(['dog', '#cat'], amount=2) \
    .end()
