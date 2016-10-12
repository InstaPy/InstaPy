from instapy import InstaPy

#Write your automation here
#Stuck ? Look at the github page or the examples in the examples folder

InstaPy(username='<username>', password='<password>')\
  .login()\
  .like_by_tags(['cat', 'dog'], amount=100)\
  .end()