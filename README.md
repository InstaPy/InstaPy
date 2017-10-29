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

**Have an issue**
Head over to https://github.com/timgrossmann/InstaPy/wiki/Reporting-An-Issue to find out how to report this to us and get help.

**Disclaimer**: Please Note that this is a research project. I am by no means responsible for any usage of this tool. Use on your own behalf. I’m also not responsible if your accounts get banned due to extensive use of this tool.

#### Newsletter: [SignUp for the Newsletter here!](http://eepurl.com/cZbV_v)

### Social

#### [Slack Workspace](https://join.slack.com/t/instapy/shared_invite/enQtMjYzNTgwMDg3MDEyLTk2NWI0MjY2MTVjYmM2NjFlYjVmMmE0ZjU1OGQ0OWM2MTQwOTc1NTIyOGVhZDEwMTFkYzFmODE5ZWIxZjhjMTQ) | [InstaPy Twitter](https://twitter.com/InstaPy) | [My Twitter](https://twitter.com/timigrossmann) | [How it works (Medium)](https://medium.freecodecamp.com/my-open-source-instagram-bot-got-me-2-500-real-followers-for-5-in-server-costs-e40491358340) | [Check out the talk](https://youtu.be/4TmKFZy-ioQ) | [Support InstaPy!](https://www.paypal.me/supportInstaPy)

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
  * [Follow someone else's followers/following](#follow-someone-elses-followers/following)
  * [Interact with specific users](#interact-with-specific-users)
  * [Interact with users that someone else is following](#interact-with-users-that-someone-else-is-following)
  * [Interact with someone else's followers](#interact-with-someone-elses-followers)
  * [Unfollowing](#unfollowing)
  * [Prevents unfollow active users](#prevents-unfollow-active-users)
  * [Interactions based on the number of followers a user has](#interactions-based-on-the-number-of-followers-a-user-has)
  * [Like by Locations](#like-by-locations)
  * [Like by Tags](#like-by-tags)
  * [Like by Feeds](#like-by-feeds)
  * [Restricting Likes](#restricting-likes)
  * [Ignoring Users](#ignoring-users)
  * [Ignoring Restrictions](#ignoring-restrictions)
  * [Excluding friends](#excluding-friends)
  * [Blacklist](#blacklist)
  * [Follow/Unfollow/exclude not working?](#followunfollowexclude-not-working)
* [Third Party InstaPy GUI for Windows](#third-party-instapy-gui-for-windows)
* [Switching to Firefox](#switching-to-firefox)
* [Emoji Support](#emoji-support)
* [Clarifai ImageAPI](#clarifai-imageapi)
* [Running on a Server](#running-on-a-server)
* [Running with Docker microservices manual](#running-with-docker-microservices-manual)
* [Running all-in-one with Docker (obsolete)](#running-all-in-one-with-docker-obsolete)
* [Automate with cron](#automate-with-cron)
* [Automate with Schedule](#automate-with-schedule)
* [Extra Informations](#extra-informations)

## Getting started

### Video tutorials:
**[Setting up InstaPy for OSX](https://www.youtube.com/watch?v=I025CEBJCvQ)**

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
4. Download ```chromedriver``` for your system [from here](https://sites.google.com/a/chromium.org/chromedriver/downloads). And put it in ```/assets``` folder.


### Basic Setup

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
session.set_upper_follower_count(limit=2500)
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

## InstaPy Available Features

### Commenting

```python
# default enabled=False, ~ every 4th image will be commented on

session.set_do_comment(enabled=True, percentage=25)
session.set_comments(['Awesome', 'Really Cool', 'I like your stuff'])

# you can also set comments for specific media types (Photo / Video)

session.set_comments(['Nice shot!'], media='Photo')
session.set_comments(['Great Video!'], media='Video')
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
# If random is false it will pick in a top-down fashion

session.follow_user_followers(['friend1', 'friend2', 'friend3'], amount=10, random=False)

# default sleep_delay=600 (10min) for every 10 user following, in this case
# sleep for 60 seconds  

session.follow_user_followers(['friend1', 'friend2', 'friend3'], amount=10, random=False, sleep_delay=60)
```

### Follow users that someone else is following

```python
# Follows the people that a given users are following
# The usernames can be either a list or a string
# The amount is for each account, in this case 30 users will be followed
# If random is false it will pick in a top-down fashion

session.follow_user_following(['friend1', 'friend2', 'friend3'], amount=10, random=False)

# default sleep_delay=600 (10min) for every 10 user following, in this case
# sleep for 60 seconds

session.follow_user_following(['friend1', 'friend2', 'friend3'], amount=10, random=False, sleep_delay=60)
```

### Follow someone else's followers/following

```python
# For 50% of the 30 newly followed, move to their profile
# and randomly choose 5 pictures to be liked.
# Take into account the other set options like the comment rate
# and the filtering for inappropriate words or users

session.set_user_interact(amount=5, random=True, percentage=50, media='Photo')
session.follow_user_followers(['friend1', 'friend2', 'friend3'], amount=10, random=False, interact=True)
```

### Interact with specific users
```python
# Interact with specific users
# set_do_like, set_do_comment, set_do_follow are applicable

session.set_do_follow(enabled=False, percentage=50)
session.set_comments(["Cool", "Super!"])
session.set_do_comment(enabled=True, percentage=80)
session.set_do_like(True, percentage=70)
session.interact_by_users(['user1', 'user2', 'user3'], amount=5, random=True, media='Photo')
```

### Interact with users that someone else is following
```python
# Interact with the people that a given user is following
# set_do_comment, set_do_follow and set_do_like are applicable

session.set_user_interact(amount=5, random=True, percentage=50, media='Photo')
session.set_do_follow(enabled=False, percentage=70)
session.set_do_like(enabled=False, percentage=70)
session.set_comments(["Cool", "Super!"])
session.set_do_comment(enabled=True, percentage=80)
session.interact_user_following(['natgeo'], amount=10, random=True)
```

### Interact with someone else's followers
```python
# Interact with the people that a given user is following
# set_do_comment, set_do_follow and set_do_like are applicable

session.set_user_interact(amount=5, random=True, percentage=50, media='Photo')
session.set_do_follow(enabled=False, percentage=70)
session.set_do_like(enabled=False, percentage=70)
session.set_comments(["Cool", "Super!"])
session.set_do_comment(enabled=True, percentage=80)
session.interact_user_followers(['natgeo'], amount=10, random=True)
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
```

### Prevents unfollow active users

```python
# Prevents unfollow followers who have liked one of your latest 5 posts

session.set_unfollow_active_users(enabled=False, posts=5)
```

### Interactions based on the number of followers a user has

```python
# This is used to check the number of followers a user has and if this number 
# exceeds the number set then no further interaction happens

session.set_upper_follower_count(limit = 250)
```

```python
# This is used to check the number of followers a user has and if this number
# does not pass the number set then no further interaction happens

session.set_lower_follower_count(limit = 1)
```

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

### Like by Feeds

```python
# This is used to perform likes on your own feeds
# amount=100  specifies how many total likes you want to perform
# random=True randomly skips posts to be liked on your feed
# unfollow=True unfollows the author of a post which was considered 
# inappropriate interact=True visits the author's profile page of a 
# certain post and likes a given number of his pictures, then returns to feed

session.like_by_feed(amount=100, randomize=True, unfollow=True, interact=True)
```

### Restricting Likes

```python
session.set_dont_like('#exactmatch', '[startswith', ']endswith', 'broadmatch')
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

### Blacklist

```python
# If enabled=True, after interact (liked or followed) the user will be stored in
# the blacklist. Users in the blacklist will not be liked or followed.

session.set_blacklist(enabled=True)
```

### Follow/Unfollow/exclude not working?
If you notice that one or more of the above functionalities are not working as expected - e.g. you have specified:
```python
session.set_do_follow(enabled=True, percentage=10, times=2)
```
but none of the profiles are being followed - or any such functionality is misbehaving - then one thing you should check is the position/order of such methods in your script. Essentially, all the ```set_*``` methods have to be before ```like_by_tags``` or ```like_by_locations``` or ```unfollow```. This is also implicit in all the exmples and quickstart.py


## Third Party InstaPy GUI for Windows

**[1. Official Cross Platform GUI](https://github.com/ahmadudin/electron-instaPy-GUI)**

[<img src="https://raw.githubusercontent.com/ahmadudin/ahmadudin.github.io/master/assets/images/screencapture1.PNG" width="400" />](https://github.com/ahmadudin/electron-instaPy-GUI)

[2. Third Party InstaPy GUI for Windows](https://github.com/Nemixalone/GUI-tool-for-InstaPy-script)


## Switching to Firefox

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

## Automate with `cron`

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

## Automate with [Schedule](https://github.com/dbader/schedule)

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

