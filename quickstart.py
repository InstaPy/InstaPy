from instapy import InstaPy

insta_username = ''
insta_password = ''

InstaPy(username=insta_username, password=insta_password, use_firefox=False, page_delay=25)\
  .login()\
  .set_upper_follower_count(limit=2500)\
  .set_do_comment(True, percentage=10)\
  .set_comments(['aMEIzing!', 'So much fun!!', 'Nicey!'])\
  .set_dont_include(['friend1', 'friend2', 'friend3'])\
  .set_dont_like(['pizza', 'girl'])\
  .set_ignore_if_contains(['cow'])\
  .like_by_tags(['kanisha', 'chickenbutt'], amount=100)\
  .end()
