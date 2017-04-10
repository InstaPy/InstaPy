> **Think this tool is worth supporting?** <br />
> Feel free to contribute to the project in whatever way! <br /> If you're not familiar with python, you could build a github page for this project (Just head over to the issues, there might be a task for you). You're a marketer? Perfect! hit me with a message on contact.timgrossmann@gmail.com. <br /> **Become a part of InstaPy!**

> **Disclaimer**: Please Note that this is a research project. I am by no means responsible for any usage of this tool. Use on your own behalf. I'm also not responsible if your accounts get banned due to extensive use of this tool.

<img src="http://i.imgur.com/9ZjtveL.png" width="150" align="right">

# InstaPy
[![GitHub license](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/timgrossmann/InstaPy/blob/master/LICENSE)
[![built with Selenium](https://img.shields.io/badge/built%20with-Selenium-red.svg)](https://github.com/SeleniumHQ/selenium)
[![built with Python3](https://img.shields.io/badge/Built%20with-Python3-green.svg)](https://www.python.org/)

### [Read about how it works on Medium](https://medium.freecodecamp.com/my-open-source-instagram-bot-got-me-2-500-real-followers-for-5-in-server-costs-e40491358340)

### Instagram Like, Comment and Follow Automation Script
>Automation Script for "farming" Likes, Comments and Followers on Instagram.<br />
Implemented in Python using the Selenium module.

<h4>Example</h4>

```python
from instapy import InstaPy

InstaPy(username='test', password='test')\
  .login()\
  .set_do_comment(True, percentage=10)\
  .set_comments(['Cool!', 'Awesome!', 'Nice!'])\
  .set_dont_include(['friend1', 'friend2', 'friend3'])\
  .set_dont_like(['food', 'girl', 'hot'])\
  .set_ignore_if_contains(['pizza'])\
  .like_by_tags(['dog', '#cat'], amount=100)\
  .end()
```
<h2>It's easy to use and the built in delays prevent your account from getting banned. (Just make sure you don't like 1000s of post/day)</h2>
<h3>Getting started</h3>

#### Make sure to get the right ```chromedriver``` for your system from here: https://sites.google.com/a/chromium.org/chromedriver/downloads. Just put it in /assets.
```bash
cd InstaPy
pip install .
```

or

```bash
cd InstaPy
python setup.py install
```

<p>If you want the script to get the username and password for your environment, you can do:</p>

```
export INSTA_USER="<Your username>"
export INSTA_PW="<Your password>"
```
<hr />

```python
from instapy import InstaPy

#if you don't provide arguments, the script will look for INSTA_USER and INSTA_PW in the environment

session = InstaPy(username='test', password='test')
session.login()

#likes 100 posts of dogs

session.like_by_tags(['#dog'], amount=100)
session.like_from_image(url='www.instagram.com/image', amount=100)

#likes 50 photos of other animals

session.like_by_tags(['#animals'], amount=50, media='Photo')
session.like_from_image(url='www.instagram.com/image', amount=50, media='Photo')

#likes 15 videos of cats

session.like_by_tags(['#cat'], amount=15, media='Video')
session.like_from_image(url='www.instagram.com/image', amount=15, media='Video')

session.end()
```

<h5>Restricting Likes</h5>

```python
#searches the description for the given words and won't
# like the image if one of the words are in there

session.set_dont_like(['food', 'eat', 'meal'])
```
<h5>Ignoring Restrictions</h5>

```python
#will ignore the don't like if the description contains
# one of the given words

session.set_ignore_if_contains(['glutenfree', 'french', 'tasty'])
```

<h5>Commenting</h5>

```python
#default enabled=False, ~ every 4th image will be commented on

session.set_do_comment(enabled=True, percentage=25)
session.set_comments(['Awesome', 'Really Cool', 'I like your stuff'])

# you can also set comments for specific media types (Photo / Video)
session.set_comments(['Nice shot!'], media='Photo')
session.set_comments(['Great Video!'], media='Video')
```

<h5>Following</h5>

```python
#default enabled=False, follows ~ every 10th user from the images, times=1 (only follows a user once (if unfollowed again))

session.set_do_follow(enabled=True, percentage=10, times=2)
```

<h5>Excluding friends</h5>

```python
#will prevent commenting on and unfollowing your good friends (the images will still be liked)

session.set_dont_include(['friend1', 'friend2', 'friend3'])
```

<h5>Unfollowing</h5>

```python
#unfollows 10 of the accounts your following -> instagram will only unfollow 10 before you'll be 'blocked for 10 minutes' (if you enter a higher number than 10 it will unfollow 10, then wait 10 minutes and will continue then)

session.unfollow_users(amount=10)
```
<br />
<h3>Clarifai ImageAPI</h3>
<img src="https://d1qb2nb5cznatu.cloudfront.net/startups/i/396673-2fb6e8026b393dddddc093c23d8cd866-medium_jpg.jpg?buster=1399901540" width="200" align="right">
<h6>Note: Head over to https://developer.clarifai.com/signup/ and create a free account, once you're logged in go to https://developer.clarifai.com/account/applications/ and create a new application. You can find the client ID and Secret there. You get 5000 API-calls free/month.</h6>
<p>If you want the script to get your Clarifai_ID and Clarifai_Secret for your environment, you can do:</p>

```
export CLARIFAI_ID="<ProjectID>"
export CLARIFAI_SECRET="<Project Secret>"
```
<h4>Example with Imagecontent handling</h4>

```python
from instapy import InstaPy

InstaPy(username='test', password='test')\
  .login()\
  .set_do_comment(True, percentage=10)\
  .set_comments(['Cool!', 'Awesome!', 'Nice!'])\
  .set_dont_include(['friend1', 'friend2', 'friend3'])\
  .set_dont_like(['food', 'girl', 'hot'])\
  .set_ignore_if_contains(['pizza'])\
  .set_use_clarifai(enabled=True)\
  .clarifai_check_img_for(['nsfw'])\
  .clarifai_check_img_for(['food', 'lunch', 'dinner'], comment=True, comments=['Tasty!', 'Nice!', 'Yum!'])\
  .like_by_tags(['dog', '#cat'], amount=100)\
  .end()
```
<h5>Enabling Imagechecking</h5>

```python
#default enabled=False , enables the checking with the clarifai api (image tagging)
#if secret and proj_id are not set, it will get the environment Variables
# 'Clarifai_SECRET' and 'CLARIFAI_ID'

session.set_use_clarifai(enabled=True, secret='xyz', proj_id='123')
```
<h5>Filtering inappropriate images</h5>

```python
# uses the clarifai api to check if the image contains nsfw content
# -> won't comment if image is nsfw

session.clarifai_check_img_for(['nsfw'])
```
<h5>Specialized comments for images with specific content</h5>

```python
#checks the image for keywords food and lunch, if found,
#comments with the given comments

session.clarifai_check_img_for(['food', 'lunch'], comment=True, comments=['Tasty!', 'Yum!'])
```
<h6>Check out https://clarifai.com/demo to see some of the available tags.</h6>
<hr />
<h6>Have Fun & Feel Free to report any issues</h6>
