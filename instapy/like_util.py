"""Module that handles the like features"""
from math import ceil
from re import findall
from selenium.webdriver.common.keys import Keys

from .time_util import sleep


def get_links_for_tag(browser, tag, amount):
  """Fetches the number of links specified
  by amount and returns a list of links"""
  browser.get('https://www.instagram.com/explore/tags/'
              + (tag[1:] if tag[:1] == '#' else tag))

  sleep(2)

  # clicking load more till there are 1000 posts
  body_elem = browser.find_element_by_tag_name('body')

  sleep(2)

  load_button = body_elem.find_element_by_xpath \
    ('//a[contains(@class, "_8imhp _glz1g")]')
  body_elem.send_keys(Keys.END)
  sleep(2)

  load_button.click()

  body_elem.send_keys(Keys.HOME)
  sleep(1)

  main_elem = browser.find_element_by_tag_name('main')

  new_needed = int(ceil((amount - 33) / 12))

  for _ in range(new_needed):  # add images x * 12
    body_elem.send_keys(Keys.END)
    sleep(1)
    body_elem.send_keys(Keys.HOME)
    sleep(1)

  link_elems = main_elem.find_elements_by_tag_name('a')
  links = [link_elem.get_attribute('href') for link_elem in link_elems]

  return links[:amount]

def check_link(browser, link, dont_like, ignore_if_contains, username, like_by_followers_upper_limit, like_by_followers_lower_limit):

  browser.get(link)
  sleep(2)

  """Check if the Post is Valid/Exists"""
  post_page = browser.execute_script("return window._sharedData.entry_data.PostPage")
  if post_page is None:
    print('Unavailable Page: ' + link)
    return False, 'Unavailable Page'

  """Gets the description of the link and checks for the dont_like tags"""
  user_name = browser.execute_script("return window._sharedData.entry_data.PostPage[0].media.owner.username")
  image_text = browser.execute_script("return window._sharedData.entry_data.PostPage[0].media.caption")

  """If the image has no description gets the first comment"""
  if image_text is None:
    image_text = browser.execute_script("return window._sharedData.entry_data.PostPage[0].media.comments.nodes[0].text")
  if image_text is None:
    image_text = "No description"

  """Find the number of followes the user has"""
  userlink = 'https://www.instagram.com/' + user_name
  browser.get(userlink)
  sleep(1)
  num_followers = browser.execute_script("return window._sharedData.entry_data.ProfilePage[0].user.followed_by.count")
  browser.get(link)
  sleep(1)


  print('Image from: ' + user_name)
  print('Link: ' + link)
  print('Description: ' + image_text)
  print "Number of Followers: ", num_followers

  if like_by_followers_upper_limit and num_followers > like_by_followers_upper_limit:
    return True, user_name, 'Number of followers exceeds limit'
  if like_by_followers_lower_limit and num_followers < like_by_followers_lower_limit:
    return True, user_name, 'Number of followers does not reach limit'

  if any((word in image_text for word in ignore_if_contains)):
      return False, user_name, 'None'

  if any(((tag in image_text or user_name == username) for tag in dont_like)):
      return True, user_name, 'Inappropriate'

  return False, user_name, 'None'

def like_image(browser):
  """Likes the browser opened image"""
  like_elem = browser.find_elements_by_xpath("//a[@role = 'button']/span[text()='Like']")
  liked_elem = browser.find_elements_by_xpath("//a[@role = 'button']/span[text()='Unlike']")

  if len(like_elem) == 1:
    browser.execute_script("document.getElementsByClassName('" + like_elem[0].get_attribute("class") + "')[0].click()")
    print('--> Image Liked!')
    sleep(2)
    return True
  elif len(liked_elem) == 1:
    print('--> Already Liked!')
    return False
  else:
    print('--> Invalid Like Element!')
    return False

def get_tags(browser, url):
  """Gets all the tags of the given description in the url"""
  browser.get(url)
  sleep(1)

  image_text = browser.execute_script("return window._sharedData.entry_data.PostPage[0].media.caption")

  tags = findall(r'#\w*', image_text)
  return tags
