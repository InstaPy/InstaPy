"""Module only used to log the number of followers to a file"""
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException

def log_follower_num(browser, username):
  """Prints and logs the current number of followers to
  a seperate file"""
  browser.get('https://www.instagram.com/' + username)

  followed_by = browser.execute_script("return window._sharedData.entry_data.ProfilePage[0].user.followed_by.count")

  with open('./logs/followerNum.txt', 'a') as numFile:
    numFile.write('{:%Y-%m-%d %H:%M} {}\n'.format(datetime.now(), followed_by or 0))


def log_followed_pool(login, followed):
  """Prints and logs the followed to
  a seperate file"""

  with open('./logs/' + login + '_followedPool.csv', 'a') as followPool:
    followPool.write(followed + ",\n")
    followPool.close()

def delete_line_from_file(filepath, lineToDelete):
    f = open(filepath,"r")
    lines = f.readlines()
    f.close()
    f = open(filepath,"w")

    for line in lines:

      if line!= lineToDelete:
        f.write(line)
    f.close()
