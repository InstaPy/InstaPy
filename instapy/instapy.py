"""OS Modules environ method to get the setup vars from the Environment"""
from datetime import datetime
from os import environ
from random import randint
from time import sleep
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

from .clarifai_util import check_image
from .comment_util import comment_image
from .like_util import check_link
from .like_util import get_links_for_tag
from .like_util import get_tags
from .like_util import like_image
from .login_util import login_user
from .unfollow_util import unfollow
from .unfollow_util import follow_user
from .unfollow_util import load_follow_restriction
from .unfollow_util import dump_follow_restriction
from .print_log_writer import log_follower_num

class InstaPy:
  """Class to be instantiated to use the script"""
  def __init__(self, username=None, password=None):
    #self.display = Display(visible=0, size=(800, 600))
    #self.display.start()
    chrome_options = Options()
    chrome_options.add_argument('--dns-prefetch-disable')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--lang=en-US')
    chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en-US'})
    self.browser = webdriver.Chrome('./assets/chromedriver', chrome_options=chrome_options)
    self.browser.implicitly_wait(25)

    self.logFile = open('./logs/logFile.txt', 'a')
    self.logFile.write('Session started - %s\n' \
                       % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    self.username = username or environ.get('INSTA_USER')
    self.password = password or environ.get('INSTA_PW')


    self.do_comment = False
    self.comment_percentage = 0
    self.comments = ['Cool!', 'Nice!', 'Looks good!']
    self.photo_comments = []
    self.video_comments = []

    self.followed = 0
    self.follow_restrict = load_follow_restriction()
    self.follow_times = 1
    self.do_follow = False
    self.follow_percentage = 0
    self.dont_include = []

    self.dont_like = ['sex', 'nsfw']
    self.ignore_if_contains = []

    self.use_clarifai = False
    self.clarifai_secret = None
    self.clarifai_id = None
    self.clarifai_img_tags = []

    self.aborting = False

  def login(self):
    """Used to login the user either with the username and password"""
    if not login_user(self.browser, self.username, self.password):
      print('Wrong login data!')
      self.logFile.write('Wrong login data!\n')

      self.aborting = True
    else:
      print('Logged in successfully!')
      self.logFile.write('Logged in successfully!\n')

    log_follower_num(self.browser, self.username)

    return self

  def set_do_comment(self, enabled=False, percentage=0):
    """Defines if images should be commented or not
    percentage=25 -> ~ every 4th picture will be commented"""
    if self.aborting:
      return self

    self.do_comment = enabled
    self.comment_percentage = percentage

    return self

  def set_comments(self, comments=None, media=None):
    """Changes the possible comments"""
    if self.aborting:
      return self

    if (media not in [None, 'Photo', 'Video']):
      print('Unkown media type! Treating as "any".')
      media = None

    self.comments = comments or []

    if media is None:
      self.comments = comments
    else:
      attr = '{}_comments'.format(media.lower())
      setattr(self, attr, comments)

    return self

  def set_do_follow(self, enabled=False, percentage=0, times=1):
    """Defines if the user of the liked image should be followed"""
    if self.aborting:
      return self

    self.follow_times = times
    self.do_follow = enabled
    self.follow_percentage = percentage

    return self

  def set_dont_like(self, tags=None):
    """Changes the possible restriction tags, if one of this
     words is in the description, the image won't be liked"""
    if self.aborting:
      return self

    self.dont_like = tags or []

    return self

  def set_ignore_if_contains(self, words=None):
    """ignores the don't likes if the description contains
    one of the given words"""
    if self.aborting:
      return self

    self.ignore_if_contains = words or []

    return self

  def set_dont_include(self, friends=None):
    """Defines which accounts should not be unfollowed"""
    if self.aborting:
      return self

    self.dont_include = friends or []

    return self

  def set_use_clarifai(self, enabled=False, secret=None, proj_id=None):
    """Defines if the clarifai img api should be used
    Which 'project' will be used (only 5000 calls per month)"""
    if self.aborting:
      return self

    self.use_clarifai = enabled

    if secret is None and self.clarifai_secret is None:
      self.clarifai_secret = environ.get('CLARIFAI_SECRET')
    elif secret:
      self.clarifai_secret = secret

    if proj_id is None and self.clarifai_id is None:
      self.clarifai_id = environ.get('CLARIFAI_ID')
    elif proj_id is not None:
      self.clarifai_id = proj_id

    return self

  def clarifai_check_img_for(self, tags=None, comment=False, comments=None):
    """Defines the tags, the images should be checked for"""
    if self.aborting:
      return self

    if tags is None and not self.clarifai_img_tags:
      self.use_clarifai = False
    elif tags:
      self.clarifai_img_tags.append((tags, comment, comments))

    return self

  def like_by_tags(self, tags=None, amount=50, media=None):
    """Likes (default) 50 images per given tag"""
    if self.aborting:
      return self

    liked_img = 0
    already_liked = 0
    inap_img = 0
    commented = 0
    followed = 0

    tags = tags or []

    for index, tag in enumerate(tags):
      print('Tag [%d/%d]' % (index + 1, len(tags)))
      print('--> ' + tag)
      self.logFile.write('Tag [%d/%d]' % (index + 1, len(tags)))
      self.logFile.write('--> ' + tag + '\n')

      try:
        links = get_links_for_tag(self.browser, tag, amount, media)
      except NoSuchElementException:
        print('Too few images, aborting')
        self.logFile.write('Too few images, aborting\n')

        self.aborting = True
        return self

      for i, link in enumerate(links):
        print('[%d/%d]' % (i + 1, len(links)))
        self.logFile.write('[%d/%d]' % (i + 1, len(links)))
        self.logFile.write(link)

        try:
          inappropriate, user_name, is_video = \
            check_link(self.browser, link, self.dont_like,
                       self.ignore_if_contains, self.username)

          if not inappropriate:
            liked = like_image(self.browser)

            if liked:
              liked_img += 1
              checked_img = True
              temp_comments = []
              commenting = randint(0, 100) <= self.comment_percentage
              following = randint(0, 100) <= self.follow_percentage

              if self.use_clarifai and (following or commenting):
                try:
                  checked_img, temp_comments =\
                    check_image(self.browser, self.clarifai_id,
                                self.clarifai_secret,
                                self.clarifai_img_tags)
                except Exception as err:
                  print('Image check error: ' + str(err))
                  self.logFile.write('Image check error: ' + str(err) + '\n')

              if self.do_comment and user_name not in self.dont_include \
                  and checked_img and commenting:
                if temp_comments:
                  # Use clarifai related comments only!
                  comments = temp_comments
                elif is_video:
                  comments = self.comments + self.video_comments
                else:
                  comments = self.comments + self.photo_comments
                commented += comment_image(self.browser, comments)
              else:
                print('--> Not commented')
                sleep(1)

              if self.do_follow and user_name not in self.dont_include \
                  and checked_img and following \
                  and self.follow_restrict.get(user_name, 0) < self.follow_times:
                followed += follow_user(self.browser, user_name, self.follow_restrict)
              else:
                print('--> Not following')
                sleep(1)
            else:
              already_liked += 1
          else:
            print('Image not liked: Inappropriate')
            inap_img += 1
        except NoSuchElementException as err:
          print('Invalid Page: ' + str(err))
          self.logFile.write('Invalid Page: ' + str(err))

        print('')
        self.logFile.write('\n')

    print('Liked: ' + str(liked_img))
    print('Already Liked: ' + str(already_liked))
    print('Inappropriate: ' + str(inap_img))
    print('Commented: ' + str(commented))
    print('Followed: ' + str(followed))

    self.logFile.write('Liked: ' + str(liked_img) + '\n')
    self.logFile.write('Already Liked: ' + str(already_liked) + '\n')
    self.logFile.write('Inappropriate: ' + str(inap_img) + '\n')
    self.logFile.write('Commented: ' + str(commented) + '\n')
    self.logFile.write('Followed: ' + str(followed) + '\n')

    self.followed += followed

    return self

  def like_from_image(self, url, amount=50, media=None):
    """Gets the tags from an image and likes 50 images for each tag"""
    if self.aborting:
      return self

    try:
      tags = get_tags(self.browser, url)
      print(tags)
      self.like_by_tags(tags, amount, media)
    except TypeError as err:
      print('Sorry, an error occured: ' + str(err))
      self.logFile.write('Sorry, an error occured: ' + str(err) + '\n')

      self.aborting = True
      return self

    return self

  def unfollow_users(self, amount=10):
    """Unfollows (default) 10 users from your following list"""
    while amount > 0:
      try:
        amount -= unfollow(self.browser, self.username, amount, self.dont_include)
      except TypeError as err:
        print('Sorry, an error occured: ' + str(err))
        self.logFile.write('Sorry, an error occured: ' + str(err) + '\n')

        self.aborting = True
        return self

      if amount > 10:
        sleep(600)
        print('Sleeping for 10min')

    return self

  def end(self):
    """Closes the current session"""
    dump_follow_restriction(self.follow_restrict)
    self.browser.delete_all_cookies()
    self.browser.close()
    #self.display.stop()

    print('')
    print('Session ended')
    print('-------------')

    self.logFile.write('\nSession ended - %s\n' \
                       % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    self.logFile.write('-' * 20 + '\n\n')
    self.logFile.close()

    with open('./logs/followed.txt', 'w') as followFile:
      followFile.write(str(self.followed))
