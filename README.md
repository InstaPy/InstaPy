<img src="https://i.imgur.com/sJzfZsL.jpg" width="150" align="right">

# InstaPy
[![MIT license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/timgrossmann/InstaPy/blob/master/LICENSE)
[![built with Selenium](https://img.shields.io/badge/built%20with-Selenium-yellow.svg)](https://github.com/SeleniumHQ/selenium)
[![built with Python3](https://img.shields.io/badge/built%20with-Python3-red.svg)](https://www.python.org/)
[![Travis](https://img.shields.io/travis/rust-lang/rust.svg)](https://travis-ci.org/timgrossmann/InstaPy)

### Automation Script for “farming” Likes, Comments and Followers on Instagram
Implemented in Python using the Selenium module.

**Think this tool is worth supporting?**
Head over to https://github.com/timgrossmann/InstaPy/wiki/How-to-Contribute to find out how you can help.
**Become a part of InstaPy!**

**Have an issue?**
Head over to https://github.com/timgrossmann/InstaPy/wiki/Reporting-An-Issue to find out how to report this to us and get help.

**Disclaimer**: Please Note that this is a research project. I am by no means responsible for any usage of this tool. Use on your own behalf. I’m also not responsible if your accounts get banned due to extensive use of this tool.

#### Newsletter: [SignUp for the Newsletter here!](http://eepurl.com/cZbV_v)

### Social

#### [Slack Workspace](https://join.slack.com/t/instapy/shared_invite/enQtMjYzNTgwMDg3MDEyLTk2NWI0MjY2MTVjYmM2NjFlYjVmMmE0ZjU1OGQ0OWM2MTQwOTc1NTIyOGVhZDEwMTFkYzFmODE5ZWIxZjhjMTQ) | [InstaPy Twitter](https://twitter.com/InstaPy) | [My Twitter](https://twitter.com/timigrossmann) | [How it works (Medium)](https://medium.freecodecamp.com/my-open-source-instagram-bot-got-me-2-500-real-followers-for-5-in-server-costs-e40491358340) | [Check out the talk](https://youtu.be/4TmKFZy-ioQ) |
[Listen to the "Talk Python to me"-Episode](https://talkpython.fm/episodes/show/142/automating-the-web-with-selenium-and-instapy) | [Support InstaPy!](https://www.paypal.me/supportInstaPy)

[![paypal](https://img.shields.io/badge/-PayPal-blue.svg)](https://www.paypal.me/supportInstaPy)

Table of Contents
=================

* [Getting Started](#getting-started)
  * [Basic Installation](#basic-installation)
  * [Basic Setup](#basic-setup)
* [InstaPy Available Features](#instapy-available-features)
  * [Commenting](#commenting)
  * [Following](#following)
  * [Following by a list](#following-by-a-list)
  * [Follow someone else's followers](#follow-someone-elses-followers)
  * [Follow users that someone else is following](#follow-users-that-someone-else-is-following)
  * [Follow someone else's followers/following](#follow-someone-elses-followersfollowing)
  * [Interact with specific users](#interact-with-specific-users)
  * [Interact with users that someone else is following](#interact-with-users-that-someone-else-is-following)
  * [Interact with someone else's followers](#interact-with-someone-elses-followers)
  * [Unfollowing](#unfollowing)
  * [Don't unfollow active users](#dont-unfollow-active-users)
  * [Interactions based on the number of followers and/or following a user has](#interactions-based-on-the-number-of-followers-andor-following-a-user-has)
  * [Liking based on the number of existing likes a post has](#liking-based-on-the-number-of-existing-likes-a-post-has)
  * [Commenting based on the number of existing comments a post has](#commenting-based-on-the-number-of-existing-comments-a-post-has)
  * [Comment by Locations](#comment-by-locations)
  * [Like by Locations](#like-by-locations)
  * [Like by Tags](#like-by-tags)
  * [Like by Feeds](#like-by-feeds)
  * [Restricting Likes](#restricting-likes)
  * [Ignoring Users](#ignoring-users)
  * [Ignoring Restrictions](#ignoring-restrictions)
  * [Excluding friends](#excluding-friends)
  * [Blacklist Campaign](#blacklist-campaign)
  * [Smart Hashtags](#smart-hashtags)
  * [Follow/Unfollow/exclude not working?](#followunfollowexclude-not-working)
  * [Bypass Suspicious Login Attempt](#bypass-suspicious-login-attempt)
* [Third Party InstaPy GUI for Windows](#third-party-instapy-gui-for-windows)
* [Use a proxy](#use-a-proxy)
* [Switching to Firefox](#switching-to-firefox)
* [Emoji Support](#emoji-support)
* [Clarifai ImageAPI](#clarifai-imageapi)
* [Running on a Server](#running-on-a-server)
* [Running on a Headless Browser](#running-on-a-headless-browser)
* [Running Multiple Accounts](#running-multiple-accounts)
* [Running with Docker microservices manual](#running-with-docker-microservices-manual)
* [Running all-in-one with Docker (obsolete)](#running-all-in-one-with-docker-obsolete)
* [Automate InstaPy](#automate-instapy)
  * [Windows Task Scheduler](#windows-task-scheduler)
  * [cron](#cron)
  * [Schedule](#schedule)
* [Extra Informations](#extra-informations)

## Getting started

### Video tutorials:
**[Setting up InstaPy for OSX](https://www.youtube.com/watch?v=I025CEBJCvQ)**

**[Setting up InstaPy at Digital Ocean (for Debian)](https://www.youtube.com/watch?v=2Ci-hXU1IEY)**

### Guides:
**[How to Ubuntu (64-Bit)](./docs/How_To_DO_Ubuntu_on_Digital_Ocean.md) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**

**[How to RaspberryPi](./docs/How_to_Raspberry.md) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**

**[How to Windows](./docs/How_to_Windows.md)**

### Basic Installation:

```bash
1. git clone https://github.com/timgrossmann/InstaPy.git
2. cd InstaPy
3. pip install .
or
3. python setup.py install
```
4. Download ```chromedriver``` for your system [from here](https://sites.google.com/a/chromium.org/chromedriver/downloads). Extract the .zip file and put it in ```/assets``` folder.

### Preferred Installation:

The best way to install InstaPy is to create a virtualenv, install InstaPy there and run it from a separate file:

```bash
1. virtualenv venv
2. source venv/bin/activate
3. pip install git+https://github.com/timgrossmann/InstaPy.git
```

If you're not familiar with virtualenv, please [read about it here](https://virtualenv.pypa.io/en/stable/) and use it to your advantage.
In essence, this is be the _only_ Python library you should install as root (e.g., with sudo). All other Python libraries should be inside a virtualenv.
Now copy/paste the `quickstart.py` Python code below and run your first InstaPy script. Remember to run it with Python from the virtualenv, so from `venv/bin/python`. To make sure which Python is used, run `which python`, it will tell you which Python is 'active'.
Running `source venv/bin/activate` will activate the correct Python to run InstaPy. To exit an activated virtualenv run `deactivate'.

### Set it up yourself with this Basic Setup

Basic setup is a good way to test the tool. At project root folder open `quickstart.py` and update with your username and password.

```python
from instapy import InstaPy

insta_username = ''
insta_password = ''

# if you want to run this script on a server,
# simply add nogui=True to the InstaPy() constructor
session = InstaPy(username=insta_username, password=insta_password)
session.login()

# set up all the settings
session.set_relationship_bounds(enabled=True,
				 potency_ratio=-1.21,
				  delimit_by_numbers=True,
				   max_followers=4590,
				    max_following=5555,
				     min_followers=45,
				      min_following=77)
session.set_do_comment(True, percentage=10)
session.set_comments(['aMEIzing!', 'So much fun!!', 'Nicey!'])
session.set_dont_include(['friend1', 'friend2', 'friend3'])
session.set_dont_like(['pizza', 'girl'])

# do the actual liking
session.like_by_tags(['natgeo', 'world'], amount=100)

# end the bot session
session.end()
```

Execute it:

```bash
$ python quickstart.py
```

### Or use one of our GUIs

**[1. Official Cross Platform GUI](https://github.com/ahmadudin/electron-instaPy-GUI)**

[<img src="https://raw.githubusercontent.com/ahmadudin/ahmadudin.github.io/master/assets/images/screencapture1.PNG" width="400" />](https://github.com/ahmadudin/electron-instaPy-GUI)

[2. Third Party InstaPy GUI for Windows](https://github.com/Nemixalone/GUI-tool-for-InstaPy-script)

[3. Session scheduling with Telegram](https://github.com/Tkd-Alex/Telegram-InstaPy-Scheduling)

## InstaPy Available Features

### Commenting

```python
# default enabled=False, ~ every 4th image will be commented on

session.set_do_comment(enabled=True, percentage=25)
session.set_comments(['Awesome', 'Really Cool', 'I like your stuff'])

# you can also set comments for specific media types (Photo / Video)

session.set_comments(['Nice shot!'], media='Photo')
session.set_comments(['Great Video!'], media='Video')

# and you can add the username of the poster to the comment by using

session.set_comments(['Nice shot! @{}'], media='Photo')
```


### Following

```python
# default enabled=False, follows ~ 10% of the users from the images, times=1
# (only follows a user once (if unfollowed again))

session.set_do_follow(enabled=True, percentage=10, times=2)
```

### Following by a list

```python
# follows each account from a list of instagram nicknames (only follows a user
# once (if unfollowed again)) would be useful for the precise targeting.
# For example, if one needs to get followbacks from followers of a chosen
# account/group of accounts.

accs = ['therock','natgeo']
session.follow_by_list(accs, times=1)
```

### Follow someone else's followers

```python
# Follows the followers of each given user
# The usernames can be either a list or a string
# The amount is for each account, in this case 30 users will be followed
# If randomize is false it will pick in a top-down fashion

session.follow_user_followers(['friend1', 'friend2', 'friend3'], amount=10, randomize=False)

# default sleep_delay=600 (10min) for every 10 user following, in this case
# sleep for 60 seconds

session.follow_user_followers(['friend1', 'friend2', 'friend3'], amount=10, randomize=False, sleep_delay=60)
```

### Follow users that someone else is following

```python
# Follows the people that a given users are following
# The usernames can be either a list or a string
# The amount is for each account, in this case 30 users will be followed
# If randomize is false it will pick in a top-down fashion

session.follow_user_following(['friend1', 'friend2', 'friend3'], amount=10, randomize=False)

# default sleep_delay=600 (10min) for every 10 user following, in this case
# sleep for 60 seconds

session.follow_user_following(['friend1', 'friend2', 'friend3'], amount=10, randomize=False, sleep_delay=60)
```

### Follow someone else's followers/following

```python
# For 50% of the 30 newly followed, move to their profile
# and randomly choose 5 pictures to be liked.
# Take into account the other set options like the comment rate
# and the filtering for inappropriate words or users

session.set_user_interact(amount=5, randomize=True, percentage=50, media='Photo')
session.follow_user_followers(['friend1', 'friend2', 'friend3'], amount=10, randomize=False, interact=True)
```

### Follow by Tags

```python
# Follow user based on hashtags (without liking the image)

session.follow_by_tags(['tag1', 'tag2'], amount=10)
```

### Follow users that liked some photo(s)

```python
# Follows the people that liked given photo
# The photo_url_arr is array of urls of photos, can also be just 1 url as string
# The amount is how many people to follow
# In this case 10 people who liked photo in photo_url_arr will be followed, for each photo

session.follow_likers(['https://www.instagram.com/p/Bga_UUrDFoc/', 'https://www.instagram.com/p/BgbOtLHD7yp/?taken-by=natgeo'], amount=10)
```

### Follow users that liked some user's post(s)

```python
# Follows the people that liked photos of given array of users
# The usernames can be array
# The photos_grab_amount is how many photos will I grat from users profile and analyze who liked it.
# The follow_likers_per_photo is how many people to follow per each photo
# Randomize=False will take photos from newes, true will take random from first 12
# In this case 2 random photos from each given user will be analyzed and 3 people who liked them will be followed, so 6 follows in total

session.follow_user_likers (['user1' , 'user2'], photos_grab_amount = 2, follow_likers_per_photo = 3, randomize=True)
```

### Follow users who comment the most on given user(s)'s photos

```python
# Follows the people that commented photos of given array of users
# The usernames can be array
# The amount is how many people to follow
# The daysold will only take commenters from photos no older than daysold days
# The max_pic will limit number of photos to analyze
# In thi case (max 100 newest photos & maximum 365 days old) from each given user will be analyzed and 100 people who commented the most will be followed

session.follow_commenters(['user1', 'user2', 'user3'], amount=100, daysold=365, max_pic = 100)
```

### Interact with specific users
```python
# Interact with specific users
# set_do_like, set_do_comment, set_do_follow are applicable

session.set_do_follow(enabled=False, percentage=50)
session.set_comments(["Cool", "Super!"])
session.set_do_comment(enabled=True, percentage=80)
session.set_do_like(True, percentage=70)
session.interact_by_users(['user1', 'user2', 'user3'], amount=5, randomize=True, media='Photo')
```

### Interact with users that someone else is following
```python
# Interact with the people that a given user is following
# set_do_comment, set_do_follow and set_do_like are applicable

session.set_user_interact(amount=5, randomize=True, percentage=50, media='Photo')
session.set_do_follow(enabled=False, percentage=70)
session.set_do_like(enabled=False, percentage=70)
session.set_comments(["Cool", "Super!"])
session.set_do_comment(enabled=True, percentage=80)
session.interact_user_following(['natgeo'], amount=10, randomize=True)
```

### Interact with someone else's followers
```python
# Interact with the people that a given user is following
# set_do_comment, set_do_follow and set_do_like are applicable

session.set_user_interact(amount=5, randomize=True, percentage=50, media='Photo')
session.set_do_follow(enabled=False, percentage=70)
session.set_do_like(enabled=False, percentage=70)
session.set_comments(["Cool", "Super!"])
session.set_do_comment(enabled=True, percentage=80)
session.interact_user_followers(['natgeo'], amount=10, randomize=True)
```

### Unfollowing

```python
# unfollows 10 of the accounts you're following -> instagram will only
# unfollow 10 before you'll be 'blocked for 10 minutes' (if you enter a
# higher number than 10 it will unfollow 10, then wait 10 minutes and will
# continue then).
# You can choose to only unfollow the user that Insta has followed by adding
# onlyInstapyFollowed = True otherwise it will unfollow all users
# You can choose unfollow method as FIFO (First-Input-First-Output) or
# LIFO (Last-Input-First-Output). The default is FIFO method.
# onlyInstapyMethod is using only when onlyInstapyFollowed = True
# sleep_delay sets the time it will sleep every 10 profile unfollow, default
# is 10min
session.unfollow_users(amount=10, onlyInstapyFollowed = True, onlyInstapyMethod = 'FIFO', sleep_delay=60 )

# You can only unfollow user that won't follow you back by adding
# onlyNotFollowMe = True it still only support on profile following
# you should disable onlyInstapyFollowed when use this
session.unfollow_users(amount=10, onlyNotFollowMe=True, sleep_delay=60)

# You can also unfollow users only after following them certain amount of time,
# this will provide seamless unfollow activity without the notice of the targeted user
# To use, just add `unfollow_after` argument with the desired time, e.g.
session.unfollow_users(amount=10, onlyInstapyFollowed = True, onlyInstapyMethod = 'FIFO', sleep_delay=600, unfollow_after=48*60*60)
# will unfollow users only after following them 48 hours (2 days), since `unfollow_after`s value
# is seconds, you can simply give it `unfollow_after=100` to unfollow after 100 seconds,
# but `1*60*60` (which is equal to 1 hour or 3600 seconds) style is a lot simpler to use 👍
```

### Don't unfollow active users

```python
# Prevents unfollow followers who have liked one of your latest 5 posts

session.set_dont_unfollow_active_users(enabled=True, posts=5)
```

### Interactions based on the number of followers and/or following a user has

##### This is used to check the number of _followers_ and/or _following_ a user has and if these numbers _either_ **exceed** the number set OR **does not pass** the number set OR if **their ratio does not reach** desired potency ratio then no further interaction happens
```python
session.set_relationship_bounds(enabled=True,
				 potency_ratio=1.34,
				  delimit_by_numbers=True,
				   max_followers=8500,
				    max_following=4490,
				     min_followers=100,
				      min_following=56)
```
Use `enabled=True` to **activate** this feature, and `enabled=False` to **deactivate** it, _any time_  
`delimit_by_numbers` is used to **activate** & **deactivate** the usage of max & min values  
`potency_ratio` accepts values in **2 format**s _according to your_ **style**: _positive_ & _negative_  
* `potency_ratio` with **POSITIVE** values can be used to _route_ interactions to _only_ **potential** (_real_) **users** _WHOSE_ **followers count** is higher than **following count** (**e.g.**, `potency_ratio = 1.39`)  
_**find** desired_ `potency_ratio` _with this formula_: `potency_ratio` == **followers count** / **following count**  (_use desired counts_)
>_**e.g.**_, target user has _`5000` followers_ & _`4000` following_ and you set `potency_ratio=1.35`.  
**Now** it _will **not** interact_ with this user, **cos** the user's **relationship ratio** is `5000/4000==1.25` and `1.25` is **below** _desired_ `potency_ratio` _of `1.35`_  

* `potency_ratio` with **NEGATIVE** values can be used to _route_ interactions to _only_ **massive followers** _WHOSE_ **following count** is higher than **followers count** (**e.g.**, `potency_ratio = -1.42`)  
_**find** desired_ `potency_ratio` _with this formula_: `potency_ratio` == **following count** / **followers count**  (_use desired counts_)
>_**e.g.**_, target user has _`2000` followers_ & _`3000` following_ and you set `potency_ratio = -1.7`.  
**Now** it _will **not** interact_ with this user, **cos** the user's **relationship ratio** is `3000/2000==1.5` and `1.5` is **below** _desired_ `potency_ratio` _of `1.7`_ (_**note that**, negative `-` sign is only used to determine your style, nothing more_)


###### There are **3** **COMBINATIONS** _available_ to use:
* **1**. You can use `potency_ratio` **or not** (**e.g.**, `potency_ratio=None`, `delimit_by_numbers=True`) - _will decide only by your **pre-defined** max & min values regardless of the_ `potency_ratio`
```python
session.set_relationship_bounds (enabled=True, potency_ratio=None, delimit_by_numbers=True, max_followers=22668, max_following=10200, min_followers=400, min_following=240)
```
* **2**. You can use **only** `potency_ratio` (**e.g.**, `potency_ratio=-1.5`, `delimit_by_numbers=False`) - _will decide per_ `potency_ratio` _regardless of the **pre-defined** max & min values_
```python
session.set_relationship_bounds (enabled=True, potency_ratio=-1.5, delimit_by_numbers=False, max_followers=400701, max_following=90004, min_followers=963, min_following=2310)
```
> apparently, _once_ `delimit_by_numbers` gets `False` value, max & min values _do not matter_
* **3**. You can use both `potency_ratio` and **pre-defined** max & min values **together** (**e.g.**, `potency_ratio=2.35`, `delimit_by_numbers=True`) - _will decide per_ `potency_ratio` _& your **pre-defined** max & min values_
```python
session.set_relationship_bounds (enabled=True, potency_ratio=2.35, delimit_by_numbers=True, max_followers=10005, max_following=24200, min_followers=77, min_following=500)
```

> **All** of the **4** max & min values are _able to **freely** operate_, **e.g.**, you may want to _**only** delimit_ `max_followers` and `min_following` (**e.g.**, `max_followers=52639`, `max_following=None`, `min_followers=None`, `min_following=2240`)
```python
session.set_relationship_bounds (enabled=True, potency_ratio=-1.44, delimit_by_numbers=True, max_followers=52639, max_following=None, min_followers=None, min_following=2240)
```  



### Liking based on the number of existing likes a post has

##### This is used to check the number of existing likes a post has and if it _either_ **exceed** the _maximum_ value set OR **does not pass** the _minimum_ value set then it will not like that post
```python
session.set_delimit_liking(enabled=True, max=1005, min=20)
```
Use `enabled=True` to **activate** and `enabled=False` to **deactivate** it, _any time_  
`max` is the maximum number of likes to compare  
`min` is the minimum number of likes to compare
> You can use **both** _max_ & _min_ values OR **one of them** _as you desire_, just **put** the value of `None` _to the one_ you **don't want to** check for., _e.g._,
```python
session.set_delimit_liking(enabled=True, max=242, min=None)
```
_at this configuration above, it **will not** check number of the existing likes against **minimum** value_

* **_Example_**:  
```
session.set_delimit_liking(enabled=True, max=500, min=7)
```
_**Now**, if a post has more existing likes than maximum value of `500`, then it will not like that post,
**similarly**, if that post has less existing likes than the minimum value of `7`, then it will not like that post..._



### Commenting based on the number of existing comments a post has

##### This is used to check the number of existing comments a post has and if it _either_ **exceed** the _maximum_ value set OR **does not pass** the _minimum_ value set then it will not comment on that post
```python
session.set_delimit_commenting(enabled=True, max=32, min=0)
```
Use `enabled=True` to **activate** and `enabled=False` to **deactivate** it, _any time_  
`max` is the maximum number of comments to compare  
`min` is the minimum number of comments to compare
> You can use **both** _max_ & _min_ values OR **one of them** _as you desire_, just **put** the value of `None` _to the one_ you **don't want to** check for., _e.g._,
```python
session.set_delimit_commenting(enabled=True, max=None, min=4)
```
_at this configuration above, it **will not** check number of the existing comments against **maximum** value_

* **_Example_**:  
```
session.set_delimit_commenting(enabled=True, max=70, min=5)
```
_**Now**, if a post has more comments than the maximum value of `70`, then it will not comment on that post,
**similarly**, if that post has less comments than the minimum value of `5`, then it will not comment on that post..._



### Comment by Locations

```python
session.comment_by_locations(['224442573/salton-sea/'], amount=100)
# or
session.comment_by_locations(['224442573'], amount=100)
# or include media entities from top posts section

session.comment_by_locations(['224442573'], amount=5, skip_top_posts=False)
```

This method allows commenting by locations, without liking posts. To get locations follow instructions in 'Like by Locations'



### Like by Locations

```python
session.like_by_locations(['224442573/salton-sea/'], amount=100)
# or
session.like_by_locations(['224442573'], amount=100)
# or include media entities from top posts section

session.like_by_locations(['224442573'], amount=5, skip_top_posts=False)
```

You can find locations for the `like_by_locations` function by:
- Browsing https://www.instagram.com/explore/locations/
- Regular instagram search.

Example:
* Search 'Salton Sea' and select the result with a location icon
* The url is: https://www.instagram.com/explore/locations/224442573/salton-sea/
* Use everything after 'locations/' or just the number


### Like by Tags

```python
# Like posts based on hashtags
session.like_by_tags(['natgeo', 'world'], amount=10)
```

### Like by Tags and interact with user

```python
# Like posts based on hashtags and like 3 posts of its poster
session.set_user_interact(amount=3, randomize=True, percentage=100, media='Photo')
session.like_by_tags(['natgeo', 'world'], amount=10, interact=True)
```

### Like by Feeds

```python
# This is used to perform likes on your own feeds
# amount=100  specifies how many total likes you want to perform
# randomize=True randomly skips posts to be liked on your feed
# unfollow=True unfollows the author of a post which was considered
# inappropriate interact=True visits the author's profile page of a
# certain post and likes a given number of his pictures, then returns to feed

session.like_by_feed(amount=100, randomize=True, unfollow=True, interact=True)
```

### Blacklist Campaign
```python
# Controls your interactions by campaigns.
# ex. this week InstaPy will like and comment interacting by campaign called
# 'soccer', next time InstaPy runs, it will not interact again with users in
# blacklist
# In general, this means that once we turn off the soccer_campaign again, InstaPy
# will have no track of the people it interacted with about soccer.
# This will help you target people only once but several times for different campaigns

session.set_blacklist(enabled=True, campaign='soccer_campaign')
session.set_do_comment(True, percentage=50)
session.set_comments(['Neymar is better than CR7', 'Soccer is cool'])
session.like_by_tags(['soccer', 'cr7', 'neymar'], amount=100, media='Photo')

```

### Smart Hashtags

```python
# Generate smart hashtags based on https://displaypurposes.com ranking,
# banned and spammy tags are filtered out.
# (limit) defines amount limit of generated hashtags by hashtag
# (sort) sort generated hashtag list 'top' and 'random' are available
# (log_tags) shows generated hashtags before use it
# (use_smart_hashtags) activates like_by_tag to use smart hashtags

session.set_smart_hashtags(['cycling', 'roadbike'], limit=3, sort='top', log_tags=True)
session.like_by_tags(amount=10, use_smart_hashtags=True)
```

### Restricting Likes

```python
session.set_dont_like(['#exactmatch', '[startswith', ']endswith', 'broadmatch'])
```

`.set_dont_like` searches the description and owner comments for hashtags and
won't like the image if one of those hashtags are in there

You have 4 options to exclude posts from your InstaPy session:
* words starting with `#` will match only exact hashtags (e. g. `#cat` matches `#cat`, but not `#catpic`)
* words starting with `[` will match all hashtags starting with your word (e. g. `[cat` matches `#catpic`, `#caturday` and so on)
* words starting with `]` will match all hashtags ending with your word (e. g. `]cat` matches `#mycat`, `#instacat` and so on)
* words without these prefixes will match all hashtags that contain your word regardless if it is placed at the beginning, middle or end of the hashtag (e. g. `cat` will match `#cat`, `#mycat`, `#caturday`, `#rainingcatsanddogs` and so on)

### Ignoring Users

```python
# completely ignore liking images from certain users

session.set_ignore_users(['random_user', 'another_username'])
```

### Ignoring Restrictions

```python
# will ignore the don't like if the description contains
# one of the given words

session.set_ignore_if_contains(['glutenfree', 'french', 'tasty'])
```

### Excluding friends

```python
# will prevent commenting on and unfollowing your good friends (the images will
# still be liked)

session.set_dont_include(['friend1', 'friend2', 'friend3'])
```

### Follow/Unfollow/exclude not working?
If you notice that one or more of the above functionalities are not working as expected - e.g. you have specified:
```python
session.set_do_follow(enabled=True, percentage=10, times=2)
```
but none of the profiles are being followed - or any such functionality is misbehaving - then one thing you should check is the position/order of such methods in your script. Essentially, all the ```set_*``` methods have to be before ```like_by_tags``` or ```like_by_locations``` or ```unfollow```. This is also implicit in all the exmples and quickstart.py

### Bypass Suspicious Login Attempt

If you're having issues with the "we detected an unusual login attempt" message,
you can bypass it setting InstaPy in this way:

```python
session = InstaPy(username=insta_username, password=insta_password, bypass_suspicious_attempt=True)
```

```bypass_suspicious_attempt=True``` will send the verification code to your
email, and you will be prompted to enter the security code sent to your email.
It will login to your account, now you can set bypass_suspicious_attempt to False
```bypass_suspicious_attempt=False``` and InstaPy will quickly login using cookies.

### Use a proxy

You can use InstaPy behind a proxy by specifying server address and port

```python
session = InstaPy(username=insta_username, password=insta_password, proxy_address='8.8.8.8', proxy_port=8080)
```

To use proxy with authentication you should firstly generate proxy chrome extension (works only with Chrome and headless_browser=False).

```python
from proxy_extension import create_proxy_extension

proxy = 'login:password@ip:port'
proxy_chrome_extension = create_proxy_extension(proxy)

session = InstaPy(username=insta_username, password=insta_password, proxy_chrome_extension=proxy_chrome_extension, nogui=True)
```

### Switching to Firefox

Chrome is the default browser, but InstaPy provides support for Firefox as well.

```python
session = InstaPy(username=insta_username, password=insta_password, use_firefox=True)
```

### Emoji Support
To use an emoji just add an `u` in front of the opening apostrophe:

```
session.set_comments([u'This post is 🔥',u'More emojis are always better 💯',u'I love your posts 😍😍😍']);
# or
session.set_comments([u'Emoji text codes are also supported :100: :thumbsup: :thumbs_up: \u2764 💯💯']);
```

Emoji text codes are implemented using 2 different naming codes. A complete list of emojis codes can be found on the [Python Emoji Github](https://github.com/carpedm20/emoji/blob/master/emoji/unicode_codes.py), but you can use the alternate shorted naming scheme found for Emoji text codes [here](https://www.webpagefx.com/tools/emoji-cheat-sheet). Note: Every Emoji has not been tested. Please report any inconsistencies.

> **Legacy Emoji Support**
>
> You can still use Unicode strings in your comments, but there are some limitations.
> 1. You can use only Unicode characters with no more than 4 characters and you have to use the unicode code (e. g. ```\u1234```). You find a list of emoji with unicode codes on [Wikipedia](https://en.wikipedia.org/wiki/Emoji#Unicode_blocks), but there is also a list of working emoji in ```/assets```
>
> 2. You have to convert your comment to Unicode. This can safely be done by adding an u in front of the opening apostrophe: ```u'\u1234 some comment'```

## Clarifai ImageAPI

<img src="https://d1qb2nb5cznatu.cloudfront.net/startups/i/396673-2fb6e8026b393dddddc093c23d8cd866-medium_jpg.jpg?buster=1399901540" width="200" align="right">

###### Note: Head over to [https://developer.clarifai.com/signup/](https://developer.clarifai.com/signup/) and create a free account, once you’re logged in go to [https://developer.clarifai.com/account/applications/](https://developer.clarifai.com/account/applications/) and create a new application. You can find the client ID and Secret there. You get 5000 API-calls free/month.

If you want the script to get your CLARIFAI_API_KEY for your environment, you can do:

```
export CLARIFAI_API_KEY="<API KEY>"
```
### Example with Imagecontent handling

```python
session.set_do_comment(True, percentage=10)
session.set_comments(['Cool!', 'Awesome!', 'Nice!'])
session.set_use_clarifai(enabled=True)
session.clarifai_check_img_for(['nsfw'])
session.clarifai_check_img_for(['food', 'lunch', 'dinner'], comment=True, comments=['Tasty!', 'Nice!', 'Yum!'])

session.end()
```
### Enabling Imagechecking

```python
# default enabled=False , enables the checking with the clarifai api (image
# tagging) if secret and proj_id are not set, it will get the environment
# variables 'CLARIFAI_API_KEY'

session.set_use_clarifai(enabled=True, api_key='xxx')
```
### Filtering inappropriate images

```python
# uses the clarifai api to check if the image contains nsfw content
# -> won't comment if image is nsfw

session.clarifai_check_img_for(['nsfw'])
```
### Specialized comments for images with specific content

```python
# checks the image for keywords food and lunch, if both are found,
# comments with the given comments. If full_match is False (default), it only
# requires a single tag to match Clarifai results.

session.clarifai_check_img_for(['food', 'lunch'], comment=True, comments=['Tasty!', 'Yum!'], full_match=True)
```

###### Check out [https://clarifai.com/demo](https://clarifai.com/demo) to see some of the available tags.</h6>

## Running on a Server

Use the `nogui` parameter to interact with virtual display

```
session = InstaPy(username='test', password='test', nogui=True)
```

## Running on a Headless Browser

**Note:** Chrome only! Must user chromedriver v2.9+

Use `headless_browser` parameter to run the bot via the CLI. Works great if running the scripts locally, or to deploy on a server. No GUI, less CPU intensive. [Example](http://g.recordit.co/BhEgXANLhJ.gif)

```
session = InstaPy(username='test', password='test', headless_browser=True)
```

## Running Multiple Accounts

Use the multi_logs parameter if you are going to use multiple accounts and want the log files stored per account.
```
session = InstaPy(username='test', password='test', multi_logs=True)
```

## Running with Docker microservices manual

Docker allows very easy and fast run of the instapy bot without any pain and tears.

### 0. Preparations

Install docker from the official website [https://www.docker.com/](https://www.docker.com/)

Install VNC viewer if you do not have one. For windows, a good program is  [http://www.tightvnc.com/](http://www.tightvnc.com/)

### 1. Set your instagram login and password

Open `docker_quickstart.py` and fill the quotes after insta_username and insta_password with your credentials.

Don't forget to make other changes for the file as you want to. Read the documentation above for info.

### 2. Run and build containers with docker-compose

First you need to open your terminal, move to the root folder (usually with the `cd` command) of instapy project and then type:
```bash
docker-compose up -d --build
```

That's all! At this step, you are already successfully running your personal bot!

### 3. See what your bot can do right now

Run your VNC viewer, and type address and port `localhost:5900`. The password is `secret`.

### 4. Stop your instapy bot

Use your terminal again, type in the same window:
```bash
docker-compose down
```

Your bot is stopped!

### 5. Further steps

Those are just basic steps to run instapy bot on your PC with docker. There are other docker-compose settings file in the root of project.

#### Development environment to run, test and debug by SSH

Use it to help us with development and test instapy! `docker-dev.yml` file.

```bash
docker-compose -f docker-dev.yml up -d
```

After striking this command, you can access your bot by VNC on the adress  `localhost:5901`, the password is `secret`.

But there is more! There is a fully accessible bash console with all code mounted at the path `/code`. When you hack some files they are dynamically updated inside your container.

To access yor container console to run bot type `localhost:22` in your favorite ssh client. The User is `root` and the password is `root` also.

#### Run in production without opened VNC port

 Suitable to run in a remote server. Attention! You can not view what happened through VNC on this configuration `docker-prod.yml` file.

```bash
docker-compose -f docker-prod.yml up -d
```

## Running all-in-one with Docker (obsolete)

### 1. Build the Image

First you need to build the image by running this in the Terminal:
```bash
docker build -t instapy ./docker_conf/all_in_one
```

Make sure to use the `nogui` feature:
```python
# you can use the nogui parameter to use a virtual display

session = InstaPy(username='test', password='test', nogui=True)
```

### 2. Run in a Container

After the build succeeds, you can simply run the container with:
```bash
docker run --name=instapy -e INSTA_USER=<your-user> -e INSTA_PW=<your-pw> -d --rm instapy
```

## Automate InstaPy

### [Windows Task Scheduler](https://msdn.microsoft.com/en-us/library/windows/desktop/aa383614(v=vs.85).aspx)

You can use Window's built in Task Scheduler to automate InstaPy, using a variety of trigger types: time, login, computer idles, etc. To schedule a simple daily run of an Instapy script follow the below directions
1. Open [Windows Task Scheduler](https://msdn.microsoft.com/en-us/library/windows/desktop/aa383614(v=vs.85).aspx)
2. Select "Create Basic Task"
3. Fill out "Name" and "Description" as desired, click "Next"
4. On "Trigger" screen select how frequently to run, click "Next" (Frequency can be modified later)
5. On "Daily" screen, hit "Next"
6. "Action Screen" select "Start a program" and then click "Next"
7. "Program/script" enter the path, or browse to select the path to python. ([How to find python path on Windows](https://stackoverflow.com/questions/647515/how-can-i-get-python-path-under-windows))
8. "Add arguments" input the InstaPy script path you wish to run. (Example: C:\Users\USER_NAME\Documents\GitHub\InstaPy\craigquick.py)
9. "Start in" input Instapy install location (Example: C:\Users\USER_NAME\Documents\GitHub\InstaPy\). Click "Next"
10. To finish the process, hit "Finish"



### `cron`

You can add InstaPy to your crontab, so that the script will be executed regularly. This is especially useful for servers, but be sure not to break Instagrams follow and like limits.

```
# Edit or create a crontab
crontab -e
# Add information to execute your InstaPy regularly.
# With cd you navigate to your InstaPy folder, with the part after &&
# you execute your quickstart.py with python. Make sure that those paths match
# your environment.
45 */4 * * * cd /home/user/InstaPy && /usr/bin/python ./quickstart.py
```

### [Schedule](https://github.com/dbader/schedule)

> Schedule is an in-process scheduler for periodic jobs that uses the builder pattern for configuration. Schedule lets you run Python functions periodically at pre-determined intervals using a simple, human-friendly syntax.

```shell
pip install schedule
```

```python
from instapy import InstaPy
import schedule
import time

def job():
    try:
        session = InstaPy(selenium_local_session=False) # Assuming running in Compose
        session.set_selenium_remote_session(selenium_url='http://selenium:4444/wd/hub')
        session.login()
        session.set_do_comment(enabled=True, percentage=20)
        session.set_comments(['Well done!'])
        session.set_do_follow(enabled=True, percentage=5, times=2)
        session.like_by_tags(['love'], amount=100, media='Photo')
        session.end()
    except:
        import traceback
        print(traceback.format_exc())

schedule.every().day.at("6:35").do(job)
schedule.every().day.at("16:22").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
```

## Extra Informations

#### How not to be banned ?
Built-in delays prevent your account from getting banned. (Just make sure you don't like 1000s of post/day)

### Chrome Browser

64-bit system is a requirement for current versions of chrome browser.

---
###### Have Fun & Feel Free to report any issues
---
