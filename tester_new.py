#!/usr/bin/env python3.5

from random import randint
from random import sample
from time import sleep
from instapy import InstaPy

tag_list = ['sex','nude','naked','beef','pork','seafood',
            'egg','chicken','cheese','sausage','lobster',
            'fisch','schwein','lamm','rind','kuh','meeresfrüchte',
            'schaf','ziege','hummer','yoghurt','joghurt','dairy',
            'meal','food','eat','pancake','cake','dessert',
            'protein','essen','mahl','breakfast','lunch',
            'dinner','turkey','truthahn','plate','bacon',
            'sushi','burger','salmon','shrimp','steak',
            'schnitzel','goat','oxtail','mayo','fur','leather',
            'cream', 'hunt','gun', 'shoot', 'slaughter', 'pussy']

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

normalComments = [u'Awesome! \u270A', u'Awesome! \u270C', u'Cool! \u270C',
		  u'Love your stuff! \u2757', u'Nice Pics! \u27B0',
                  u'Really cool \u270C', u'Superb \u2728',
		  u'That looks amazing \u2714', u'That looks amazing!',
		  u'Epic! \u2B50', u'Great Stuff! \u2705', u'Nice Stuff \u2757',
		  u'Nice Pic! \u263A', u'Great Stuff', u'Awesome Stuff!', u'\u270A',
            	  u'\u270C', u'\u2728', u'\u2705', u' \u2665', u'Damn!', u'Bravo!',
		  u'Neat!', u'Thats really neat! \u270C', u'Lovely \u2665',
		  u'So cool! \u270A', u'You Rock!', u'Your feed rocks!']

foodComments = [u'Tasty! \u2665', u'Tasty!', u'Tasty', u'Nice!', u'Nice  \u2757',
		u'Yum! \u270C', u'Would love to try that! \u270B',
		u'Would love to try that!', u'Yummy \u2728', u'Love it! \u2665',
                u'Perfect! \u2714', u'Perfect!', u'Looks tasty\u203C', u'Nice!',
		u'Nice \u270A', u'Definitely trying this \u270B', u'Definitely trying this!',
                u'Yummy!', u'Yummy \u2757', u'Love it!', u'Yum that looks delicious! \u2665',
                u'Looks delicious! \u263A', u'Wow!! This looks so tasty! \u2728',
                u'That looks amazing \u2757', u'Great! \u270C', u'Sooo good \u2665',
		u'Just... Perfect\u2757 \u2B50', u'Mesmerizing \u263A', u'\u270A',
                u'\u270C', u'\u2728', u'\u2705', u' \u2665', u'Ohh yes...', u'Damn!',
		u'Bravo!', u'Neat!', u'Thats really neat! \u270C', u'Lovely \u2665',
                u'So cool! \u270A']

natureComments = [u'Epic! \u2B50', u'Epic\u2757', u'Epic', u'Perfect',
		  u'Would love to visit this Place! \u2665', u'Impressive \u2600',
                  u'Beautiful \u2728', u'Beautiful!', u'Impressive!', u'Awesome!',
 		  u'Incredible!', u'Incredible \u270C', u'Incredible Shot \u2764',
                  u'Pretty awesome! \u270A', u'Lovely', u'Visit this place \u2705',
                  u'\u270A', u'\u270C', u'\u2728', u'\u2705', u' \u2665', u'Damn!',
	          u'Bravo!', u'Neat!', u'Thats really neat! \u270C', u'Lovely \u2665',
                  u'So cool! \u270A']

followed = 0

with open('./logs/followed.txt', 'r') as followFile:
  followed = int(followFile.read())

def startScript():
  tag1 = randint(250, 350)
  tag2 = randint(50, 400 - tag1)
  tag3 = 500 - tag1 - tag2

  InstaPy()\
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

runFile = open('/root/InstaPy/logs/run.txt', 'a')


if randint(0,20) < 19:
  try:
    runFile.write('started\n')
    runFile.close()
    sleep(randint(0, 60 * 30))
    startScript()
  except Exception as err:
    with open('/root/erros.log', 'a') as errLog:
      errLog.write(str(err) + '\n')

else:
  runFile.write('not started\n')
  runFile.close()
