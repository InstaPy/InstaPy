"""OS Modules environ method to get the setup vars from the Environment"""
from os import environ
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from modules.comment_util import comment_image
from modules.like_util import check_link
from modules.like_util import get_links_for_tag
from modules.like_util import get_tags
from modules.like_util import like_image
from modules.login_util import login_user
from modules.unfollow_util import unfollow
from modules.unfollow_util import follow_user

class InstaPy:
  """Class to be instantiated to use the script"""
  def __init__(self, username=None, password=None):
    self.browser = webdriver.Chrome('./assets/chromedriver')
    if username is None:
      self.username = environ.get('INSTA_USER')
    else:
      self.username = username

    if password is None:
      self.password = environ.get('INSTA_PW')
    else:
      self.password = password

    self.do_comment = False
    self.comment_percentage = 0
    self.comments = ['Cool!', 'Nice!', 'Looks good!']

    self.do_follow = False
    self.follow_percentage = 0
    self.dont_include = []

    self.dont_like = ['sex', 'nsfw']

  def login(self):
    """Used to login the user either with the username and password"""
    try:
      login_user(self.browser, self.username, self.password)
      print('Logged in successfully')
      sleep(3)
    except NotImplementedError as err:
      print(str(err))

  def set_do_comment(self, enabled=False, percentage=0):
    """Defines if images should be commented or not
    percentage=25 -> ~ every 4th picture will be commented"""
    self.do_comment = enabled
    self.comment_percentage = percentage

  def set_comments(self, comments=None):
    """Changes the possible comments"""
    if comments is None:
      comments = []
    self.comments = comments

  def set_do_follow(self, enabled=False, percentage=0):
    """Defines if the user of the liked image should be followed"""
    self.do_follow = enabled
    self.follow_percentage = percentage

  def set_dont_like(self, tags=None):
    """Changes the possible restriction tags, if one of this
     words is in the description, the image won't be liked"""
    if tags is None:
      tags = []
    self.dont_like = tags

  def set_dont_include(self, friends=None):
    """Defines which accounts should not be unfollowed"""
    if friends is None:
      friends = []
    self.dont_include = friends

  def like_by_tags(self, tags=None, amount=50):
    """Likes (default) 50 images per given tag"""
    liked_img = 0
    already_liked = 0
    inap_img = 0
    commented = 0
    followed = 0

    if tags is None:
      tags = []

    for tag in tags:
      print('--> ' + tag)
      links = get_links_for_tag(self.browser, tag, amount)

      for link in links:
        try:
          inappropriate, user_name = \
            check_link(self.browser, link, self.dont_like, self.username)

          if not inappropriate:
            liked = like_image(self.browser)

            if liked:
              liked_img += 1
              if self.do_comment and user_name not in self.dont_include:
                commented += comment_image(self.browser, self.comments,
                                           self.comment_percentage)

              if self.do_follow and user_name not in self.dont_include:
                followed += follow_user(self.browser, self.follow_percentage)
            else:
              already_liked += 1
          else:
            inap_img += 1
        except NoSuchElementException as err:
          print('Invalid Page: ' + str(err))
        print('')

    print('Liked: ' + str(liked_img))
    print('Already Liked: ' + str(already_liked))
    print('Inappropriate: ' + str(inap_img))
    print('Commented: ' + str(commented))
    print('Followed: ' + str(followed))

  def like_from_image(self, url, amount=50):
    """Gets the tags from an image and likes 50 images for each tag"""
    try:
      tags = get_tags(self.browser, url)
      print(tags)
      self.like_by_tags(tags, amount)
    except TypeError as err:
      print('Sorry, an error occured: ' + str(err))
      self.end()

  def unfollow_users(self, amount=10):
    """Unfollows (default) 10 users from your following list"""
    while amount > 0:
      try:
        unfollow(self.browser, self.username, amount)
      except TypeError as err:
        print('Sorry, an error occured: ' + str(err))
        self.end()

      if amount > 10:
        sleep(600)
        print('Sleeping for 10min')

      amount -= 10

  def end(self):
    """Closes the current session"""
    self.browser.delete_all_cookies()
    self.browser.close()
    print('')
    print('Session ended')
    print('-------------')
