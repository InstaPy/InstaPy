"""Module which handles the follow features like unfollowing and following"""
import json
import csv
from .time_util import sleep
from random import randint
import locale
locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )

from .print_log_writer import log_followed_pool
from .print_log_writer import delete_line_from_file

def setAutomatedFollowedPool(username):
      automatedFollowedPool = []

      try:
          with open('./logs/' + username + '_followedPool.csv') as followedPoolFile:
             reader = csv.reader(followedPoolFile)
             automatedFollowedPool = [row[0] for row in reader]

          print("--> automatedFollowedPool length {}".format(len(automatedFollowedPool)))
          followedPoolFile.close()

      except BaseException as e:
          print("setAutomatedFollowedPool error \n", str(e))

      return automatedFollowedPool

def unfollow(browser, username, amount, dont_include, automatedFollowedPool):

  """unfollows the given amount of users"""
  unfollowNum = 0

  browser.get('https://www.instagram.com/' + username)

  #  check how many poeple we are following
  allfollowing = locale.atoi(browser.find_element_by_xpath("//li[3]/a/span").text)

  #  throw RuntimeWarning if we are 0 people following
  if (allfollowing == 0):
      raise RuntimeWarning('There are 0 people to unfollow')

  try:
      following_link = browser.find_elements_by_xpath('//header/div[2]//li[3]')
      following_link[0].click()
  except BaseException as e:
      print("following_link error \n", str(e))

  sleep(2)

  # find dialog box
  dialog = browser.find_element_by_xpath('/html/body/div[2]/div/div[2]/div/div[2]')

  #scroll down the page
  for i in range(int(allfollowing/2)):
    browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", dialog)
    sleep(randint(500,1000)/1000)

  #get persons and unfollow buttons
  person_list_div = browser.find_element_by_class_name('_4gt3b')
  person_list = dialog.find_elements_by_tag_name("a")
  person_list = [x.text for x in person_list]

  follow_div = browser.find_element_by_class_name('_4gt3b')
  follow_buttons = dialog.find_elements_by_tag_name('button')

  automatedFollowedPoolLength = len(automatedFollowedPool)

  try:

      for button, person in zip(follow_buttons, person_list):
        if  unfollowNum >= amount:
            print("--> Total unfollowNum reached it's amount given ", unfollowNum)
            break

        if  unfollowNum >= automatedFollowedPoolLength:
            print("--> Total unfollowNum exeeded the pool of automated followed ", unfollowNum)
            break

        if unfollowNum != 0 and unfollowNum%10 == 0:
            sleep(600)
            print('Sleeping for about 10min')

        if person not in dont_include and person in automatedFollowedPool:
          unfollowNum += 1
          button.click()
          delete_line_from_file('./logs/' + username + '_followedPool.csv', person + ",\n")

          print('--> Ongoing Unfollow ' + str(unfollowNum) +  ' now unfollowing: {}'.format(person.encode('utf-8')))
          sleep(15)

          continue

        else:
          continue

  except BaseException as e:
          print("unfollow loop error \n", str(e))

  return unfollowNum

def follow_user(self, user_name):
  """Follows the user of the currently opened image"""
  browser = self.browser
  follow_restrict = self.follow_restrict
  login = self.username

  follow_button = browser.find_element_by_xpath("//article/header/span/button")
  sleep(2)

  if follow_button.text == 'Follow':
    follow_button.click()
    print('--> Now following')
    log_followed_pool(login, user_name)
    follow_restrict[user_name] = follow_restrict.get(user_name, 0) + 1
    sleep(3)
    return 1

  else:
    print('--> Already following')
    sleep(1)
    return 0

def follow_given_user(browser, acc_to_follow, follow_restrict):
    """Follows a given user."""
    browser.get('https://www.instagram.com/' + acc_to_follow)
    print('--> {} instagram account is opened...'.format(acc_to_follow))
    follow_button = browser.find_element_by_xpath("//*[contains(text(), 'Follow')]")
    sleep(10)
    if follow_button.text == 'Follow':
        follow_button.click()
        print('---> Now following: {}'.format(acc_to_follow))
        print('*' * 20)
        follow_restrict[acc_to_follow] = follow_restrict.get(acc_to_follow, 0) + 1
        sleep(3)
        return 1
    else:
        print('---> {} is already followed'.format(acc_to_follow))
        print('*' * 20)
        sleep(3)
        return  0

def dump_follow_restriction(followRes):
  """Dumps the given dictionary to a file using the json format"""
  with open('./logs/followRestriction.json', 'w') as followResFile:
    json.dump(followRes, followResFile)

def load_follow_restriction():
  """Loads the saved """
  with open('./logs/followRestriction.json') as followResFile:
    return json.load(followResFile)
