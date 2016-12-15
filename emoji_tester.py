# -*- coding: utf-8 -*-

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

ignore_list = ['vegan', 'veggie', 'plantbased']

normalComments = ['Awesome!']

InstaPy()\
  .login()\
  .set_dont_like(tag_list)\
  .set_ignore_if_contains(ignore_list)\
  .set_do_comment(enabled=True, percentage=100)\
  .set_comments(comments=normalComments)\
  .like_by_tags(['vegan'], amount=1)\
  .end()