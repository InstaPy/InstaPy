"""Module only used to log the number of followers to a file"""
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException

def log_follower_num(browser, username):
  """Prints and logs the current number of followers to
  a seperate file"""
  browser.get('https://www.instagram.com/' + username)

  follower_num = 0

  followed_by = browser.execute_script("return window._sharedData.entry_data.ProfilePage[0].user.followed_by.count")
  if followed_by is not None:
    follower_num = followed_by

  with open('./logs/followerNum.txt', 'a') as numFile:
    numFile.write(datetime.now().strftime('%Y-%m-%d %H:%M '))
    numFile.write(str(follower_num) + '\n')
