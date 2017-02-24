#!/usr/bin/env python3.5

from random import randint
from random import sample
from time import sleep
from instapy import InstaPy

import comments

tag_list = ['sex','nude','naked','beef','pork','seafood',
            'egg','chicken','cheese','sausage','lobster',
            'fisch','schwein','lamm','rind','kuh','meeresfrüchte',
            'schaf','ziege','hummer','yoghurt','joghurt','dairy',
            'meal','food','eat','pancake','cake','dessert',
            'protein','essen','mahl','breakfast','lunch',
            'dinner','turkey','truthahn','plate','bacon',
            'sushi','burger','salmon','shrimp','steak',
            'schnitzel','goat','oxtail','mayo','fur','leather',
            'cream', 'hunt','gun', 'shoot', 'slaughter', 'pussy',
	    'breakfast', 'dinner', 'lunch']

like_tag_list = ['veganfoodshare', 'veganfood', 'whatveganseat', 'nature',
		'govegan', 'veganism', 'environment', 'landscape', 'vegansofig',
		 'veganfoodshare', 'veganrecipes', 'veganfit', 'forest', 'veggies',
        	'travel', 'landscape', 'iphoneonly', 'woods', 'animals', 'veganfoodie',
		'animal', 'veganism', 'good', 'mountain', 'gopro', 'holiday', 'vacation',
		'enjoy']

friendList = ['verenaeipper', 'shaymaamawad', 'laraladybird', 'benitalea',
              'sanne_kelle', 'eippitraveleurope', 'neburius_ezluhcs',
              'michaswagner', 'paya92', 'micha.schulze', 'chrissifassl',
              'crstph', 'mrholz', 'ericisinthehaus', 'debbsta7112', 'clenomenal',
	      'paya92', 'shaymaamawad', 'jon.hurleys']

ignore_list = ['vegan', 'veggie', 'plantbased']

normalComments = comments.normal_comments

foodComments = comments.food_comments

natureComments = comments.nature_comments

followed = 0

with open('./logs/followed.txt', 'r') as followFile:
  followed = int(followFile.read())

def startScript():
  tag1 = randint(250, 350)
  tag2 = randint(50, 400 - tag1)
  tag3 = 500 - tag1 - tag2

  InstaPy(username='tombiggoingvegan', password='Hawai1994')\
    .login()\
    .set_dont_like(tag_list)\
    .set_dont_include(friendList)\
    .set_ignore_if_contains(ignore_list)\
    .unfollow_users(amount=followed)\
    .set_do_comment(enabled=True, percentage=5)\
    .set_do_follow(enabled=True, percentage=10)\
    .set_comments(comments=normalComments)\
    .set_use_clarifai(enabled=True)\
    .clarifai_check_img_for(['nsfw'])\
    .clarifai_check_img_for(['food', 'lunch', 'dinner'], comment=True, comments=foodComments)\
    .clarifai_check_img_for(['lake', 'landscape', 'mountain'], comment=True, comments=natureComments)\
    .like_by_tags(['vegan'], amount=tag1)\
    .like_by_tags(sample(like_tag_list, 1), amount=tag2)\
    .like_by_tags(sample(like_tag_list, 1), amount=tag3)\
    .end()

runFile = open('./logs/run.txt', 'a')

if randint(0,20) < 19:
  try:
    runFile.write('started\n')
    runFile.close()
    sleep(randint(0, 60 * 10))
    startScript()
  except Exception as err:
    with open('/root/erros.log', 'a') as errLog:
      errLog.write(str(err) + '\n')

else:
  runFile.write('not started\n')
  runFile.close()
