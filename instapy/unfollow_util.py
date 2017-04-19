"""Module which handles the follow features like unfollowing and following"""
import json

from .time_util import sleep


def unfollow(browser, username, amount, dont_include):
  """unfollows the given amount of users"""
  unfollowNum = 0

  browser.get('https://www.instagram.com/' + username)

  # Make sure the necessary element is loaded (try 10 times)
  following_link_div = browser.find_elements_by_class_name('_218yx')
  sleep(1)
  num_of_tries = 0

  while len(following_link_div) < 3 and num_of_tries < 10:
      following_link_div = browser.find_elements_by_class_name('_218yx')
      sleep(1)
      num_of_tries += 1

  # Failed to unfollow
  if len(following_link_div) < 3:
      return unfollowNum

  following_link = following_link_div[2].find_element_by_tag_name('a')
  following_link.click()
  
  sleep(2)

  person_list_div = browser.find_element_by_class_name('_4gt3b')
  person_list = person_list_div.find_elements_by_class_name('_cx1ua')
  follow_div = browser.find_element_by_class_name('_4gt3b')

  temp_list = []
  actions = ActionChains(browser)
  actions.move_to_element(follow_div)
  actions.click()
  actions.send_keys()
  actions.perform()

  # Load ALL followed users first (or until list is so long 1 second
  # is not enough to reach the end to load more)
  actions.send_keys(Keys.END).perform()
  sleep(1)
  actions.send_keys(Keys.HOME).perform()
  sleep(1)
  temp_list = person_list_div.find_elements_by_class_name('_cx1ua')

  while len(person_list) < len(temp_list):
    actions.send_keys(Keys.END).perform()
    sleep(1)
    person_list = temp_list
    temp_list = person_list_div.find_elements_by_class_name('_cx1ua')

  # Finally, extract the names of users from the list in reversed order (and buttons)
  follow_div = browser.find_element_by_class_name('_4gt3b')
  person_list = reversed([x.find_element_by_class_name('_gzjax').text for x in person_list])
  follow_buttons = reversed(follow_div.find_elements_by_tag_name('button'))

  for button, person in zip(follow_buttons, person_list):
    if person not in dont_include:
      unfollowNum += 1
      button.click()
      print('--> Now unfollowing: {}'.format(person.encode('utf-8')))
      sleep(15)

      # Stop if reached amount or if reached a maximum of 10
      if unfollowNum >= amount or unfollowNum == 10:
          break

  return unfollowNum

def follow_user(browser, user_name, follow_restrict):
  """Follows the user of the currently opened image"""
  follow_button = browser.find_element_by_xpath("//article/header/span/button")
  sleep(2)

  if follow_button.text == 'Follow':
    follow_button.click()
    print('--> Now following')

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
