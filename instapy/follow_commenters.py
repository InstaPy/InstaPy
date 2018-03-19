"""Methods to extract the data for the given usernames profile"""
#most of the code copied from https://github.com/timgrossmann/instagram-profilecrawl/blob/master/util/extractor.py
from time import sleep
from re import findall

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

def get_user_info(browser):
  """Get the basic user info from the profile screen"""

  container = browser.find_element_by_class_name('_mesn5')
  img_container = browser.find_element_by_class_name('_b0acm')

  infos = container.find_elements_by_class_name('_t98z6')
  print ("infos: ", infos)
                          
  alias_name = container.find_element_by_class_name('_ienqf')\
                        .find_element_by_tag_name('h1').text
  try:
    bio = container.find_element_by_class_name('_tb97a')\
                        .find_element_by_tag_name('span').text                      
  except:
    print ("\nBio is empty")
    bio = ""
  print ("\nalias name: ", alias_name)
  print ("\nbio: ", bio,"\n")
  prof_img = img_container.find_element_by_tag_name('img').get_attribute('src')
  num_of_posts = int(infos[0].text.split(' ')[0].replace(',', ''))
  followers = infos[1].text.split(' ')[0].replace(',', '').replace('.', '')
  followers = int(followers.replace('k', '00').replace('m', '00000'))
  following = infos[2].text.split(' ')[0].replace(',', '').replace('.', '')
  following = int(following.replace('k', '00'))

  return alias_name, bio, prof_img, num_of_posts, followers, following


def extract_post_info(browser):
  """Get the information from the current post"""

  post = browser.find_element_by_class_name('_622au')

  #print('BEFORE IMG')

  imgs = post.find_elements_by_tag_name('img')
  img = ''
  
  
  if len(imgs) >= 2:
    img = imgs[1].get_attribute('src')
    

  

  # if more than 22 comment elements, use the second to see
  # how much comments, else count the li's

  # first element is the text, second either the first comment
  # or the button to display all the comments
  comments = []
  tags = []
  
  
  
  user_commented_list = []
  if post.find_elements_by_tag_name('ul'):
    comment_list = post.find_element_by_tag_name('ul')
    comments = comment_list.find_elements_by_tag_name('li')
    
    if len(comments) > 1:
      # load hidden comments
      while (comments[1].text == 'load more comments'):
        comments[1].find_element_by_tag_name('button').click()
        comment_list = post.find_element_by_tag_name('ul')
        comments = comment_list.find_elements_by_tag_name('li')
      #adding who commented into user_commented_list
      for comm in comments:
        user_commented = comm.find_element_by_tag_name('a').get_attribute("href").split('/')
        user_commented_list.append(user_commented[3])
        
      tags = comments[0].text + ' ' + comments[1].text
    else:
      tags = comments[0].text

    tags = findall(r'#[A-Za-z0-9]*', tags)
    print (len(user_commented_list), " comments.")
  return user_commented_list


def extract_information(browser, nicknameget):
  
  """Get all the information for the given username"""

  browser.get('https://www.instagram.com/' + nicknameget)
  
  try:
    alias_name, bio, prof_img, num_of_posts, followers, following \
    = get_user_info(browser)
  except:
    print ("\nError: Couldn't get user profile.\nTerminating")
    quit()
  prev_divs = browser.find_elements_by_class_name('_70iju')


  try:
    body_elem = browser.find_element_by_tag_name('body')

    #load_button = body_elem.find_element_by_xpath\
    #  ('//a[contains(@class, "_1cr2e _epyes")]')
    #body_elem.send_keys(Keys.END)
    #sleep(3)

    #load_button.click()

    links = []
    links2 = []

    
    #list links contains 30 links from the current view, as that is the maximum Instagram is showing at one time
    #list links2 contains all the links collected so far
    previouslen = -1
    while (len(links2) < num_of_posts):
      
      prev_divs = browser.find_elements_by_tag_name('main')      
      links_elems = [div.find_elements_by_tag_name('a') for div in prev_divs]  
      links = sum([[link_elem.get_attribute('href')
        for link_elem in elems] for elems in links_elems], [])
      for link in links:
        if "/p/" in link:
          links2.append(link) 
      links2 = list(set(links2))   
      if (len(links2) == previouslen):
        print ("Cannot scroll, quitting..")
        sleep(0.5)
        break
      else:
        print ("Scrolling profile ", len(links2), "/", num_of_posts)
        body_elem.send_keys(Keys.END)
        previouslen = len(links2)
        sleep(1.5)

  except NoSuchElementException as err:
    print('- Something went terribly wrong\n')

  post_infos = []

  counter = 1  
  #into user_commented_total_list I will add all username links who commented on any post of this user
  user_commented_total_list = []
  for link in links2:
    
    print ("\n", counter , "/", len(links2))
    counter = counter + 1
    print ("\nScrapping link: ", link)
    browser.get(link)  
    try:
      user_commented_list = extract_post_info(browser)
      print("ucl", user_commented_list)
      
      user_commented_total_list = user_commented_total_list + user_commented_list
      #sleep(1.5)
    except NoSuchElementException:
      print('- Could not get information from post: ' + link)




  #sorts the list by frequencies, so users who comment the most are at the top
  import collections
  from operator import itemgetter, attrgetter
  counter=collections.Counter(user_commented_total_list)
  com = sorted(counter.most_common(), key=itemgetter(1,0), reverse=True)
  com = map(lambda x: [x[0]] * x[1], com)
  user_commented_total_list = [item for sublist in com for item in sublist]
   
  #remove duplicates preserving order (that's why not using set())
  user_commented_list = []
  last = ''
  for i in range(len(user_commented_total_list)):
    if nicknameget.lower() != user_commented_total_list[i]:
      if last != user_commented_total_list[i]:
        user_commented_list.append(user_commented_total_list[i])
      last = user_commented_total_list[i]     

  print ("successful")
  return user_commented_list
