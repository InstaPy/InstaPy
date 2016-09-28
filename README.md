<img src="https://s3-eu-central-1.amazonaws.com/centaur-wp/designweek/prod/content/uploads/2016/05/11170038/Instagram_Logo-1002x1003.jpg" width="200" align="right">
# InstaPy

<h2>Instagram Like, Comment and Follow Automation Script</h2>
<p>Automation Script for "farming" Likes, Comments and Followers on Instagram.<br />
Implemented in Python using the selenium module.</p>

<h4>Example</h4>
```
from instapy import InstaPy

InstaPy(username='test', password='test')\ #start the session
  .login()\ #logs you in with the given username and pw
  .set_do_comment(True, percentage=10)\ #enables comments
  .set_comments(['Cool!', 'Awesome!', 'Nice!'])\ #sets the used comments
  .set_dont_include(['friend1', 'friend2', 'friend3'])\ #won't commenting/unfollow real friends
  .set_dont_like(['food', 'girl', 'hot'])\ # won't like posts that contain these
  .like_by_tags(['dog', '#cat'], amount=2)\ # likes 2 posts for dog and for cat
  .end() # ends the session
```
<h2>It's easy to use and the built in delays prevet your account from getting banned</h2>
<h5>Getting started</h5>
```
pip install selenium
```
<p>If you want the script to get the username and password for your environment, you can do:</p>
```
export INSTA_USER="<Your username>"
export INSTA_PW="<Your password>"
```
<hr />
```
from instapy import InstaPy

#if you don't provide arguments, the script will look for INSTA_USER and INSTA_PW in the environment

session = InstaPy(username='test', password='test')
session.login()

#likes 100 posts of dogs

session.like_by_tags(['#dog'], amount=100)
session.like_from_image(url='www.instagram.com/image', amount=100)

session.end()
```

<h5>Restricting Likes</h5>
```
#searches the description for the given words and won't
# like the image if one of the words are in there

session.set_dont_like(['food', 'eat', 'meal'])
```

<h5>Commenting</h5>
```
#default enabled=False, ~ every 4th image will be commented on

session.set_do_comment(enabled=True, percentage=25)
session.set_comments(['Awesome', 'Really Cool', 'I like your stuff'])
```

<h5>Following</h5>
```
#default enabled=False, follows ~ every 10th user from the images

session.set_do_follow(enabled=True, percentage=10)
```

<h5>Excluding friends</h5>
```
#will prevent commenting on and unfollowing your good friends (the images will still be liked)

session.set_dont_include(['friend1', 'friend2', 'friend3'])
```

<h5>Unfollowing</h5>
```
#unfollows 10 of the accounts your following -> instagram will only unfollow 10 before you'll be 'blocked for 10 minutes' (if you enter a higher number than 10 it will unfollow 10, then wait 10 minutes and will continue then)

session.unfollow_users(amount=10) 
```

<h6>Have Fun & Feel Free to report any issues</h6>
