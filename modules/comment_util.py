"""Module which handles the commenting features"""
from random import randint
from random import choice
from time import sleep

def comment_image(browser, comments, comment_percentage):
  """Checks if it should comment on the image"""
  if randint(0, 100) <= comment_percentage:
    rand_comment = (choice(comments))

    comment_input = browser.find_element_by_xpath\
      ('//input[@placeholder = "Add a comment…"]')
    comment_input.send_keys(rand_comment)
    comment_input.submit()

    print('--> Commented: ' + rand_comment)
    sleep(1)
    return 1
  else:
    print('--> Not commented')
    sleep(1)
    return 0
