#!/usr/bin/env python3.5
import json
from re import findall
from sys import argv
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

username = argv[1]

def getUserInfo(browser, username):
  container = browser.find_element_by_class_name('_de9bg')
  img_container = browser.find_element_by_class_name('_o0ohn')

  infos = container.find_elements_by_class_name('_218yx')

  prof_img = img_container.find_element_by_tag_name('img').get_attribute('src')
  num_of_posts = int(infos[0].text.split(' ')[0].replace(',', ''))
  followers = int(infos[1].text.split(' ')[0].replace(',', ''))
  following = int(infos[2].text.split(' ')[0].replace(',', ''))

  return prof_img, num_of_posts, followers, following

def extractPostInfo(browser):
  post = browser.find_element_by_class_name('_tjnr4')

  imgs = post.find_elements_by_tag_name('img')
  img = imgs[1].get_attribute('src')

  likes = post.find_element_by_tag_name('section')\
          .find_element_by_tag_name('div').text

  likes = likes.split(' ')

  #count the names if there is no number displayed
  if len(likes) > 2:
    likes = len([word for word in likes if word not in ['and', 'like', 'this']])
  else:
    likes = likes[0]
    likes = likes.replace(',', '')

  # if more than 22 comment elements, use the second to see
  # how much comments, else count the li's

  # first element is the text, second either the first comment
  # or the button to display all the comments
  comment_list = post.find_element_by_tag_name('ul')
  comments = comment_list.find_elements_by_tag_name('li')

  if len(comments) > 1:
    tags = comments[0].text + ' ' + comments[1].text
  else:
    tags = comments[0].text

  tags = findall(r'#[A-Za-z0-9]*', tags)

  if len(comments) < 22:
    comments = len(comments) - 1
  else:
    comments = comments[1].find_element_by_tag_name('span').text
    comments = comments.replace(',', '')

  return img, tags, int(likes), int(comments)

browser = webdriver.Chrome('./assets/chromedriver')
browser.get('https://www.instagram.com/' + username)

prof_img, num_of_posts, followers, following = getUserInfo(browser, username)

prev_divs = browser.find_elements_by_class_name('_myci9')

try:
  body_elem = browser.find_element_by_tag_name('body')

  load_div = browser.find_element_by_class_name('_pupj3')
  load_button = load_div.find_element_by_tag_name('a')
  load_button.click()

  while(len(browser.find_elements_by_class_name('_myci9')) > len(prev_divs)):
    prev_divs = browser.find_elements_by_class_name('_myci9')
    body_elem.send_keys(Keys.END)
    sleep(1)
    body_elem.send_keys(Keys.HOME)
    sleep(1)

except NoSuchElementException as err:
  print('Only few posts')

links_elems = [div.find_elements_by_tag_name('a') for div in prev_divs]
links = sum([[link_elem.get_attribute('href') for link_elem in elems] for elems in links_elems], [])

postInfos = []

for link in links:
  browser.get(link)

  try:
    img, tags, likes, comments = extractPostInfo(browser)
  except NoSuchElementException as err:
    print('Error: ' + str(err))

  postInfos.append({'img': img, 'tags': tags, 'likes': likes, 'comments': comments})

information = {
  'prof_img': prof_img,
  'num_of_posts': num_of_posts,
  'followers': followers,
  'following': following,
  'posts': postInfos
}

with open('./follow_num_plot/information.json', 'w') as fp:
  json.dump(information, fp)

browser.delete_all_cookies()
browser.close()