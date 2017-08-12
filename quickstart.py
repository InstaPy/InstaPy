from instapy import InstaPy

insta_username = ''
insta_password = ''

# if you want to run this script on a server, 
# simply add nogui=True to the InstaPy() constructor

InstaPy(username=insta_username, password=insta_password)\
  .login()\
  .set_upper_follower_count(limit=2500)\
  .set_do_comment(True, percentage=10)\
  .set_comments(['aMEIzing!', 'So much fun!!', 'Nicey!'])\
  .set_dont_include(['friend1', 'friend2', 'friend3'])\
  .set_dont_like(['pizza', 'girl'])\
  .like_by_tags(['natgeo', 'world'], amount=100)\
  .end()
