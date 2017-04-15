"""Module which handles the clarifai api and checks
the image for invalid content"""
from clarifai.client import ClarifaiApi

def check_image(browser, clarifai_id, clarifai_secret, img_tags, full_match=False):
  """Uses the link to the image to check for invalid content
  in the image"""
  clarifai_api = ClarifaiApi(clarifai_id, clarifai_secret)

  img_link = get_imagelink(browser)
  result = clarifai_api.tag_image_urls(img_link)
  result_tags = result['results'][0]['result']['tag']['classes']

  for pair in img_tags:
    if not pair[1]:
      if given_tags_in_result(pair[0], result_tags, full_match):
        print('Inappropriate content in Image, not commenting')
        return False, []
    else:
      if given_tags_in_result(pair[0], result_tags, full_match):
        return True, pair[2]

  return True, []

def given_tags_in_result(search_tags, result_tags, full_match=False):
  """Checks the result tags if it contains one (or all) search tags """
  if full_match:
    return all([tag in result_tags for tag in search_tags])
  else:
    return any((tag in result_tags for tag in search_tags))


def get_imagelink(browser):
  """Gets the imagelink from the given webpage open in the browser"""
  return browser.find_element_by_xpath('//img[@class = "_icyx7"]')\
         .get_attribute('src')
