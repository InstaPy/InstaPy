# -*- coding: utf-8 -*-
"""Module which handles the commenting features"""
from random import choice

from .time_util import sleep


def comment_image(browser, comments):
  """Checks if it should comment on the image"""
  rand_comment = (choice(comments))

  comment_input = browser.find_element_by_xpath\
    ('//input[@placeholder = "Add a comment…"]')
  comment_input.send_keys(rand_comment)
  comment_input.submit()

  print('--> Commented: ' + rand_comment)
  sleep(2)
  return 1
