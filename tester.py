from instapy import InstaPy

tag_list = ['sex','nude','naked','beef','pork','seafood',
            'egg','chicken','cheese','sausage','lobster',
            'fisch','schwein','lamm','rind','kuh','meeresfrüchte',
            'schaf','ziege','hummer','yoghurt','joghurt','dairy',
            'meal','food','eat','pancake','cake','dessert',
            'protein','essen','mahl','breakfast','lunch',
            'dinner','turkey','truthahn','plate','bacon',
            'sushi','burger','salmon','shrimp','steak',
            'schnitzel','goat','oxtail','mayo','fur','leather']

ignore_list = ['vegan', 'veggie', 'plantbased']


InstaPy()\
  .login()\
  .set_dont_like(tag_list)\
  .set_ignore_if_contains(ignore_list)\
  .set_do_comment(enabled=True, percentage=10)\
  .set_comments(comments=['Awesome!', 'Cool!', 'Love your stuff!'])\
  .set_use_clarifai(enabled=True)\
  .clarifai_check_img_for(['nsfw'])\
  .clarifai_check_img_for(['food', 'lunch', 'dinner'], comment=True, comments=['Tasty!', 'Nice!', 'Yum!'])\
  .clarifai_check_img_for(['lake', 'landscape', 'mountain'], comment=True, comments=['Epic!', 'Perfect'])\
  .set_do_follow(enabled=True, percentage=10)\
  .like_by_tags(['veganfoodshare'], amount=50)\
  .end()