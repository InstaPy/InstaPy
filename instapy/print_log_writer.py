"""Module only used to log the number of followers to a file"""
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException

def log_follower_num(browser, username):
  """Prints and logs the current number of followers to
  a seperate file"""
  browser.get('https://www.instagram.com/' + username)

  followed_by = browser.execute_script("return window._sharedData.entry_data.ProfilePage[0].user.followed_by.count")
  with open('./logs/followerNum.txt', 'a') as numFile:
    numFile.write('{:%Y-%m-%d %H:%M} {}'.format(datetime.now(), followed_by or 0))
