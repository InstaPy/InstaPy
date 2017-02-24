#!/usr/bin/env python3.5

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
            'cream', 'hunt','gun', 'shoot', 'slaughter', 'pussy',
	    'breakfast', 'dinner', 'lunch']


InstaPy(username='tombiggoingvegan', password='Hawai1994')\
    .login()\
    .set_dont_like(tag_list)\
    .set_do_follow(enabled=True, percentage=100, times=3)\
    .like_by_tags(['travel'], amount=5)\
    .end()