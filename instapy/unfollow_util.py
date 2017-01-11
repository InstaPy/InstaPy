"""Module which handles the follow features like unfollowing and following"""
from time import sleep

def unfollow(browser, username, amount):
  """unfollows the given amount of users"""
  browser.get('https://www.instagram.com/' + username)

  following_link_div = browser.find_elements_by_class_name('_218yx')[2]
  following_link = following_link_div.find_element_by_tag_name('a')
  following_link.click()

  sleep(2)

  person_list_div = browser.find_element_by_class_name('_6jvgy')
  person_list = person_list_div.find_elements_by_xpath\
    ('//a[@class = "_4zhc5 notranslate _j7lfh"]')
  person_list = [x.text for x in person_list]

  follow_div = browser.find_element_by_class_name('_4gt3b')
  follow_buttons = follow_div.find_elements_by_tag_name('button')

  for button, person in zip(follow_buttons[:amount], person_list[:amount]):
    button.click()
    print('--> Now unfollowing: ' + person)
    sleep(15)

def follow_user(browser):
  """Follows the user of the currently opened image"""
  follow_button = browser.find_elements_by_tag_name('button')[0]
  sleep(2)

  if follow_button.text == 'Follow':
    follow_button.click()
    print('--> Now following')
    sleep(3)
    return 1

  else:
    print('--> Already following')
    sleep(1)
    return 0
