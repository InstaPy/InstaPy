"""Module only used to log the number of followers to a file"""
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException

def log_follower_num(browser, username):
  """Prints and logs the current number of followers to
  a seperate file"""
  browser.get('https://www.instagram.com/' + username)
  follower_num = 0

  try:
    follower_num = browser.find_element_by_xpath\
      ('//a[@href="/' + username.lower()  + '/followers/"]').text
  except NoSuchElementException:
    follower_num = 0

  with open('./logs/followerNum.txt', 'a') as numFile:
    numFile.write(datetime.now().strftime('%Y-%m-%d %H:%M '))
    numFile.write(str(follower_num) + '\n')
