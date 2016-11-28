from random import randint
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
            'cream']

friendList = ['verenaeipper', 'shaymaamawad', 'laraladybird', 'benitalea',
              'sanne_kelle', 'eippitraveleurope', 'neburius_ezluhcs',
              'michaswagner', 'paya92', 'micha.schulze', 'chrissifassl',
              'crstph', 'mrholz', 'ericisinthehaus']

ignore_list = ['vegan', 'veggie', 'plantbased']

normalComments = ['Awesome!', 'Cool!', 'Love your stuff!', 'Nice Pics!',
                  'Really cool', 'Superb', 'That looks amazing']
foodComments = ['Tasty!', 'Nice!', 'Yum!', 'Would love to try that!',
                'Perfect!', 'Looks tasty', 'Nice!', 'Definitely trying this',
                'Yummy!', 'Love it!', 'Yum that looks delicious!',
                'Looks delicious!', 'Wow!! This looks so tasty!',
                'That looks amazing']
natureComments = ['Epic!', 'Perfect', 'Would love to visit this Place!',
                  'Beautiful', 'Impressive!', 'Awesome!', 'Incredible!',
                  ]

def startScript():
  InstaPy()\
    .login()\
    .set_dont_like(tag_list)\
    .set_dont_include(friendList)\
    .set_ignore_if_contains(ignore_list)\
    .set_do_comment(enabled=True, percentage=10)\
    .set_comments(comments=normalComments)\
    .set_use_clarifai(enabled=True)\
    .clarifai_check_img_for(['nsfw'])\
    .clarifai_check_img_for(['food', 'lunch', 'dinner'], comment=True, comments=foodComments)\
    .clarifai_check_img_for(['lake', 'landscape', 'mountain'], comment=True, comments=natureComments)\
    .like_by_tags(['vegan', 'veganfoodshare', 'veganfood', 'whatveganseat','nature'], amount=100)\
    .end()

runFile = open('/root/InstaPy/logs/run.txt', 'a')


if randint(0,10) < 6:
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
