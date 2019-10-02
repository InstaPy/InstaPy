# Documentation

### Table of Contents
- **[Settings](#settings)**
  - [Liking](#liking)
  - [Commenting](#commenting)
  - [Emoji Support](#emoji-support)
  - [Following](#following)
  - [Smart Hashtags](#smart-hashtags)
  - [Smart Location Hashtags](#smart-location-hashtags)
  - [Quota Supervisor](#quota-supervisor)
  - [Restricting Likes](#restricting-likes)
  - [Ignoring Restrictions](#ignoring-restrictions)
  - [Ignoring Users](#ignoring-users)
  - [Excluding friends](#excluding-friends)
  - [Mandatory Words](#mandatory-words)
  - [Mandatory Language](#mandatory-language)
  - [Don't unfollow active users](#dont-unfollow-active-users)
  - [Blacklist Campaign](#blacklist-campaign)
  - [Simulation](#simulation)
  - [Skipping user for private account, no profile picture, business account](#skipping-user-for-private-account-no-profile-picture-business-account)
  - [Liking based on the number of existing likes a post has](#liking-based-on-the-number-of-existing-likes-a-post-has)
  - [Commenting based on the number of existing comments a post has](#commenting-based-on-the-number-of-existing-comments-a-post-has)
  - [Commenting based on mandatory words in the description or first comment](#commenting-based-on-mandatory-words-in-the-description-or-first-comment)
  - [Interactions based on the number of followers and/or following a user has](#interactions-based-on-the-number-of-followers-andor-following-a-user-has)
  - [Interactions based on the number of posts a user has](#interactions-based-on-the-number-of-posts-a-user-has)
  - [Custom action delays](#custom-action-delays)
  
 <br />

- **[Actions](#actions)**
  - [Like by Tags](#like-by-tags)
  - [Like by Feeds](#like-by-feeds)
  - [Like by Locations](#like-by-locations)
  - [Comment by Locations](#comment-by-locations)
  - [Follow by Tags](#follow-by-tags)
  - [Follow by Locations](#follow-by-locations)
  - [Following by a list](#following-by-a-list)
  - [Follow someone else's followers](#follow-someone-elses-followers)
  - [Follow users that someone else is following](#follow-users-that-someone-else-is-following)
  - [Follow and interact someone else's followers/following](#follow-and-interact-someone-elses-followersfollowing)  
  - [Follow the likers of photos of users](#follow-the-likers-of-photos-of-users)  
  - [Follow the commenters of photos of users](#follow-the-commenters-of-photos-of-users)  
  - [Unfollowing](#unfollowing)
  - [Interact on posts at given URLs](#interact-on-posts-at-given-urls)
  - [Interact with specific users](#interact-with-specific-users)
  - [Interact with specific users' tagged posts](#interact-with-specific-users-tagged-posts)
  - [Interact with someone else's followers](#interact-with-someone-elses-followers)
  - [Interact with users that someone else is following](#interact-with-users-that-someone-else-is-following)
  - [Interact by Comments](#interact-by-comments)
  - [Accept pending follow requests](#accept-pending-follow-requests)
  - [Remove outgoing follow requests](#remove-outgoing-follow-requests)
  - [Skip based on Profile Bio](#skip-based-on-profile-bio)
  - [InstaPy Pods](#instapy-pods)
  - [InstaPy Stories](#instapy-stories)
  
 <br />

- **[Third Party features](#third-party-features)**
  - [Clarifai ImageAPI](#clarifai-imageapi)
  - [Text Analytics](#text-analytics)
    - [Yandex Translate API](#yandex-translate-api)
    - [MeaningCloud Sentiment Analysis API](#meaningcloud-sentiment-analysis-api)
  - [Integration with Telegram](#telegram-integration)
 <br />

- **[Instance Settings](#instance-settings)**
  - [Running on a Headless Browser](#running-on-a-headless-browser)
  - [Bypass Suspicious Login Attempt](#bypass-suspicious-login-attempt)
  - [Use a proxy](#use-a-proxy)
  - [Running in threads](#running-in-threads)
  
 <br />

- **[Relationship tools](#relationship-tools)**
  - [Grab Followers of a user](#grab-followers-of-a-user)
  - [Grab Following of a user](#grab-following-of-a-user)
  - [Pick Unfollowers of a user](#pick-unfollowers-of-a-user)
  - [Pick Nonfollowers of a user](#pick-nonfollowers-of-a-user)
  - [Pick Fans of a user](#pick-fans-of-a-user)
  - [Pick Mutual Following of a user](#pick-mutual-following-of-a-user)

 <br />

- **[Automate InstaPy](#automate-instapy)**
  - [Windows Task Scheduler](#windows-task-scheduler)
  - [cron](#cron)
  - [Schedule](#schedule)  
  
 <br />

- **[Additional Information](#additional-information)**
  - [Advanced Installation](#advanced-installation)
  - [Workspace folders](#workspace-folders)
  - [Pass arguments by CLI](#pass-arguments-by-cli)
  - [Extensions](#extensions)
  - [Custom geckodriver](#custom-geckodriver)
  - [Using one of the templates](#using-one-of-the-templates)
  - [How not to be banned](#how-not-to-be-banned)
  - [Disable Image Loading](#disable-image-loading)
  - [Changing DB location](#changing-db-location)
  - [Split SQLite DB by Username](#split-sqlite-by-username)
  - [How to avoid _python_ & pip confusion](#how-to-avoid-python--pip-confusion)
  - [Dealing with Selenium Common Exception Issues](#dealing-with-selenium-common-exception-issues)

---

<br /> 
<br />

## Settings
### Liking
This method is only needed for the `interact_by_...` actions.   
Posts will liked by default when using `like_by_...` actions.

```python
# ~70% of the by InstaPy viewed posts will be liked

session.set_do_like(enabled=True, percentage=70)
```


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


### Emoji Support
To use an emoji just add an `u` in front of the opening apostrophe:

```python
session.set_comments([u'This post is 🔥',u'More emojis are always better 💯',u'I love your posts 😍😍😍']);
# or
session.set_comments([u'Emoji text codes are also supported :100: :thumbsup: :thumbs_up: \u2764 💯💯']);
```

Emoji text codes are implemented using 2 different naming codes. A complete list of emojis codes can be found on the [Python Emoji Github](https://github.com/carpedm20/emoji/blob/master/emoji/unicode_codes.py), but you can use the alternate shorted naming scheme found for Emoji text codes [here](https://www.webpagefx.com/tools/emoji-cheat-sheet). Note: Every Emoji has not been tested. Please report any inconsistencies.


### Following

```python
# default enabled=False, follows ~ 10% of the users from the images, times=1
# (only follows a user once (if unfollowed again))

session.set_do_follow(enabled=True, percentage=10, times=2)
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


### Smart Location Hashtags
 Generate smart hashtags based on https://displaypurposes.com/map ranking.
 Banned and spammy tags are filtered out.

  ```python
 Use_smart_location_hashtags activates like_by_tag to use smart hashtags

 session.set_smart_location_hashtags(['204517928/chicago-illinois', '213570652/nagoya-shi-aichi-japan'], radius=20, limit=10)
 session.like_by_tags(amount=10, use_smart_location_hashtags=True)
  ```

  #### Parameters
 `radius`: Radius around the location in Miles   
 `limit`: Defines amount limit of generated hashtags by hashtag   
 `log_tags`: Shows generated hashtags before use it (default is True)   


### Quota Supervisor
###### Take full control of the actions with the most sophisticated approaches

```python
session.set_quota_supervisor(enabled=True, sleep_after=["likes", "comments_d", "follows", "unfollows", "server_calls_h"], sleepyhead=True, stochastic_flow=True, notify_me=True,
                              peak_likes_hourly=57,
                              peak_likes_daily=585,
                               peak_comments_hourly=21,
                               peak_comments_daily=182,
                                peak_follows_hourly=48,
                                peak_follows_daily=None,
                                 peak_unfollows_hourly=35,
                                 peak_unfollows_daily=402,
                                  peak_server_calls_hourly=None,
                                  peak_server_calls_daily=4700)
```
#### Parameters:
`enabled`: put `True` to **activate** or `False` to **deactivate** supervising any time


If you **don't want to** _supervise_ likes **at all**, simply **remove** `peak_likes` parameter **OR** use `peak_likes=(None, None)`.  
_Once_ likes **reach** peak, it will **jump** every other like, _yet_, **will do all available actions** (_e.g. follow or unfollow_).  
+ Only `server calls` **does not** jump, it exits the program **once reaches the peak**.
> Although, you can put server calls to sleep once reaches peak, read `sleep_after` parameter.  
+ _Every action_ will be **jumped** separately after reaching it's peak, _except_ comments. Cos commenting without a like isn't welcomed that's why as like peak is reached, it will jump comments, too.

`sleep_after`: is used to put **InstaPy** to _sleep_ **after reaching peak** _rather than_ **jumping the action** (_or exiting- **for** server calls_)  
_Any action_ can be included `["likes", "comments", "follows", "unfollows", "server_calls"]`.  
_As if_ you want to put _sleep_ **only after** reaching **hourly** like peak, put `"likes_h"` **OR** put `"likes_d"` for _sleeping_ **only after** reaching **daily** like peak.  
_such as_,
+ `sleep_after=['follows_h']` will _sleep_ after reaching **hourly** follow peak  
+ `sleep_after=['likes_d', 'follows', 'server_calls_h']` will _sleep_ after reaching **daily** like peak, follow peaks (_**hourly** and **daily**_) and **hourly** server call peak.  

**Notice**: there can be _either_ `"likes"` (_for both **hourly** and **daily** sleep_) **OR** `"likes_h"` (_for **hourly** sleep only_) **OR** `"likes_d"` (_for **daily** sleep only_).  
>_Once_ gone to sleep, it will **wake up** as _new_ **hour**/**day** (_according to the interval_) arrives AND **continue** the activity.


`sleepyhead`: can help to _sound_ **more humanly** which will **wake up a little bit later** in a randomly chosen time interval around accurate wake up time.
>_e.g._, if remaining time is `17` minutes, it will sleep `20` minutes instead (_random values each time_)..


`stochastic_flow`: can provide _smooth_ peak value generation by your original values.  
+ Every ~**hour**/**day** it will generate peaks **at close range** _around_ your **original peaks** (_but below them_).  
> _e.g._, your peak likes **hourly** is `45`, next hour that peak will be `39`, the next `43`, etc.


`notify_me`: sends **toast notifications** (_directly to your OS_) _about_ the **important states of** _supervisor_- **sleep**, **wake up** and **exit** messages.

#### Mini-Examples:
+ Claudio has written **a new 😊 quickstart** script where it **mostly** _put likes and comments_. He wants the program to **comment safely** cos he is _afraid of exceeding_ **hourly** & **daily** comment limits,
```python
session.set_quota_supervisor(enabled=True, peak_comments_daily=21, peak_comments_hourly=240)
```
>_That's it! When it reaches the comments peak, it will just jump all of the comments and will again continue to put comments when is available [in the next  hour/day]_.

+ Alicia has a **24**/**7** 🕦 working **quickstart** script and **would like to** keep _server calls_ in control to AVOID **excessive amount of requests** to the _server_ in **hourly** basis, also,
    + **wants** the program to **sleep after** reaching **hourly** _server calls_ peak: **adds** `"server_calls_h"` into `sleep_after` parameter
    + **wants** the program to **wake up** _a little bit later_ than real sleep time [once reaches the peaks]: **uses** `sleepyhead=True` parameter
```python
session.set_quota_supervisor(enabled=True, peak_server_calls_daily=490, sleep_after=["server_calls_h"], sleepyhead=True)
```
>_It will sleep after **hourly** server calls reaches its peak given - `490` and **never allow** one more extra request to the server out of the peak and **wake up** when **new hour** comes in WHILST **daily** server calls **will not be** supervised at all- as Alicia wishes_.

+ Sam has a _casual_ 🦆 **quickstart** script full of _follow_/_unfollow_ features and he wants to **do it safely**, also,
    + is **gonna** run on local computer and **wants** to receive **toast notifications** 😋 on _supervising states_: **uses** `notify_me` parameter
    + **wants** QS to _randomize_ his `pre-defined` peak values [at close range] each new _hour_/_day_: **uses** `stochastic_flow=True` parameter
    + **wants** the program to sleep after reaching **hourly** _follow_ peak and **daily** _unfollow_ peak: **adds** `"follows_h"` and `"unfollows_d"`into `sleep_after` parameter
```python
session.set_quota_supervisor(enabled=True, peak_follows_daily=560, peak_follows_hourly=56, peak_unfollows_hourly=49, peak_unfollows_daily=550, sleep_after=["follows_h", "unfollows_d"], stochastic_flow=True, notify_me=True)
```

---
>**Big Hint**: _Find your NEED_ 🤔 _and supervise it!_  
+ _EITHER_ **fully** configure QS to supervise **all** of the _actions_ all time  
+ _OR_ **just** supervise the desired _action_(_s_) in desired _interval_(_s_) [**hourly** and/or **daily**] per your need


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


### Ignoring Restrictions

```python
# will ignore the don't like if the description contains
# one of the given words

session.set_ignore_if_contains(['glutenfree', 'french', 'tasty'])
```


### Ignoring Users

```python
# completely ignore liking images from certain users

session.set_ignore_users(['random_user', 'another_username'])
```


### Excluding friends

```python
# will prevent commenting on and unfollowing your good friends (the images will
# still be liked)

session.set_dont_include(['friend1', 'friend2', 'friend3'])
```


### Mandatory Words

```python
session.set_mandatory_words(['#food', '#instafood'])
```

`.set_mandatory_words` searches the description, location and owner comments for words and
will like the image if **any** of those words are in there

### Mandatory Language

```python
session.set_mandatory_language(enabled=True, character_set=['LATIN'])
session.set_mandatory_language(enabled=True, character_set=['LATIN', 'CYRILLIC'])
```

`.set_mandatory_language` restrict the interactions, liking and following if any character of the description is outside of the character sets you selected (the location is not included and non-alphabetic characters are ignored). For example if you choose `LATIN`, any character in Cyrillic will flag the post as inappropriate. If you choose 'LATIN' and 'CYRILLIC', any other character sets will flag the post as inappropriate as well.

* Available character sets: `LATIN`,  `GREEK`, `CYRILLIC`, `ARABIC`, `HEBREW`, `CJK`, `HANGUL`, `HIRAGANA`, `KATAKANA` and `THAI`


### Don't unfollow active users

```python
# Prevents unfollow followers who have liked one of your latest 5 posts

session.set_dont_unfollow_active_users(enabled=True, posts=5)
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


### Simulation  
##### During indirect data retrieval, **simulation** happens to provide a _genuine_ activity flow triggered by a wise algorithm.  
To **turn off** simulation or to **decrease** its occurrence frequency, use `set_simulation` setting:  
```python
#use the value of `False` to permanently turn it off
session.set_simulation(enabled=False)

#use a desired occurrence percentage
session.set_simulation(enabled=True, percentage=66)
```


### Skipping user for private account, no profile picture, business account

#### This is used to skip users with certain condition
```python
session.set_skip_users(skip_private=True,
                       private_percentage=100,
                       skip_no_profile_pic=False,
                       no_profile_pic_percentage=100,
                       skip_business=False,
		       skip_non_business=False,
                       business_percentage=100,
                       skip_business_categories=[],
                       dont_skip_business_categories=[])
```
##### Skip private account
**This is done by default**
```python
session.set_skip_users(skip_private=True,
                       private_percentage=100)
```
Will skip users that have private account, even if are followed by running account.
You can set a percentage of skipping:
    _private_percentage_= 100 always skip private users
    _private_percentage_= 0 never skip private users (so set skip_private=False)

##### Skip users that don't have profile picture

```python
session.set_skip_users(skip_private=True,
                       skip_no_profile_pic=True,
                       no_profile_pic_percentage=100)
```
Will skip users that haven't uploaded yet a profile picture
You can set a percentage of skipping:
    _no_profile_pic_percentage_= 100 always skip users without profile picture
    _no_profile_pic_percentage_= 0 never skip users without profile picture (so set _skip_no_profile_pic_=False)

##### Skip users that have business account

```python
session.set_skip_users(skip_private=True,
                       skip_no_profile_pic=True,
		               skip_business=True,
		               business_percentage=100)
```
This will skip all users that have business account activated.
You can set a percentage of skipping:
    _business_percentage_= 100 always skip business users
    _business_percentage_= 0 never skip business users (so set _skip_business_=False)

**N.B.:** This _business_percentage_ parameter works only if no _skip_business_categories_ or _dont_skip_business_categories_ are provided!

###### Skip only users that have certain business account
```python
session.set_skip_users(skip_private=True,
                       skip_no_profile_pic=True,
		       skip_business=True,
		       skip_business_categories=['Creators & Celebrities'])
```
This will skip all business accounts that have category in given list
**N.B.** In _skip_business_categories_ you can add more than one category

###### Skip all business accounts, except from list given
```python
session.set_skip_users(skip_private=True,
                       skip_no_profile_pic=True,
		       skip_business=True,
		       dont_skip_business_categories=['Creators & Celebrities'])
```
This will skip all business accounts except the ones that have a category that matches one item in the list of _dont_skip_business_categories_
**N.B.** If both _dont_skip_business_categories_ and _skip_business_categories_, InstaPy will skip only business accounts in the list given from _skip_business_categories_.

> [A list of all availlable business categories can be found here](https://github.com/InstaPy/instapy-docs/blob/master/BUSINESS_CATEGORIES.md)

###### Skip all non business and bussines accounts, except from list given
 ```python
 session.set_skip_users(skip_private=True,
                        skip_no_profile_pic=True,
                        skip_business=True,
                        skip_non_business=True,
                        dont_skip_business_categories=['Creators & Celebrities'])
 ```
 Thiw will skip all non business and business accounts except categories in _dont_skip_business_categories_.

### Liking based on the number of existing likes a post has
##### This is used to check the number of existing likes a post has and if it _either_ **exceed** the _maximum_ value set OR **does not pass** the _minimum_ value set then it will not like that post
```python
session.set_delimit_liking(enabled=True, max_likes=1005, min_likes=20)
```
Use `enabled=True` to **activate** and `enabled=False` to **deactivate** it, _any time_  
`max` is the maximum number of likes to compare  
`min` is the minimum number of likes to compare
> You can use **both** _max_ & _min_ values OR **one of them** _as you desire_, just **put** the value of `None` _to the one_ you **don't want to** check for., _e.g._,
```python
session.set_delimit_liking(enabled=True, max_likes=242, min_likes=None)
```
_at this configuration above, it **will not** check number of the existing likes against **minimum** value_

* **_Example_**:  
```python
session.set_delimit_liking(enabled=True, max_likes=500, min_likes=7)
```
_**Now**, if a post has more existing likes than maximum value of `500`, then it will not like that post,
**similarly**, if that post has less existing likes than the minimum value of `7`, then it will not like that post..._


### Commenting based on the number of existing comments a post has
##### This is used to check the number of existing comments a post has and if it _either_ **exceed** the _maximum_ value set OR **does not pass** the _minimum_ value set then it will not comment on that post
```python
session.set_delimit_commenting(enabled=True, max_comments=32, min_comments=0)
```
Use `enabled=True` to **activate** and `enabled=False` to **deactivate** it, _any time_  
`max` is the maximum number of comments to compare  
`min` is the minimum number of comments to compare
> You can use **both** _max_ & _min_ values OR **one of them** _as you desire_, just **leave** it out or **put** it to `None` _to the one_ you **don't want to** check for., _e.g._,
```python
session.set_delimit_commenting(enabled=True, min_comments=4)
# or
session.set_delimit_commenting(enabled=True, max_comments=None, min_comments=4)
```
_at this configuration above, it **will not** check number of the existing comments against **maximum** value_

* **_Example_**:  
```python
session.set_delimit_commenting(enabled=True, max_comments=70, min_comments=5)
```
_**Now**, if a post has more comments than the maximum value of `70`, then it will not comment on that post,
**similarly**, if that post has less comments than the minimum value of `5`, then it will not comment on that post..._


### Commenting based on mandatory words in the description or first comment

##### This is used to check the description of the post and the first comment of the post (some users only put tags in the comments instead of the post description) for the occurence of mandatory words before commenting. If none of the mandatory words is present, the post will not be commented.

This feature is helpful when you want to comment only on specific tags.

```python
session.set_delimit_commenting(enabled=True, comments_mandatory_words=['cat', 'dog'])
```
> This will only comment on posts that contain either cat or dog in the post description or first comment.


### Interactions based on the number of followers and/or following a user has
##### This is used to check the number of _followers_ and/or _following_ a user has and if these numbers _either_ **exceed** the number set OR **does not pass** the number set OR if **their ratio does not reach** desired potency ratio then no further interaction happens
```python
session.set_relationship_bounds(enabled=True,
				 potency_ratio=1.34,
				  delimit_by_numbers=True,
				   max_followers=8500,
				    max_following=4490,
				     min_followers=100,
				      min_following=56,
				       min_posts=10,
                max_posts=1000)
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
session.set_relationship_bounds(enabled=True, potency_ratio=None, delimit_by_numbers=True, max_followers=22668, max_following=10200, min_followers=400, min_following=240)
```
* **2**. You can use **only** `potency_ratio` (**e.g.**, `potency_ratio=-1.5`, `delimit_by_numbers=False`) - _will decide per_ `potency_ratio` _regardless of the **pre-defined** max & min values_
```python
session.set_relationship_bounds(enabled=True, potency_ratio=-1.5, delimit_by_numbers=False, max_followers=400701, max_following=90004, min_followers=963, min_following=2310)
```
> apparently, _once_ `delimit_by_numbers` gets `False` value, max & min values _do not matter_
* **3**. You can use both `potency_ratio` and **pre-defined** max & min values **together** (**e.g.**, `potency_ratio=2.35`, `delimit_by_numbers=True`) - _will decide per_ `potency_ratio` _& your **pre-defined** max & min values_
```python
session.set_relationship_bounds(enabled=True, potency_ratio=2.35, delimit_by_numbers=True, max_followers=10005, max_following=24200, min_followers=77, min_following=500)
```

> **All** of the **4** max & min values are _able to **freely** operate_, **e.g.**, you may want to _**only** delimit_ `max_followers` and `min_following` (**e.g.**, `max_followers=52639`, `max_following=None`, `min_followers=None`, `min_following=2240`)
```python
session.set_relationship_bounds(enabled=True, potency_ratio=-1.44, delimit_by_numbers=True, max_followers=52639, max_following=None, min_followers=None, min_following=2240)
```


### Interactions based on the number of posts a user has
#### This is used to check number of posts of a user and skip if they aren't in the boundaries provided
```python
session.set_relationship_bounds(min_posts=10,
                                 max_posts=1000)
```
Users that have more than 1000 posts or less than 10 will be discarded

**N.B.:** It is up to the user to check that `min_posts < max_posts`

You can also set only one parameter at a time:
```python
session.set_relationship_bounds(max_posts=1000)
```

Will skip only users that have more than 1000 posts in their feed


### Custom action delays
###### _After doing each action- like, comment, follow, unfollow or story, there is a sleep delay to provide smooth activity flow_.  
##### But you can set a _custom_ sleep delay for each action yourself by using the `set_action_delays` setting!
```python
session.set_action_delays(enabled=True,
                           like=3,
                           comment=5,
                           follow=4.17,
                           unfollow=28,
                           story=10)
```
_Now it will sleep `3` seconds **after putting every single like**, `5` seconds for every single comment and similarly for the others.._


You can also customize the sleep delay of _e.g._ **only the likes**:
```python
session.set_action_delays(enabled=True, like=3)
```

##### Wanna go smarter? - use `random_range_from` and `random_range_to`  
By just enabling `randomize` parameter, you can **enjoy** having random sleep delays at desired range, e.g.,
```python
session.set_action_delays(enabled=True, like=5.2, randomize=True, random_range_from=70, random_range_to=140)
```
_There, it will have a **random sleep delay between** `3.64` (_`70`% of `5.2`_) and `7.28`(_`140`% of `5.2`_) seconds _each time_ **after putting a like**._  
+ You can also put **only the max range** as- `random_range_from=None, random_range_to=200`  
Then, the _min range will automatically be_ `100`%- the same time delay itself.  
And the random sleep delays will be between `5.2` and `10.4` seconds.  
+ If you put **only the min range** as- `random_range_from=70, random_range_to=None`  
Then, the _max range will automatically be_ `100`%- the same time delay itself.  
And the random sleep delays will be between `3.64` and `5.2` seconds.  
+ But if you **put `None` to both** min & max ranges as- `random_range_from=None, random_range_to=None`  
Then no randomization will occur and the sleep delay will always be `5.2` seconds.
+ Heh! You **mistakenly put** min range instead of max range as- `random_range_from=100, random_range_to=70`?  
No worries. It will automatically take the smaller number as min and the bigger one as max.
+ Make sure to use the values **bigger than `0`** for the `random_rage` percentages.  
E.g. `random_range_from=-10, random_range_to=140` is an invalid range and no randomization will happen.
+ You can provide **floating point numbers** as percentages, too!  
`random_range_from=70.7, random_range_to=200.45` will work greatly.

###### Note: There is a _minimum_ **default** delay for each action and if you enter a smaller time of delay than the default value, then it will **pick the default value**. You can turn that behaviour off with `safety_match` parameter.
```python
session.set_action_delays(enabled=True, like=0.15, safety_match=False)
```
_It has been held due to safety considerations. Cos sleeping a respective time after doing actions- for example ~`10` seconds after an unfollow, is very important to avoid possible temporary blocks and if you might enter e.g. `3` seconds for that without realizing the outcome..._

---

<br /> 
<br />

## Actions
### Like by Tags

```python
# Like posts based on hashtags
session.like_by_tags(['natgeo', 'world'], amount=10)
```

#### Parameters:
 `tags`: The tags that will be searched for and posts will be liked from

  `amount`: The amount of posts that will be liked

  `skip_top_posts`: Determines whether the first 9 top posts should be liked or not (default is True)

  `use_smart_hashtags`: Make use of the [smart hashtag feature](#smart-hashtags)

  `use_smart_location_hashtags`: Make use of the [smart location hashtag feature](#smart-location-hashtags)

  `interact`: Defines whether the users of the given post should also be interacted with (needs `set_user_interact` to be also set)

  `randomize`: Determines whether the first `amount` of posts should be liked or a random selection.

  `media`: Determines which media should be liked, Photo or Video (default is `None` which is all)


#### Like by Tags and interact with user

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


### Comment by Locations

```python
session.comment_by_locations(['224442573/salton-sea/'], amount=100)
# or
session.comment_by_locations(['224442573'], amount=100)
# or include media entities from top posts section

session.comment_by_locations(['224442573'], amount=5, skip_top_posts=False)
```

This method allows commenting by locations, without liking posts. To get locations follow instructions in 'Like by Locations'


### Follow by Tags

```python
# Follow user based on hashtags (without liking the image)

session.follow_by_tags(['tag1', 'tag2'], amount=10)
```

#### Parameters:
 `tags`: The tags that will be searched for and posts will be liked from

  `amount`: The amount of posts that will be liked

  `skip_top_posts`: Determines whether the first 9 top posts should be liked or not (default is True)

  `use_smart_hashtags`: Make use of the [smart hashtag feature]()

  `use_smart_location_hashtags`: Make use of the [smart location hashtag feature]()

  `interact`: Defines whether the users of the given post should also be interacted with (needs `set_user_interact` to be also set)

  `randomize`: Determines whether the first `amount` of posts should be liked or a random selection.

  `media`: Determines which media should be liked, Photo or Video (default is `None` which is all)


### Follow by Locations

```python
session.follow_by_locations(['224442573/salton-sea/'], amount=100)
# or
session.follow_by_locations(['224442573'], amount=100)
# or include media entities from top posts section

session.follow_by_locations(['224442573'], amount=5, skip_top_posts=False)
```
This method allows following by locations, without liking or commenting posts. To get locations follow instructions in 'Like by Locations'



### Following by a list
##### This will follow each account from a list of instagram nicknames
```python
follow_by_list(followlist=['samantha3', 'larry_ok'], times=1, sleep_delay=600, interact=False)
```
_only follows a user once (if unfollowed again) would be useful for the precise targeting_  
`sleep_delay` is used to define break time after some good following (_averagely ~`10` follows_)  
For example, if one needs to get followbacks from followers of a chosen account/group of accounts.  
```python
accs = ['therock','natgeo']
session.follow_by_list(accs, times=1, sleep_delay=600, interact=False)
```
* You can also **interact** with the followed users by enabling `interact=True` which will use the configuration of `set_user_interact` setting:  
```python
session.set_user_interact(amount=4,
				 percentage=50,
                  randomize=True,
                   media='Photo')
session.follow_by_list(followlist=['samantha3', 'larry_ok'], times=2, sleep_delay=600, interact=True)
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
> **Note**: [simulation](#simulation) takes place while running this feature.



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
> **Note**: [simulation](#simulation) takes place while running this feature.



### Follow and interact someone else's followers/following

```python
# For 50% of the 30 newly followed, move to their profile
# and randomly choose 5 pictures to be liked.
# Take into account the other set options like the comment rate
# and the filtering for inappropriate words or users

session.set_user_interact(amount=5, randomize=True, percentage=50, media='Photo')
session.follow_user_followers(['friend1', 'friend2', 'friend3'], amount=10, randomize=False, interact=True)
```


### Follow the likers of photos of users
##### This will follow the people those liked photos of given list of users   
```python
session.follow_likers(['user1' , 'user2'], photos_grab_amount = 2, follow_likers_per_photo = 3, randomize=True, sleep_delay=600, interact=False)
```
_in this case 2 random photos from each given user will be analyzed and 3 people who liked them will be followed, so 6 follows in total_  
The `usernames` can be any list   
The `photos_grab_amount` is how many photos will I grat from users profile and analyze who liked it  
The `follow_likers_per_photo` is how many people to follow per each photo  
`randomize=False` will take photos from newes, true will take random from first 12  
`sleep_delay` is used to define break time after some good following (_averagely ~`10` follows_)

* You can also **interact** with the followed users by enabling `interact=True` which will use the configuration of `set_user_interact` setting:  
```python
session.set_user_interact(amount=2,
				 percentage=70,
                  randomize=True,
                   media='Photo')
session.follow_likers(['user1' , 'user2'], photos_grab_amount = 2, follow_likers_per_photo = 3, randomize=True, sleep_delay=600, interact=True)
```


### Follow the commenters of photos of users
##### This will follow the people those commented on photos of given list of users
```python
session.follow_commenters(['user1', 'user2', 'user3'], amount=100, daysold=365, max_pic = 100, sleep_delay=600, interact=False)
```
_in this case (max 100 newest photos & maximum 365 days old) from each given user will be analyzed and 100 people who commented the most will be followed_  
The `usernames` can be any list  
The `amount` is how many people to follow  
The `daysold` will only take commenters from photos no older than `daysold` days  
The `max_pic` will limit number of photos to analyze  
`sleep_delay` is used to define break time after some good following (_averagely ~`10` follows_)

* You can also **interact** with the followed users by enabling `interact=True` which will use the configuration of `set_user_interact` setting:  
```python
session.set_user_interact(amount=3,
				 percentage=32,
                  randomize=True,
                   media='Video')
session.follow_commenters(['user1', 'user2', 'user3'], amount=100, daysold=365, max_pic = 100, sleep_delay=600, interact=True)
```


### Unfollowing
###### Unfollows the accounts you're following  
_It will unfollow ~`10` accounts and sleep for ~`10` minutes and then will continue to unfollow..._

##### There are `4` _Unfollow methods_ available to use:
`|>` **customList**  `|>` **InstapyFollowed**  `|>` **nonFollowers**  `|>` **allFollowing**

**1** - Unfollow **specific users** from a _CUSTOM_ list (_has `2` **track**s- `"all"` and `"nonfollowers"`_):  
_when **track** is `"all"`, it will unfollow **all of the users** in a given list_;
```python
custom_list = ["user_1", "user_2", "user_49", "user332", "user50921", "user_n"]
session.unfollow_users(amount=84, custom_list_enabled=True, custom_list=custom_list, custom_list_param="all", style="RANDOM", unfollow_after=55*60*60, sleep_delay=600)
```
_if **track** is `"nonfollowers"`, it will unfollow all of the users in a given list **WHO are not following you back**_;
```python
custom_list = ["user_1", "user_2", "user_49", "user332", "user50921", "user_n"]
session.unfollow_users(amount=84, custom_list_enabled=True, custom_list=custom_list, custom_list_param="nonfollowers", style="RANDOM", unfollow_after=55*60*60, sleep_delay=600)
```
* **PRO**: `customList` method can take any kind of _iterable container_, such as `list`, `tuple` or `set`.

**2** - Unfollow the users **WHO** was _followed by `InstaPy`_ (_has `2` **track**s- `"all"` and `"nonfollowers"`_):  
_again, if you like to unfollow **all of the users** followed by InstaPy, use the **track**- `"all"`_;
```python
session.unfollow_users(amount=60, instapy_followed_enabled=True, instapy_followed_param="all", style="FIFO", unfollow_after=90*60*60, sleep_delay=501)
```
_but if you like you unfollow only the users followed by InstaPy **WHO do not follow you back**, use the **track**- `"nonfollowers"`_;
```python
session.unfollow_users(amount=60, instapy_followed_enabled=True, instapy_followed_param="nonfollowers", style="FIFO", unfollow_after=90*60*60, sleep_delay=501)
```

**3** - Unfollow the users **WHO** `do not` _follow you back_:
```python
session.unfollow_users(amount=126, nonFollowers=True, style="RANDOM", unfollow_after=42*60*60, sleep_delay=655)
```

**4** - `Just` unfollow, **regardless of** a user _follows you or not_:
```python
session.unfollow_users(amount=40, allFollowing=True, style="LIFO", unfollow_after=3*60*60, sleep_delay=450)
```

#### Parameters (_all of these parameters apply to all of the 4 methods available_):

`style`  
You can choose _unfollow style_ as `"FIFO"` (_First-Input-First-Output_) **OR** `"LIFO"` (_Last-Input-First-Output_) **OR** `"RANDOM"`.  
* with `"FIFO"`, it will unfollow users _in the **exact** order they are loaded_ (_`"FIFO"` is the default style unless you **change** it_);  
* with `"LIFO`" it will unfollow users _in the **reverse** order they were loaded_;  
* with `"RANDOM"` it will unfollow users _in the **shuffled** order_;


`unfollow_after`  
By using this, you can unfollow users **only after** following them certain amount of time.  
_it will help to provide **seamless** unfollow activity without the notice of the target user_   
To use it, just add `unfollow_after` parameter with the _desired time interval_, _e.g._,
```python
session.unfollow_users(amount=94, instapy_followed_enabled=True, instapy_followed_param="all", style="RANDOM", unfollow_after=48*60*60, sleep_delay=600)
```
_will unfollow users **only after following them** `48` hours (`2` days)_.  
* Since `unfollow_after`s value is in _seconds_, you can simply give it `unfollow_after=3600` to unfollow after `3600` seconds.  
_Yeah, values kind of `1*60*60`- which is also equal to `1` hour or `3600` seconds, is much more easier to use_.  

**Sure** if you like to not use it, give the value of `None`- `unfollow_after=None`.

`sleep_delay`  
Sleep delay _sets_ the time it will sleep **after** every ~`10` unfollows (_default delay is ~`10` minutes_).

> **NOTE**: You should know that, _in one RUN_, `unfollow_users` feature can take only one method from all `4` above.  
That's why, **it is best** to **disable** other `3` methods _while using a one_:
```python
session.unfollow_users(amount=200, custom_list_enabled=True, custom_list=["user1", "user2", "user88", "user200"], instapy_followed_enabled=False, nonFollowers=False, allFollowing=False, style="FIFO", unfollow_after=22*60*60, sleep_delay=600)
```
_here the unfollow method- **customList** is used_  
**OR** just keep the method you want to use and remove other 3 methods from the feature
```python
session.unfollow_users(amount=200, allFollowing=True, style="FIFO", unfollow_after=22*60*60, sleep_delay=600)
```
_here the unfollow method- **alFollowing** is used_


### Interact on posts at given URLs
###### Like, comment, follow on the post in the links provided, also can interact the owner of the post

```python
session.interact_by_URL(urls=["some/URL/1", "some/URL/2" "other/URL"], randomize=True, interact=True)
```

**To use**, _define_ all of the `interaction settings` and **start** the feature right away!
```python
#define interaction settings
session.set_do_like(enabled=True, percentage=94)
session.set_do_comment(enabled=True, percentage=24)
session.set_comments(["Masterful shot", "Chilling!", "Unbelievably great..."])
session.set_do_follow(enabled=True, percentage=44)
session.set_user_interact(amount=6, randomize=True, percentage=72, media='Photo')

#start the feature
session.interact_by_URL(urls=["Fv0J4AJ3Y7r/?taken-at=628416252", "Vb0D4bJgY7r" "Dj0J4VJgY7r"], randomize=True, interact=True)
```
##### Parameters:
`urls`:  
Contains the _URLs_ of the **posts** _to be interacted_.  
* You can provide _URLs_ in these formats:  
**full:** `"https://www.IG.com/p/Aj0J4bJDY7r/?taken-at=128316221"`  
just **post link:** `"https://www.IG.com/p/Aj0J4bJDY7r/"`  
just post **handle:** `"Aj0J4bJDY7r/?taken-at=128316221"`  
just post **ID:** `"Aj0J4bJDY7r"`  

`randomize`:  
Shuffles the **order** of the _URLs_ in the given list _before starts to interact_.  

`interact`:  
Use it if you like to also _interact the post owner_ **after** doing interactions on the **post itself**.  



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

### Interact with specific users' tagged posts

```python
# Interact with specific users' tagged posts
# set_do_like, set_do_comment, set_do_follow are applicable

session.set_do_follow(enabled=False, percentage=50)
session.set_comments(["Cool", "Super!"])
session.set_do_comment(enabled=True, percentage=80)
session.set_do_like(True, percentage=70)
session.interact_by_users_tagged_posts(['user1', 'user2', 'user3'], amount=5, randomize=True, media='Photo')
```


### Interact with someone else's followers

```python
# Interact with the people that a given user is followed by
# set_do_comment, set_do_follow and set_do_like are applicable

session.set_user_interact(amount=5, randomize=True, percentage=50, media='Photo')
session.set_do_follow(enabled=False, percentage=70)
session.set_do_like(enabled=False, percentage=70)
session.set_comments(["Cool", "Super!"])
session.set_do_comment(enabled=True, percentage=80)
session.interact_user_followers(['natgeo'], amount=10, randomize=True)
```
> **Note**: [simulation](#simulation) takes place while running this feature.


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
> **Note**: [simulation](#simulation) takes place while running this feature.


### Interact by Comments
###### Like comments on posts, reply to them and then interact by the users whose comment was liked on the post

```python
session.interact_by_comments(usernames=["somebody", "other buddy"],
                             posts_amount=10,
                             comments_per_post=5,
                             reply=True,
                             interact=True,
                             randomize=True,
                             media="Photo")
```
#### Parameters
`usernames`
: A list containing the _usernames_ of users on WHOSE **posts'** _comments will be interacted_;  

`posts_amount`
: Number of the posts to get from **each user** for interacting by comments;  

`comments_per_post`
: Choose how many comments to interact (_like and then reply_) on **each post**;  

`reply`
: Choose if it **should reply** to comments;  

`interact`
: Use if you also like to _interact the commenters_ **after** finishing liking (_and then replying to_) comments on the **post**;  

`randomize`
: Shuffles the **order** of the **_posts_** from users' feed and **_comments_** in the given post;  

`media`
: Choose the **type of** media to be interacted - _`"Photo"`_ for photos, _`"Video"`_ for videos, `None` for any media;


#### Usage
**To use**, set **replying** and **interaction** configuration(s)
```python
session.set_do_reply_to_comments(enabled=True, percentage=14)
session.set_comment_replies(replies=[u"😎😎😎", u"😁😁😁😁😁😁😁💪🏼", u"😋🎉", "😀🍬", u"😂😂😂👈🏼👏🏼👏🏼", u"🙂🙋🏼‍♂️🚀🎊🎊🎊", u"😁😁😁", u"😂",  u"🎉",  u"😎", u"🤓🤓🤓🤓🤓", u"👏🏼😉"],
                            media="Photo")

session.set_user_interact(amount=2, percentage=70, randomize=False, media="Photo")
# also configure [at least] liking to be used while interacting with the commenters ...
session.set_do_like(enabled=True, percentage=94)

# start the feature
session.interact_by_comments(usernames=["somebody", "other.buddy"], posts_amount=10, comments_per_post=5, reply=True, interact=True, randomize=True, media="Photo")
```
**Note**: To be able to reply to comments, you have to **turn on** _text analytics_- [**Yandex**](#yandex-translate-api) & [**MeaningCloud**](#meaningcloud-sentiment-analysis-api).  
So that they will analyze the content of comments and if it is appropriate, will send a reply to the comment.  
_To configure those text analytics, see the usage in their sections_.

There are **3** **COMBINATIONS** _available_ to use regarding _text analysis_:  
**a**-) ONLY **Sentiment Analysis**;  
_MeaningCloud must be turned on and Yandex must be enabled with a valid API key_,
```python
session.set_use_meaningcloud(enabled=True, license_key='', polarity="P")
session.set_use_yandex(enabled=True, API_key='')
```
**b**-) ONLY **Language Match**;
_Yandex must be turned on_,
```python
session.set_use_yandex(enabled=True, API_key='', match_language=False, language_code="en")
```
**c**-) BOTH **Sentiment Analysis** and **Language Match**;
_MeaningCloud and Yandex must be turned on_,  
```python
session.set_use_meaningcloud(enabled=True, license_key='', polarity="P")
session.set_use_yandex(enabled=True, API_key='', match_language=True, language_code="en")
```

If you have **followed** any of those 3 _text analysis_ combinations:  
It will first _analyze comments' content_ and if it _is appropriate_, then it will _first_ like, _then_ will reply to it.  
All those inappropriate comments will neither be liked, nor replied to.  

If you have **not followed** any of those 3 _text analysis_ combinations OR **misconfigured** them:  
Comments' content will _not be able to be analyzed_ and that's why _no any comments will be_ replied.  
_Yet_, it will like _all of the comments_ that are available.  

In conclusion, the whole block SHOULD look like this,  
```python
session.set_use_meaningcloud(enabled=True, license_key='', polarity="P")
session.set_use_yandex(enabled=True, API_key='', match_language=True, language_code="en")

session.set_do_comment(enabled=True, percentage=14)
session.set_comment_replies(replies=[u"😎😎😎", u"😁😁😁😁😁😁😁💪🏼"], media="Photo")

session.set_user_interact(amount=2, percentage=70, randomize=False, media="Photo")
session.set_do_like(enabled=True, percentage=100)

session.interact_by_comments(usernames=["somebody", "other.buddy"], posts_amount=10, comments_per_post=5, reply=True, interact=True, randomize=True, media="Photo")
```

#### Extras
+ comments from the poster are ignored (_those comments are mostly poster's replies_);  
+ owner's (_logged in user_) comments are also ignored;  
+ if the commenter is in _blacklist_ or `ignored_users` list, that comment will also be ignored;  
+ it will take only one comment from each unique commenter;  
+ as if there are any usable comments, it will first **like the post itself** before _interacting by comments_ cos liking comments and replying to them without liking the post can look spammy;    
+ it will reply to a comment only after liking it;  
+ it will not send the same reply again on overall posts per each username in the list provided by you;  

#### PROs
+ you can use this feature to **auto-like** comments, **auto-reply** to them on your _own_ posts;  
+ else than interacting by the comments in your _own_ posts, you can use this feature to like lots of comments from _other users'_ posts, reply to some of _them_ and interact by those users just after _liking_ & _replying_ to their comments;  

#### CONs
+ liking a comment doesn't fill up your like quota, but replying to a comment does it to the comment quota. Try to compensate it in your style and do not overuse;  
+ using auto-reply capability of this feature can result in unwanted miscommunication between you and the commenter IN CASE OF you do not make an efficient use of text analytics;  


### Accept pending follow requests

```python
session.accept_follow_requests(amount=100, sleep_delay=1)
```

`amount`   
The maximum amount of follow requests that will be accepted.

`sleep_delay`  
Sleep delay _sets_ the time it will sleep **after** every accepted request (_default delay is ~ `1` second).


### Remove outgoing follow requests

```python
# Remove outgoing unapproved follow requests from private accounts

session.remove_follow_requests(amount=200, sleep_delay=600)
```


### InstaPy Pods

  In case you are unfamiliar with the concept do read a little. Here's a blog to learn more about [Pods](https://blog.hubspot.com/marketing/instagram-pods)

  ```python

 photo_comments = ['Nice shot! @{}',
                   'I love your profile! @{}',
 	           'Your feed is an inspiration :thumbsup:',
 	           'Just incredible :open_mouth:',
 	           'What camera did you use @{}?',
 	           'Love your posts @{}',
 	           'Looks awesome @{}',
 	           'Getting inspired by you @{}',
 	           ':raised_hands: Yes!',
 	           'I can feel your passion @{} :muscle:']

 session = InstaPy()

 with smart_run(session):
     session.set_comments(photo_comments, media='Photo')
     session.join_pods()
  ```

  #### Parameters:  
 `topic`:  
 Topic of the posts to be interacted with. `general` by default.

  > Note :  Topics allowed are {'general', 'fashion', 'food', 'travel', 'sports', 'entertainment'}.

 `engagement_mode`:
 Desided engagement mode for your posts. There are four levels of engagement modes 'no_comments', 'light', 'normal' and 'heavy'(`normal` by default). Setting engagement_mode to 'no_comments' makes you receive zero comments on your posts from pod members, 'light' encourages approximately 10% of pod members to comment on your post, similarly it's around 30% and 90% for 'normal' and 'heavy' modes respectively. Note: Liking, following or any other kind of engagements doesn't follow these modes.

### Skip based on profile bio

```python
session.set_skip_users(skip_bio_keyword = ['free shipping',' Order', 'visa', 'paypal'])
```

This will skip all users that have one these keywords on their bio.

### Instapy Stories

#### Watching Stories with interact

Will add story watching while interacting with users

```python
session.set_do_story(enabled = True, percentage = 70, simulate = True)
```

 `simulate`:
 If set to `True` InstaPy will simulate watching the stories (you won't see it in the browser), we just send commands to Instagram saying we have watched the stories.
 If set to `False` Instapy will perform the exact same action as a human user (clicking on stories, waiting until watching finishes, etc...)

  Please note: `simulate = False` is the safest settings as it fully disables all additional, simulated interactions

#### Watch stories by Tags

Will watch up to 20 stories published with specified tags.

```python
session.story_by_tags(['tag1', 'tag2'])
```

#### Watch stories from users

Take a list of users and watch their stories.

```python
session.story_by_users(['user1', 'user2'])
```

---

<br />
<br />

## Third Party Features
### Clarifai ImageAPI
<img src="https://clarifai.com/cms-assets/20180311184054/Clarifai_Pos.svg" width="200" align="right">

###### Note: Head over to [https://developer.clarifai.com/signup/](https://developer.clarifai.com/signup/) and create a free account, once you're logged in go to [https://developer.clarifai.com/account/applications/](https://developer.clarifai.com/account/applications/) and create a new application. You can find the client ID and Secret there. You get 5000 API-calls free/month.

If you want the script to get your CLARIFAI_API_KEY for your environment, you can do:

```
export CLARIFAI_API_KEY="<API KEY>"
```
#### Example with Imagecontent handling

```python
session.set_do_comment(True, percentage=10)
session.set_comments(['Cool!', 'Awesome!', 'Nice!'])
session.set_use_clarifai(enabled=True)
session.clarifai_check_img_for(['nsfw'])
session.clarifai_check_img_for(['food', 'lunch', 'dinner'], comment=True, comments=['Tasty!', 'Nice!', 'Yum!'])

session.end()
```
#### Enabling Imagechecking

```python
# default enabled=False , enables the checking with the Clarifai API (image
# tagging) if secret and proj_id are not set, it will get the environment
# variables 'CLARIFAI_API_KEY'.

session.set_use_clarifai(enabled=True, api_key='xxx')
```

#### Using Clarifai Public Models and Custom Models
If not specified by setting the `models=['model_name1']` in `session.set_use_clarifai`, `models` will be set to `general` by default.

If you wish to check against a specific model or multiple models (see Support for Compound Model Queries below), you can specify the models to be checked as shown below.

To get a better understanding of the models and their associated concepts, see the Clarifai [Model Gallery](https://clarifai.com/models) and [Developer Guide](https://clarifai.com/developer/guide/)

**NOTE ON MODEL SUPPORT**: At this time, the support for the`Focus`, `Face Detection`, `Face Embedding`, and `General Embedding` has not been added.

```python
# Check image using the NSFW model
session.set_use_clarifai(enabled=True, api_key='xxx', models=['nsfw'])

# Check image using the Apparel model
session.set_use_clarifai(enabled=True, api_key='xxx', models=['apparel'])

# Check image using the Celebrity model
session.set_use_clarifai(enabled=True, api_key='xxx', models=['celebrity'])

# Check image using the Color model
session.set_use_clarifai(enabled=True, api_key=‘xxx’, models=[‘model’])

# Check image using the Demographics model
session.set_use_clarifai(enabled=True, api_key=‘xxx’, models=[‘demographics’])

# Check image using the Food model
session.set_use_clarifai(enabled=True, api_key='xxx', models=['food'])

# Check image using the Landscape Quality model
session.set_use_clarifai(enabled=True, api_key='xxx', models=['landscape quality'])

# Check image using the Logo model
session.set_use_clarifai(enabled=True, api_key='xxx', models=['logo'])

# Check image using the Moderation model
session.set_use_clarifai(enabled=True, api_key='xxx', models=['moderation'])

# Check image using the Portrait Quality model
session.set_use_clarifai(enabled=True, api_key='xxx', models=['portrait quality'])

# Check image using the Textures and Patterns model
session.set_use_clarifai(enabled=True, api_key='xxx', models=['textures'])

# Check image using the Travel model
session.set_use_clarifai(enabled=True, api_key='xxx', models=['travel'])

# Chaeck image using the Weddings model
session.set_use_clarifai(enabled=True, api_key='xxx', models=['weddings'])

# Check image using a custom model where model_name is name of your choosing (see Clarifai documentation for using custom models)
session.set_use_clarifai(enabled=True, api_key='xxx', models=['your-model-name'])
```

#### Filtering Inappropriate Images

```python
# uses the clarifai api to check if the image contains nsfw content
# by checking against Clarifai's NSFW model
# -> won't comment if image is nsfw

session.set_use_clarifai(enabled=True, api_key='xxx', models=['nsfw'])
session.clarifai_check_img_for(['nsfw'])
```

```python
# uses the clarifai api to check if the image contains inappropriate content
# by checking against Clarifai's Moderation model
# -> won't comment if image is suggestive or explicit

session.set_use_clarifai(enabled=True, api_key='xxx', models=['moderation'])
session.clarifai_check_img_for(['suggestive', 'explicit'])

# To adjust the threshold for accepted concept predictions and their
# respective score (degree of confidence) you can set the default probability
# parameter for Clarifai (default 50%). For example, you could set probability to 15%.
# -> any image with a nsfw score of 0.15 of higher will not be commented on

session.set_use_clarifai(enabled=True, api_key='xxx', probability= 0.15, models=['nsfw'])
session.clarifai_check_img_for(['nsfw'])
```

#### Filtering by Keyword

```python
# uses the clarifai api to check if the image concepts contain the keyword(s)
# -> won't comment if image contains the keyword

session.clarifai_check_img_for(['building'])
```
#### Specialized Comments for Images with Specific Content

```python
# checks the image for keywords food and lunch. To check for both, set full_match in
# in session.set_use_clarifia to True, and if both keywords are found,
# InstaPy will comment with the given comments. If full_match is False (default), it only
# requires a single tag to match Clarifai results.

session.set_use_clarifai(enabled=True, api_key='xxx', full_match=True)
session.clarifai_check_img_for(['food', 'lunch'], comment=True, comments=['Tasty!', 'Yum!'])

# If you only want to accept results with a high degree of confidence, you could
# set a probability to a higher value, like 90%.

session.set_use_clarifai(enabled=True, api_key='xxx', probability=0.90, full_match=True)
session.clarifai_check_img_for(['food', 'lunch'], comment=True, comments=['Tasty!', 'Yum!'])
```

#### Querying Multiple Models with Workflow (Single API Call)
You can query multiple Clarifai models with a single API call by setting up a custom workflow.  Using a `workflow` is the recommended way to query multiple models. Alternatively, it is possible to query multiple models separately (see Querying Multiple Models (Multiple API Calls) below).

To setup a workflow, see the [Workflow Documentation](https://www.clarifai.com/developer/guide/workflow#workflow).

**NOTE** :As mentioned above, the `Focus`, `Face Detection`, `Face Embedding`, and `General Embedding` models are not current supported.

Once you have a workflow setup, you can use InstaPy to check images with the Clarifai Image API by setting the `workflow` parameter in `session.set_use_clarifai` to the name of your custom workflow.

Let's say you want to comment 'Great shot!' on images of men or women with the hashtag `#selfie`, but you want to make sure not to comment on images which might contain inappropriate content. To get general concepts, e.g. `woman`, you would setup your workflow using `General` and to check the image for the concepts `nsfw` and `explicit` you would also want to add NSFW and Moderation models to your workflow.

For example:
```python
session.set_use_clarifai(enabled=True, api_key='xxx', workflow=['your-workflow'], proxy='123.123.123.123:5555')
session.clarifai_check_img_for(['woman', 'man'], ['nsfw', 'explicit', 'suggestive'], comment=True, comments=['Great shot!'])
```
If Clarifai's response includes the concepts of either `woman` or `man` but also includes at least `nsfw`, `explicit`, or `suggestive`, InstaPy will not comment. On the other hand, if Clarifai's response includes the concepts of either `woman` or `man` but does not include any of the concepts `nsfw`, `explicit`, or `suggestive`, InstaPy will add the comment `Great shot!`


#### Querying Multiple Models (Multiple API Calls)
In the event that you do not want to set up a workflow, you can also query multiple models using multiple API calls.

**WARNING**: If you are using a free account with Clarifiai, be mindful that the using compound API queries could greatly increase your chances of exceeding your allotment of free 5000 operations per month. The number of Clarifai billable operations per image check equals the number of models selected. For example, if you check 100 images against `models=['general', 'nsfw', 'moderation']`, the total number of billable operations will be 300.

Following the example above, to get general concepts, e.g. `woman`, you would use the model `general` and to check the image for the concepts `nsfw` and `explicit` you would also want to check the image against the NSFW and Moderation models.

For example:
```python
session.set_use_clarifai(enabled=True, api_key='xxx', models=['general', 'nsfw', 'moderation'], proxy=None)
session.clarifai_check_img_for(['woman', 'man'], ['nsfw', 'explicit', 'suggestive'], comment=True, comments=['Great shot!'])
```

Using proxy to access clarifai:
We have 3 options:
1. ip:port
2. user:pass@ip:port
3. None

#### Checking Video
**WARNING**: Clarifai checks one frame of video for content for every second of video. **That is, in a 60 second video, 60 billable operations would be run for every model that the video is being checked against.** Running checks on video should only be used if you have special needs and are prepared to use a large number of billable operations.

To have Clarifai run a predict on video posts, you can set the `check_video` argument in `session.set_use_clarifai` to `True`. By default, this argument is set to `False`. Even if you do not choose to check the entire video, Clarifai will still check the video's keyframe for content.

For example:

```python
session.set_use_clarifai(enabled=True, api_key='xxx', check_video=True)
```

With video inputs, Clarifai's Predict API response will return a list of concepts at a rate of one frame for every second of a video.

Be aware that you cannot check video using a `workflow` and that only a select number of public models are currently supported. Models currently supported are: Apparel, Food, General, NSFW, Travel, and Wedding. In the event that the models being used do not support video inputs or you are using a workflow, the video's keyframe will still be checked for content.

##### Check out [https://clarifai.com/demo](https://clarifai.com/demo) to see some of the available tags.</h6>


### Text Analytics
#### Yandex Translate API

<img src="https://yastatic.net/www/_/Q/r/sx-Y7-1azG3UMxG55avAdgwbM.svg" width="196" align="right">

<img src="https://yastatic.net/s3/home/logos/services/1/translate.svg" width="66" align="left">

###### Offers excellent language detection and synchronized translation for over 95 languages 😎 worldwide

_This service currently is supported only by the [Interact by Comments](#interact-by-comments) feature_.

##### Usage
Go [**sign up**](https://translate.yandex.com/developers/keys) on [_translate.yandex.com_](https://translate.yandex.com) and get a _free_ `API_key`;  
_Then configure its usage at your **quickstart** script_,
```python
session.set_use_yandex(enabled=True,
                       API_key='',
                       match_language=True,
                       language_code="en")
```


##### Parameters
`enabled`
: Put `True` to **activate** or `False` to **deactivate** the service usage;  

`API_key`
: The _key_ which is **required** to authenticate `HTTP` _requests_ to the **API**;  

`match_language`
: **Enable** if you would like to match the language of the text;

`language_code`
: **Set** your desired language's code to **match language** (_if it's enabled_);
>You can get the list of all supported languages and their codes at [_tech.yandex.com_](https://tech.yandex.com/translate/doc/dg/concepts/api-overview-docpage/#api-overview__languages).


##### Rate Limits
In its _free_ plan, the **daily** request _limit_ is `1,000,000` characters and the **monthly** _limit_ is `10,000,000` characters.
>To increase the request limit, you can **switch** to the `fee-based` version of the service (_$`15`/million chars_)..


##### Examples

**1**-) Matching language;
```python
session.set_use_yandex(enabled=True, API_key='', match_language=True, language_code="az")
```
Target text
: "_your technique encourages📸 me_"  

_Now that text is gonna be labeled **inappropriate** COS its language is `english` rather than the desired `azerbaijani`_..    

**2**-) Enabling the **Yandex** service _but NOT_ matching language;
Since **Yandex** Translate is being used [internally] by the **MeaningCloud** service, you can just provide the API key of **Yandex** and enable it without enabling the `match_language` parameter what will be sufficient for the **MeaningCloud** to work..
```python
session.set_use_yandex(enabled=True, API_key='', match_language=False)
```
>And yes, you can enable **Yandex** service to make it be available for **MeaningCloud** and then also _match language_ if you like, in the same setup just by turning the `match_language` parameter on..


##### Legal Notice
[Powered by Yandex.Translate](http://translate.yandex.com/)


#### MeaningCloud Sentiment Analysis API
<img src="https://www.meaningcloud.com/developer/img/LogoMeaningCloud210x85.png" width="210" align="right">

###### Offers a detailed, multilingual analysis of all kind of unstructured content determining its sentiment ⚖
_This service currently is supported only by the [Interact by Comments](#interact-by-comments) feature_.

Determines if text displays _positive_, _negative_, or _neutral_ sentiment - or is _not possible_ to detect.  
Phrases are identified with the _relationship between_ them evaluated which identifies a _global polarity_ value of the text.


##### Usage
**1**-) Go [**sign up**](https://www.meaningcloud.com/developer/login) (_offers **sign in** with_ 😎 _**Github**_) on [_meaningcloud.com_](https://www.meaningcloud.com) and get a _free_ `license_key`;  
_Then configure its usage at your **quickstart** script_,
```python
session.set_use_meaningcloud(enabled=True,
                             license_key='',
                             polarity="P",
                             agreement="AGREEMENT",
                             subjectivity="SUBJECTIVE",
                             confidence=94)
```
**2**-) Install its _package_ for **python** by `pip`;
```powershell
pip install MeaningCloud-python
```
**3**-) Turn on **Yandex** _Translate_ service which is a **requirement** for the language _detection_ & _translation_ at request;  
_To have it configured, read its [documentation](#yandex-translate-api)_.


##### Parameters  
`enabled`
: Put `True` to **activate** or `False` to **deactivate** the service usage;  

`license_key`
: The license key is **required** to do _calls_ to the API;  

`polarity`
: It indicates the polarity found (_or not found_) in the text and applies to the **global** polarity of the text;  
_It's a **graduated** polarity - rates from **very** negative to **very** positive_.

| `score_tag` |                   definition                    |
| ----------- | ----------------------------------------------- |
|    `"P+"`   |       match if text is _**strong** positive_    |
|    `"P"`    |       match if text is _positive_ or above      |
|    `"NEU"`  |       match if text is _neutral_ or above       |
|    `"N"`    |       match if text is _negative_ or above      |
|    `"N+"`   | match if text is _**strong** negative_ or above |
|    `None`   |     do not match per _polarity_ found, at all   |

  > By "_or above_" it means- _e.g._, if you set `polarity` to `"P"`, and text is `"P+"` then it'll also be appropriate (_as it always leans towards positivity_) ..

`agreement`
: Identifies **opposing** opinions - _contradictory_, _ambiguous_;  
_It marks the agreement **between** the sentiments detected in the text, the sentence or the segment it refers to_.

|    `agreement`   |                            definition                                     |
| ---------------- | ------------------------------------------------------------------------- |
|   `"AGREEMENT"`  |       match if the different elements have **the same** polarity          |
| `"DISAGREEMENT"` | match if there is _disagreement_ between the different elements' polarity |
|      `None`      |              do not match per _agreement_ found, at all                   |


`subjectivity`
: Identification of _opinions_ and _facts_ - **distinguishes** between _objective_ and _subjective_;  
_It marks the subjectivity of the text_.

| `subjectivity` |                          definition                           |
| -------------- | ------------------------------------------------------------- |
| `"SUBJECTIVE"` |           match if text that has _subjective_ marks           |
| `"OBJECTIVE"`  | match if text that does not have **any** _subjectivity_ marks |
|     `None`     |         do not match per _subjectivity_ found, at all         |

`confidence`
: It represents the _confidence_ associated with the sentiment analysis **performed on the** text and takes an integer number in the _range of_ `(0, 100]`;  
>If you **don't want to** match per _confidence_ found, at all, use the value of `None`.


##### Rate Limits
It gives you `20 000` single API calls per each month (_starting from the date you have **signed up**_).  
It has _no daily limit_ but if you hit the limit set for number of requests can be carried out concurrently (_per second_) it'll return with error code of `104` rather than the result 😉


##### Language Support
**MeaningCloud** currently supports a generic sentiment model (_called general_) in these languages: _english_, _spanish_, _french_, _italian_, _catalan_, and _portuguese_.  
>You can define your own sentiment models using the user sentiment models console and work with them in the same way as with the sentiment models it provides.  

But **no need to worry** IF your _language_ or _target audience's language_ is NONE of those **officially** supported.  
Cos, to **increase the coverage** and support **all other** languages, as well, **Yandex** _Translate_ service comes to rescue!  
It detects the text's langugage before passing it to **MeaningCloud**, and, if its language is not supported by **MeaningCloud**, it translates it into english and only then passes it to **MeaningCloud** _Sentiment Analysis_..


##### Examples
**a** -) Match **ONLY** per `polarity` and `agreement`
```python
session.set_use_meaningcloud(enabled=True, license_key='', polarity="P", agreement="AGREEMENT")
```
Target text
: "_I appreciate your innovative thinking that results, brilliant images_"  

_Sentiment Analysis_ results for the text:

| `score_tag` |  `agreement`  | `subjectivity` | `confidence` |
| ----------- | ------------- | -------------- | ------------ |
|   `"P+"`    | `"AGREEMENT"` | `"SUBJECTIVE"` |     `100`    |

_Now that text is gonna be labeled **appropriate** COS its polarity is `"P+"` which is more positive than `"P"` and `agreement` values also do match_..  

**b** -) Match **FULLY**
```python
session.set_use_meaningcloud(enabled=True, license_key='', polarity="P+", agreement="AGREEMENT", subjectivity="SUBJECTIVE", confidence=98)
```
Target text
: "_truly fantastic but it looks sad!_"  

_Sentiment Analysis_ results for the text:

| `score_tag` |    `agreement`   | `subjectivity` | `confidence` |
| ----------- | ---------------- | -------------- | ------------ |
|    `"P"`    | `"DISAGREEMENT"` | `"SUBJECTIVE"` |     `92`    |

_Now that text is gonna be labeled **inappropriate** COS its polarity is `"P"` which is less positive than `"P+"` and also, `agreement` values also **do NOT** match, and **lastly**, `confidence` is **below** user-defined `98`_..    


##### Legal Notice
This project uses MeaningCloud™ (http://www.meaningcloud.com) for Text Analytics.

---
### Telegram Integration

This feature allows to connect your InstaPy session with a Telegram bot and send commands
to the InstaPy session

#### Prerequisites
You will need to create a token, for this go into your Telegram App and talk with @fatherbot.
You will also need to set your username as it is checked to ensure that you are authorized to 
access the InstaPy session, to do so go to Settings -> Profile -> Username.

#### Supported actions
There are 3 supported actions:
  - /start : will start the interaction between the bot and instapy. Please note: that the telegram bot 
  cannot send you messages until you first send it a /start message. The bot will store the chat_id in the logs folder
  file telegram_chat_id.txt to be reused in further sessions (so you have to actually do /start just one time)
  - /report : will gather and show the current session statistics
  - /stop: will set the aborting flag to True

#### Examples
```python
from instapy.plugins import InstaPyTelegramBot

        session = InstaPy(username=insta_username,
                          password=insta_password,
                          bypass_with_mobile=True)
                          
        telegram = InstaPyTelegramBot(token='insert_real_token_here', telegram_username='my_username', instapy_session=session)

        # if you want to receive the information when the session ends
        # just add the following before your session.end()
        telegram.end()
        session.end()
````

Additional parameters:
   - debug=True if you want low level telegram debug information
   - proxy if you need one, here is the structure that needs to be passed
    
```python 
    example_proxy = {
         'proxy_url': 'http://PROXY_HOST:PROXY_PORT/',
         # Optional, if you need authentication:
         'username': 'PROXY_USER',
         'password': 'PROXY_PASS',
     }
     telegram = InstaPytelegramBot(... , proxy=example_proxy)
```

#### Additional functionality
you can use 
```python
telegram.send_message(text="this is a message")
```

So you are able to send additional message inside your script if needed. Remember that the telegram bot
is not able to send messages as long as you haven't done at least one /start

   
<br /> 
<br />

## Instance Settings 
### Running on a Headless Browser
Use `headless_browser` parameter to run the bot via the CLI. Works great if running the scripts locally, or to deploy on a server. No GUI, less CPU intensive. [Example](http://g.recordit.co/BhEgXANLhJ.gif)

**Warning:** Some users discourage the use of this feature as Instagram could [detect](https://antoinevastel.com/bot%20detection/2017/08/05/detect-chrome-headless.html) this headless mode!

```python
session = InstaPy(username='test', password='test', headless_browser=True)
```

**(Alternative)**
If the web driver you're using doesn't support headless mode (or the headless mode becomes very detectable), you can use the `nogui` parameter which displays the window out of view. Keep in mind, this parameter lacks support and ease of use, only supporting Linux based operating systems (or those that have Xvfb, Xephyr and Xvnc display software).

```python
session = InstaPy(username='test', password='test', nogui=True)
```


### Bypass Suspicious Login Attempt

InstaPy detects automatically if the Security Code Challenge
is active, if yes, it will ask you for the Security Code on
the terminal.

The Security Code is send to your Email or SMS by Instagram, Email is the defaul option, but you can choose SMS also with:

`bypass_security_challenge_using='sms'` or `bypass_security_challenge_using='email'`

```python
InstaPy(username=insta_username,
        password=insta_password,
        bypass_security_challenge_using='sms')
```

### Use a proxy

You can use InstaPy behind a proxy by specifying server address, port and/or proxy authentication credentials. It works with and without ```headless_browser``` option.

Simple proxy setup example:
```python
session = InstaPy(username=insta_username, 
                  password=insta_password,
		  proxy_address='8.8.8.8', 
		  proxy_port=8080)

```

Proxy setup with authentication example:
```python
session = InstaPy(username=insta_username,
                  password=insta_password,
                  proxy_username='',
                  proxy_password='',
                  proxy_address='8.8.8.8',
                  proxy_port=4444)
```

### Running in threads
If you're running InstaPy in threads and get exception `ValueError: signal only works in main thread` , you have to properly close the session.
There is two ways to do it:

Closing session in smart_run context:
```python
session = InstaPy()
with smart_run(session, threaded=True):
    """ Activity flow """
    # some activity here ...
```


Closing session with `end()` method 
```python
session = InstaPy()
session.login()
# some activity here ...
session.end(threaded_session=True)
```

---

<br /> 
<br />

## Relationship tools
### Grab Followers of a user  
###### Gets and returns `followers` of the given user in desired amount, also can save locally  
```python
popeye_followers = session.grab_followers(username="Popeye", amount="full", live_match=True, store_locally=True)
##now, `popeye_followers` variable which is a list- holds the `Followers` data of "Popeye" at requested time
```
#### Parameters:  
`username`:  
A desired username to grab its followers  
* It can be your `own` username **OR** a _username of some `non-private` account._

`amount`:  
Defines the desired amount of usernames to grab from the given account
* `amount="full"`:
    + Grabs followers **entirely**
* `amount=3089`:
    * Grabs `3089` usernames **if exist**, _if not_, grabs **available** amount

`live_match`:  
Defines the method of grabbing `Followers` data
> **Knowledge Base**:  
Every time you grab `Followers` data in `"full"` range of **any** user, it is also gonna be _stored in some corner_ of `InstaPy` **for that session**.

+ `live_match=False`:
    + If the user **already do have** a `Followers` data loaded _earlier_ in the **same** session, it will run a _smart_ `data-matching` _algorithm_.  
    And **there**, it will **load only the new data** _from the server_ and then **return a compact result** of _current data_.  
    The _algorithm_ **works like**: _load the usernames **until hits the** ones from the **previous query** at certain amount_.  
    + **Also if** the `live_match` is `False` and the user has **no any** _sessional_ `Followers` data, **then** it will load `live` data at _requested range_.
    + As a **result**, `live_match=False` saves lots of `precious time` and `server requests`.  
+ `live_match=True`:  
    + It will **always** load `live` data from the server at _requested range_.

`store_locally`:  
Gives the _option_ to `save` the loaded `Followers` data in a **local storage**  
The files will be saved _into_ your **logs folder**, `~/InstaPy/logs/YourOwnUsername/relationship_data/Popeye/followers/` directory.  
Sample **filename** `14-06-2018~full~6874.json`:  
+ `14-06-2018` means the **time** of the data acquisition.
+ `"full"` means the **range** of the data acquisition;  
_If the data is requested at the range **else than** `"full"`, it will write **that** range_.
+ `6874` means the **count** of the usernames retrieved.
+ `json` is the **filetype** and the data is stored as a `list` in it.


There are **several** `use cases` of this tool for **various purposes**.  
_E.g._, inside your **quickstart** script, you can **do** _something like this_:
```python
#get followers of "Popeye" and "Cinderella"
popeye_followers = session.grab_followers(username="Popeye", amount="full", live_match=True, store_locally=True)
sleep(600)
cinderella_followers = session.grab_followers(username="Cinderella", amount="full", live_match=True, store_locally=True)

#find the users following "Popeye" WHO also follow "Cinderella" :D
popeye_cinderella_followers = [follower for follower in popeye_followers if follower in cinderella_followers]
```

#### PROs
You can **use** this tool to take a **backup** of _your_ **or** _any other user's_ **current** followers.


### Grab Following of a user  
###### Gets and returns `following` of the given user in desired amount, also can save locally  
```python
lazySmurf_following = session.grab_following(username="lazy.smurf", amount="full", live_match=True, store_locally=True)
##now, `lazySmurf_following` variable which is a list- holds the `Following` data of "lazy.smurf" at requested time
```
#### Parameters:  
`username`:  
A desired username to grab its following  
* It can be your `own` username **OR** a _username of some `non-private` account._

`amount`:  
Defines the desired amount of usernames to grab from the given account
* `amount="full"`:
    + Grabs following **entirely**
* `amount=3089`:
    * Grabs `3089` usernames **if exist**, _if not_, grabs **available** amount

`live_match`:  
Defines the method of grabbing `Following` data
> **Knowledge Base**:  
Every time you grab `Following` data in `"full"` range of **any** user, it is also gonna be _stored in some corner_ of `InstaPy` **for that session**.

+ `live_match=False`:
    + If the user **already do have** a `Following` data loaded _earlier_ in the **same** session, it will run a _smart_ `data-matching` _algorithm_.  
    And **there**, it will **load only the new data** _from the server_ and then **return a compact result** of _current data_.
    The _algorithm_ **works like**: _load the usernames **until hits the** ones from the **previous query** at certain amount_.  
    + **Also if** the `live_match` is `False` and the user has **no any** _sessional_ `Following` data, **then** it will load `live` data at _requested range_.
    + As a **result**, `live_match=False` saves lots of `precious time` and `server requests`.  
+ `live_match=True`:  
    + It will **always** load `live` data from the server at _requested range_.

`store_locally`:  
Gives the _option_ to `save` the loaded `Following` data in a **local storage**  
The files will be saved _into_ your **logs folder**, `~/InstaPy/logs/YourOwnUsername/relationship_data/lazy.smurf/following/` directory.  
Sample **filename** `15-06-2018~full~2409.json`:  
+ `15-06-2018` means the **time** of the data acquisition.
+ `"full"` means the **range** of the data acquisition;  
_If the data is requested at the range **else than** `"full"`, it will write **that** range_.
+ `2409` means the **count** of the usernames retrieved.
+ `json` is the **filetype** and the data is stored as a `list` in it.


There are **several** `use cases` of this tool for **various purposes**.  
_E.g._, inside your **quickstart** script, you can **do** _something like this_:
```python
##as we know that all lazy Smurf care is to take some good rest, so by mistake, he can follow somebody WHOM Gargamel also follow!
#so let's find it out to save Smurfs from troubles! :D

#get following of "lazy.smurf" and "Gargamel"
lazySmurf_following = session.grab_following(username="lazy.smurf", amount="full", live_match=True, store_locally=True)
sleep(600)
gargamel_following = session.grab_following(username="Gargamel", amount="full", live_match=True, store_locally=True)

#find the users "lazy.smurf" is following WHOM "Gargamel" also follow :D
lazySmurf_gargamel_following = [following for following in lazySmurf_following if following in gargamel_following]
```

#### PROs
You can **use** this tool to take a **backup** of _your_ **or** _any other user's_ **current** following.


### Pick Unfollowers of a user
###### Compares the `followers` stored in a local storage against current followers and returns absent followers
```python
all_unfollowers, active_unfollowers = session.pick_unfollowers(username="Bernard_bear", compare_by="month", compare_track="first", live_match=True, store_locally=True, print_out=True)
##now, `all_unfollowers` and `all_unfollowers` variables which are lists- hold the `Unfollowers` data of "Bernard_bear" at requested time
#`all_unfollowers` holds all of the unfollowers WHILST `active_unfollowers` holds the unfollowers WHOM "Bernard_bear" is still following
```
#### Parameters:  
`username`:  
A desired username to pick its unfollowers  
* It can be your `own` username **OR** a _username of some `non-private` account._

`compare_by`:
Defines the `compare point` to pick unfollowers
+ Available **value**s are:
    + `"latest"` chooses the very latest record from the existing records in the local folder
    + `"earliest"` chooses the very earliest record from the existing records in the local folder

    The compare points below needs a **compare track** defined, too:
    + `"day"` chooses from the existing records of today in the local folder
    + `"month"` chooses from the existing records of this month in the local folder
    + `"year"` chooses from the existing records of this year in the local folder

`compare_track`:
Defines the track to choose a file to compare for `"day"`, `"month"` and `"year"` compare points
+ Available **value**s are:
    + `"first"` selects the first record from the given `day`, `month` or `year`
    + `"median"` selects the median (_the one in the middle_) record from the given `day`, `month` or `year`
    + `"last"` selects the last record from the given `day`, `month` or `year`

`live_match`:  
Defines the method of grabbing **new** `Followers` data to compare with **existing** data
> **Knowledge Base**:  
Every time you grab `Followers` data in `"full"` range of **any** user, it is also gonna be _stored in some corner_ of `InstaPy` **for that session**.

+ `live_match=False`:
    + If the user **already do have** a `Followers` data loaded _earlier_ in the **same** session, it will run a _smart_ `data-matching` _algorithm_.  
    And **there**, it will **load only the new data** _from the server_ and then **return a compact result** of _current data_.  
    The _algorithm_ **works like**: _load the usernames **until hits the** ones from the **previous query** at certain amount_.  
    + **Also if** the `live_match` is `False` and the user has **no any** _sessional_ `Followers` data, **then** it will load `live` data at _requested range_.
    + As a **result**, `live_match=False` saves lots of `precious time` and `server requests`.  
+ `live_match=True`:  
    + It will **always** load `live` data from the server at _requested range_.

`store_locally`:  
Gives the _option_ to `save` the loaded `Unfollowers` data in a **local storage**  
There will be 2 files saved in their own directory:  
+ `all_unfollowers`:  
    + Will store all of the unfollowers in there  
    + Its files will be saved at **logs folder**, `~/InstaPy/logs/YourOwnUsername/relationship_data/Bernard_bear/unfollowers/all_unfollowers/` directory.    
+ `active_unfollowers`:    
    + Will store only the unfollowers WHOM you are currently following.  
    + Its files will be saved at **logs folder**, `~/InstaPy/logs/YourOwnUsername/relationship_data/Bernard_bear/unfollowers/active_unfollowers/` directory.    

Sample **filename** `03-06-2018~all~75.json`:  
+ `03-06-2018` means the **time** of the data acquisition.
+ `"all"` means that it is all of the unfollowers data;  
_*`"active"` unfollowers files will have `"active"` written in there_.
+ `75` means the **count** of the unfollowers retrieved.
+ `json` is the **filetype** and the data is stored as a `list` in it.

`print_out`:  
Use this parameter if you would like the `see` those unfollowers **printed** into the **console output** _right after finding them_.    

There are **several** `use cases` of this tool for **various purposes**.  
+ You can the get the unfollowers you have had from the **start of the** _year_, or from the **middle of the** _year_ or from the start of the **month**, etc.  
And then, e.g. do some `useful` **analysis** with that _generated unfollowers data_.
+ _And_ you can also **find** the unfollowers to `block` them **all**.
+ Also, you can **unfollow back** those `active unfollowers` _right away_:
```python
#find all of the active unfollowers of Bernard bear
all_unfollowers, active_unfollowers = session.pick_unfollowers(username="Bernard_bear", compare_by="earliest", compare_track="first", live_match=True, store_locally=True, print_out=True)
sleep(200)
#let's unfollow them immediately cos Bernard will be angry if heards about those unfollowers! :D
session.unfollow_users(amount=len(active_unfollowers), customList=(True, active_unfollowers, "all"), style="RANDOM", unfollow_after=None, sleep_delay=600)
```


### Pick Nonfollowers of a user
###### Compares the `Followers` data against `Following` data of a user and returns the `Nonfollowers` data
```python
scoobyDoo_nonfollowers = session.pick_nonfollowers(username="ScoobyDoo", live_match=True, store_locally=True)
#now, `scoobyDoo_nonfollowers` variable which is a list- holds the `Nonfollowers` data of "ScoobyDoo" at requested time
```
#### Parameters:  
`username`:  
A desired username to pick its nonfollowers  
* It can be your `own` username **OR** a _username of some `non-private` account._

`live_match`:  
Defines the method of grabbing `Followers` and `Following` data to compare with each other to find **nonfollowers**
> **Knowledge Base**:  
Every time you grab `Followers` and/or `Following` data in `"full"` range of **any** user, it is also gonna be _stored in some corner_ of `InstaPy` **for that session**.

+ `live_match=False`:
    + If the user **already do have** a `Followers` and/or `Following` data loaded _earlier_ in the **same** session, it will run a _smart_ `data-matching` _algorithm_.  
    And **there**, it will **load only the new data** _from the server_ and then **return a compact result** of _current data_.  
    The _algorithm_ **works like**: _load the usernames **until hits the** ones from the **previous query** at certain amount_.  
    + **Also if** the `live_match` is `False` and the user has **no any** _sessional_ `Followers` and/or `Following` data, **then** it will load `live` data at _requested range_.
    + As a **result**, `live_match=False` saves lots of `precious time` and `server requests`.  
+ `live_match=True`:  
    + It will **always** load `live` data from the server at _requested range_.

`store_locally`:  
Gives the _option_ to `save` the loaded `Nonfollowers` data in a **local storage**  
The files will be saved _into_ your **logs folder**, `~/InstaPy/logs/YourOwnUsername/relationship_data/ScoobyDoo/nonfollowers/` directory.  
Sample **filename** `01-06-2018~[5886-3575]~2465.json`:  
+ `01-06-2018` means the **time** of the data acquisition.
+ `5886` means the **count** of the followers retrieved.
+ `3575` means the **count** of the following retrieved.
+ `2465` means the **count** of the nonfollowers picked.
+ `json` is the **filetype** and the data is stored as a `list` in it.


There are **several** `use cases` of this tool for **various purposes**.  
+ You can get the nonfollowers of several users and then do analysis.  
    + _e.g., in this example Scooby Do used it like this_:  
    ```python
    ##Scooby Doo always wonders a lot and this time he wonders if there are people Shaggy is following WHO do not follow him back...
    shaggy_nonfollowers = session.pick_nonfollowers(username="Shaggy", live_match=True, store_locally=True)

    #now Scooby Doo will tell his friend Shaggy about this, who knows, maybe Shaggy will unfollow them all or even add to block :D
    ```


### Pick Fans of a user
###### Returns Fans data- all of the accounts who do follow the user WHOM user itself do not follow back
```python
smurfette_fans = session.pick_fans(username="Smurfette", live_match=True, store_locally=True)
#now, `smurfette_fans` variable which is a list- holds the `Fans` data of "Smurfette" at requested time
```
#### Parameters:  
`username`:  
A desired username to pick its fans  
* It can be your `own` username **OR** a _username of some `non-private` account._

`live_match`:  
Defines the method of grabbing `Followers` and `Following` data to compare with each other to find **fans**
> **Knowledge Base**:  
Every time you grab `Followers` and/or `Following` data in `"full"` range of **any** user, it is also gonna be _stored in some corner_ of `InstaPy` **for that session**.

+ `live_match=False`:
    + If the user **already do have** a `Followers` and/or `Following` data loaded _earlier_ in the **same** session, it will run a _smart_ `data-matching` _algorithm_.  
    And **there**, it will **load only the new data** _from the server_ and then **return a compact result** of _current data_.  
    The _algorithm_ **works like**: _load the usernames **until hits the** ones from the **previous query** at certain amount_.  
    + **Also if** the `live_match` is `False` and the user has **no any** _sessional_ `Followers` and/or `Following` data, **then** it will load `live` data at _requested range_.
    + As a **result**, `live_match=False` saves lots of `precious time` and `server requests`.  
+ `live_match=True`:  
    + It will **always** load `live` data from the server at _requested range_.

`store_locally`:  
Gives the _option_ to `save` the loaded `Fans` data in a **local storage**  
The files will be saved _into_ your **logs folder**, `~/InstaPy/logs/YourOwnUsername/relationship_data/Smurfette/fans/` directory.  
Sample **filename** `05-06-2018~[4591-2575]~3477.json`:  
+ `05-06-2018` means the **time** of the data acquisition.
+ `4591` means the **count** of the followers retrieved.
+ `2575` means the **count** of the following retrieved.
+ `3477` means the **count** of the fans picked.
+ `json` is the **filetype** and the data is stored as a `list` in it.


There are **several** `use cases` of this tool for **various purposes**.  
+ You can get the fans of several users and then do analysis.  
    + _e.g., in this example Smurfette used it like this_:  
    ```python
    ##Smurfette is so famous in the place and she wonders which smurfs is following her WHOM she doesn't even know of :D
    smurfette_fans = session.pick_fans(username="Smurfette", live_match=True, store_locally=True)
    #and now, maybe she will follow back some of the smurfs whom she may know :P
    ```


### Pick Mutual Following of a user
###### Returns `Mutual Following` data- all of the accounts who do follow the user WHOM user itself **also** do follow back
```python
Winnie_mutualFollowing = session.pick_mutual_following(username="WinnieThePooh", live_match=True, store_locally=True)
#now, `Winnie_mutualFollowing` variable which is a list- holds the `Mutual Following` data of "WinnieThePooh" at requested time
```
#### Parameters:  
`username`:  
A desired username to pick its mutual following  
* It can be your `own` username **OR** a _username of some `non-private` account._

`live_match`:  
Defines the method of grabbing `Followers` and `Following` data to compare with each other to find **mutual following**
> **Knowledge Base**:  
Every time you grab `Followers` and/or `Following` data in `"full"` range of **any** user, it is also gonna be _stored in some corner_ of `InstaPy` **for that session**.

+ `live_match=False`:
    + If the user **already do have** a `Followers` and/or `Following` data loaded _earlier_ in the **same** session, it will run a _smart_ `data-matching` _algorithm_.  
    And **there**, it will **load only the new data** _from the server_ and then **return a compact result** of _current data_.  
    The _algorithm_ **works like**: _load the usernames **until hits the** ones from the **previous query** at certain amount_.  
    + **Also if** the `live_match` is `False` and the user has **no any** _sessional_ `Followers` and/or `Following` data, **then** it will load `live` data at _requested range_.
    + As a **result**, `live_match=False` saves lots of `precious time` and `server requests`.  
+ `live_match=True`:  
    + It will **always** load `live` data from the server at _requested range_.

`store_locally`:  
Gives the _option_ to `save` the loaded `Mutual Following` data in a **local storage**  
The files will be saved _into_ your **logs folder**, `~/InstaPy/logs/YourOwnUsername/relationship_data/WinnieThePooh/mutual_following/` directory.  
Sample **filename** `11-06-2018~[3872-2571]~1120.json`:  
+ `11-06-2018` means the **time** of the data acquisition.
+ `3872` means the **count** of the followers retrieved.
+ `2571` means the **count** of the following retrieved.
+ `1120` means the **count** of the mutual following picked.
+ `json` is the **filetype** and the data is stored as a `list` in it.


There are **several** `use cases` of this tool for **various purposes**.  
+ You can get the mutual following of several users and then do analysis.  
    + _e.g., in this example Winnie The Pooh used it like this_:  
    ```python
    #Winnie The Pooh is a very friendly guy and almost everybody follows him back, but he wants to be sure about it :D
    Winnie_mutual_following = session.pick_mutual_following(username="WinnieThePooh", live_match=True, store_locally=True)
    ##now, he will write a message to his mutual followers to help him get a new honey pot :>
    ```

---

<br /> 
<br />

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
from instapy import smart_run
from instapy import set_workspace
import schedule
import time

#your login credentials
insta_username=''
insta_password=''

#path to your workspace
set_workspace(path=None)

def job():
  session = InstaPy(username=insta_username, password=insta_password)
  with smart_run(session):
    session.set_do_comment(enabled=True, percentage=20)
    session.set_comments(['Well done!'])
    session.set_do_follow(enabled=True, percentage=5, times=2)
    session.like_by_tags(['love'], amount=100, media='Photo')


schedule.every().day.at("6:35").do(job)
schedule.every().day.at("16:22").do(job)

while True:
  schedule.run_pending()
  time.sleep(10)
```

---

<br /> 
<br />

## Additional Information
### Advanced Installation
#### 🛠 Install or update to the unreleased version  
For example, there is a **bug** and its **fix** is _merged to the repo_ but a newer version of _InstaPy_ [_containing_ that **fix**] is not yet released to _PyPI_ to be able to be _installed_ or _updated_ by **pip**.  

Then, you can do this to install the **actual state** of the _repo_ 😋
```erlang
pip install -I https://github.com/timgrossmann/InstaPy/zipball/master
```

Worths to note that, this installation option does not require _Git_ to be installed, too.  
`-I` flag in there is used to _ignore the installed_ packages and _reinstall_ them instead.  

<details>
  <summary>
    <b>
      Learn why <code>-I</code> flag is required 🔎
    </b>
  </summary>

Since _InstaPy_'s version is not yet being incremented which is the reason you're installing it from a _zipball_, then if you don't use the `-I` flag, **pip** will complain saying,  
- "_Hey, I have already installed the x.y.z version! Skipping installation..._"  

But obviously, even though the version is the same, _zipball_ has the current state of the repository.  
That's why you will be able to install the actual state of the repo using the `-I` flag.

</details>

<br />

>**PRO** Tip:  
  Read the section - [How to avoid _python_ & **pip** confusion](#how-to-avoid-python--pip-confusion) 😄

<br />

#### ⚗ Install manually and manage using advanced git commands
###### For those who want to tweak or enhance _InstaPy_.

**1**. Clone _InstaPy_ repository into your computer
```erlang
git clone https://github.com/timgrossmann/InstaPy.git
```

**2**. Navigate to the _InstaPy_ project root directory
```erlang
cd InstaPy
```

**3**. Install the _local_ **instapy** package
```erlang
pip install -e .
```
<details>
  <summary>
    <b>
      Learn why <code>-e</code> flag is required 🔎
    </b>
  </summary>

Since you're gonna install the local version of _InstaPy_ you'll probably change its code per your need which is the reason you do an advanced installation from a _Git_ source, then if you don't use the `-e` flag, you'll have to install that local package by **pip** every time after making a change.  

But fortunately, `-e` flag comes to help;  
`-e` means _editable_ install, so that after editing files you don't need to re-install the package again since it will always refer to the edited files cos with the _editable_ install, it just **links** the project's location to **pip**'s install location _rather than_ adding them to **pip** location separately..
<br />
</details>
or

```erlang
python setup.py install
```

<br />

#### ⛑ Install into a Virtual Environment

###### The best way to install _InstaPy_ is to create a virtual environment and install _InstaPy_ there, then, run it from a separate file.

<details>
  <summary>
    <b>
      Guide for <b>Pythons</b> >= 3.6 🔎
    </b>
  </summary>

##### Mac/Linux

**1**. Clone _InstaPy_ repository into your computer
```erlang
git clone https://github.com/timgrossmann/InstaPy.git
```

**2**. Navigate to the _InstaPy_ project root directory
```erlang
cd InstaPy
```

**3**. Make a virtual environment
```erlang
python3 -m venv venv
```

**4**. Activate the virtual environment
```erlang
source venv/bin/activate
```

**5**. Install the _local_ **instapy** package
```erlang
pip install -e .
```



##### Windows

**1**. Clone _InstaPy_ repository into your computer
```erlang
git clone https://github.com/timgrossmann/InstaPy.git
```

**2**. Navigate to the _InstaPy_ project root directory
```erlang
cd InstaPy
```

**3**. Make a virtual environment
```erlang
python3 -m venv venv
```

**4**. Activate the virtual environment
```erlang
venv\Scripts\activate.bat
```

**5**. Install the _local_ **instapy** package
```erlang
pip install -e .
```


If you're not _familiar_ with **venv**, please [read about it here](https://docs.python.org/3/library/venv.html) and use it to your advantage;    

- Running `source venv/bin/activate` will _activate_ the correct _python_ to run _InstaPy_. To exit an activated **venv** run `deactivate`.  
- Now, copy & paste the **quickstart.py** _python_ code below and then run your first _InstaPy_ script.  
  Remember to run it with _python_ from the **venv**.  
- To make sure which _python_ is used, run `which python` which will tell you the active version of _python_.  
- Whenever you run the script, the virtual environment must be _active_.

</details>


<details>
  <summary>
    <b>
      Guide for <b>Pythons</b> < 3.6 🔎
    </b>
  </summary>

**1**. Make a virtual environment
```erlang
virtualenv venv
```

**2**. Activate the virtual environment
```erlang
source venv/bin/activate
```

**3**. Install the **instapy** package from _Git_ by using **pip**
```erlang
pip install git+https://github.com/timgrossmann/InstaPy.git
```


If you're not _familiar_ with **virtualenv**, please [read about it here](https://virtualenv.pypa.io/en/stable/) and use it to your advantage;  

In essence,    
 - This is be the **only** _python_ library you should install as `root` (_e.g., with `sudo`_).  
 - All other _python_ libraries should be inside a **virtualenv**.  
 - Running `source venv/bin/activate` will activate the correct _python_ to run _InstaPy_.  
    And to exit an activated **virtualenv** run `deactivate`.  
 - Now, copy & paste the **quickstart.py** _python_ code below and run your first _InstaPy_ script.  
 Remember to run it with _python_ from the **virtualenv**, so from **venv/bin/python**.  
 - To make sure which _python_ is used, run `which python` which would tell you the active version of _python_.

</details>

<br />

#### **Install** a _**specific** version_
```elm
pip install instapy==0.1.1
```

#### **Uninstall**
```elm
pip uninstall instapy
```


## Workspace folders
### Migrating your data to the workspace folder
After installing InstaPy with pip, you have to run it once by calling `python quickstart.py`. Once the web browser opens, you can abort the session by closing the browser or your terminal. 

You will now find an `InstaPy` folder located at the above mentioned home folder.
Simply copy and paste the content of your logs folder into that workspace folder in order to assure that all your data is migrated.

> Please note that you only have to do this once. After that, you can get rid of your old, downloaded version of this repository since the InstaPy folder in your home folder will now be the default location for your data.


###### _InstaPy_ stores user's data files inside the **workspace** folder.

By default, it is gonna be the **InstaPy** folder at your home folder.  
Such as, if your username is `Cherry`, let's show where your InstaPy folder would be,

|   OS    |       home folder     | _InstaPy_ **workspace** folder |
| ------- | --------------------- | ------------------------------ |
| Windows | `C:\\Users\\Cherry\\` | `C:\\Users\\Cherry\\InstaPy\\` |
|   Mac   |    `/Users/Cherry/`   |    `/Users/Cherry/InstaPy/`    |
|  Linux  |    `/home/Cherry/`    |    `/home/Cherry/InstaPy/`     |

Note that, at the start of each run, it shows you the **workspace** folder in use.

<br /> 

<details>
  <summary>
    <b>
      What will be stored at the <b>workspace</b> folder? 🔍
    </b>
  </summary>

Anything that is _user's **data file**_ will be stored in there.  
Such as,  
- **logs** folder - _log and other storage files_  
- **assets** folder - _e.g. user chosen chromedriver executable(s)_  
- **db** folder - _databases_  
- etc.  

</details>


### Set a _custom_ workspace folder
You can use `set_workspace()` function to set a custom **workspace** folder,
```python
from instapy import InstaPy
from instapy import set_workspace

set_workspace("C:\\My\\Custom\\Path\\InstaPy\\")

session = InstaPy(...)
```

<details>
  <summary>
    <b>
      Rules 🔎
    </b>
  </summary>

**1**-) You have to set your custom **workspace** folder before instantiates _InstaPy_.  
**2**-) Your custom **workspace** folder must have `InstaPy` (*_case sensitive_) word in its name.  
+ If your path does not have it,  
`set_workspace("C:\\Other\\Path\\InstaPie\\")`  
then your **workspace** folder will be named and made as,  
`"C:\\Other\\Path\\InstaPie\\InstaPy\\"`  
👆🏼 `InstaPy` directory will be added as a new subdirectory in there, and be your **workspace** folder.

+ If your custom **workspace** folder name has a case-insensitive default name in it- `Instapy`, `instapy`, `instaPY`, etc.,  
`set_workspace("C:\\Other\\Path\\instapy2\\")`  
then your **workspace** folder will be,   
`"C:\\Other\\Path\\InstaPy2\\"`  
as you can see, it normalizes name and sets the **workspace** folder.


##### _Why naming is so important?_
 - It will help to easily adapt to the flexible _InstaPy_ usage with that default formal name.

</details>


### Set a custom **workspace** folder _permanently_ with ease
If you want to set your custom **workspace** folder permanently and more easily, add a new environmental variable named `INSTAPY_WORKSPACE` with the value of the path of the desired **workspace** folder to your operating system.  
Then that will be the default **workspace** folder in all sessions [unless you change it using `set_workspace()` or so].


### _Get_ the location of the workspace folder in use
If you ever want to **get** the _location_ of your **workspace** folder, you can use
the `get_workspace()` function,
```python
from instapy import InstaPy
from instapy import smart_run
from instapy import set_workspace
from instapy import get_workspace

set_workspace(path="C:\\Custom\\Path\\InstaPy_super\\")

session = InstaPy(username="abc", password="123")

with smart_run(session):
    # lots of code
    workspace_in_use = get_workspace()
    print(workspace_in_use["path"])
    # code code
```
Note that, `get_workspace()` is a function used _internally_ and makes a **workspace** folder [by default at home folder] if not exists.  
It means, you must use only the `set_workspace()` feature to set a custom **workspace** folder and not try to use `get_workspace()` for that purpose..


### Set a custom _location_ 
You can set any of the **custom** _locations_ you like, **any time**!  
E.g. setting the _location_ of the **database** file,  
```python
from instapy import InstaPy
from instapy import set_workspace
from instapy import Settings


set_workspace(...)   # if you will set a custom workspace, set it before anything
Settings.db_location = "C:\\New\\Place\\DB\\instapy.db"

session = InstaPy(...)
# code code
```


<details>
  <summary>
    <b>
      Restrictions 🔎
    </b>
  </summary>

**a**-) You cannot set a custom **workspace** folder after _InstaPy_ has been instantiated;  
_E.g. while instantiating _InstaPy_, you make a logger at that given location and trying to change the_ `log_location` _really needs to restart the LOGGER adapter and make another logger instance, but it can be achieved in future_.

**b**-) If you set a custom **workspace** once and then set it again then your data locations will still use the previous locations:
```python
from instapy import InstaPy
from instapy import set_workspace
from instapy import Settings

# first time settings custom workspace folder
set_workspace("C:\\Users\\MMega\\Desktop\\My_InstaPy\\")
# second time settings custom workspace folder
set_workspace("C:\\Users\\MMega\\Documents\\My_InstaPy\\")

# locations of data files, e.g. chromedriver executable, logfolder, db will use first custom workspace locations.
# if you still want to change their location to second one, then do this one by one:
Settings.log_location = "C:\\Users\\MMega\\Documents\\My_InstaPy\\logs\\"
Settings.database_location = "C:\\Users\\MMega\\Documents\\My_InstaPy\\db\\instapy.db"
Settings.chromedriver_location = "C:\\Users\\MMega\\Documents\\My_InstaPy\\logs\\chromedriver.exe"
```
As you can see, you have to use `set_workspace()` only once.  
Why it is so difficult in those 👆🏼 regards?  
 - It's to preserve custom location assignments alive (`Settings.*`) cos otherwise setting another **workspace** would override any previously _manually_ assigned location(s). 

</details>


### Pass arguments by CLI
###### It is recommended to pass your credentials from command line interface rather than storing them inside quickstart scripts.  

Note that, arguments passed from the CLI has higher priorities than the arguments inside a **quickstart** script.  
E.g., let's assume you have,
```python
# inside quickstart script

session = InstaPy(username="abc")
```
and you start that **quickstart** script as,
```erlang
python quickstart.py -u abcdef -p 12345678
```
Then, your _username_ will be set as `abcdef` rather than `abc`.  
_And obviously, if you don't pass the flag, it'll try to get that argument from the **quickstart** script [if any]_.

#### Currently these _flags_ are supported:
  🚩 `-u` abc, `--username` abc
   - Sets your username.

  🚩 `-p` 123, `--password` 123
   - Sets your password.

  🚩 `-pd` 25, `--page-delay` 25
   - Sets the implicit wait.

  🚩 `-pa` 192.168.1.1, `--proxy-address` 192.168.1.1
   - Sets the proxy address.

  🚩 `-pp` 8080, `--proxy-port` 8080
   - Sets the proxy port.

  🚩 `-hb`, `--headless-browser`
   - Enables headless mode.

  🚩 `-dil`, `--disable-image-load`
   - Disables image load.

  🚩 `-bsa`, `--bypass-suspicious-attempt`
   - Bypasses suspicious attempt.

  🚩 `-bwm`, `--bypass-with-mobile`
   - Bypasses with mobile phone.

To get the list of available commands, you can type,
```erlang
python quickstart.py -h
# or
python quickstart.py --help
```

#### Examples
⚽ Let's quickly set your username and password right by CLI,   
```erlang
python quickstart.py -u Toto.Lin8  -p 4X27_Tibor
# or
python quickstart.py --username Toto.Lin8  --password 4X27_Tibor
# or
python quickstart.py -u "Toto.Lin8"  -p "4X27_Tibor"
```

<details>
<summary>
  <b>
    Advanced 🔎
  </b>
</summary> 

You can **pass** and then **parse** the **_custom_** CLI arguments you like right inside the **quickstart** script.  
To do it, open up your **quickstart** script and add these lines,
```python
# inside quickstart script

import argparse

my_parser = argparse.ArgumentParser()
# add the arguments as you like WHICH you will pass
# e.g., here is the simplest example you can see,
my_parser.add_argument("--my-data-files-name")
args, args_unknown = my_parser.parse_known_args()

filename = args.my_data_files_name

# now you can print it
print(filename)

# or open that file
with open(filename, 'r') as f:
    my_data = f.read()
```
After adding your custom arguments to the **quickstart** script, you can now **pass** them by CLI, comfortably,
```erlang
python quickstart.py --my-data-files-name "C:\\Users\\Anita\\Desktop\\data_file.txt"
```
>**NOTE**:  
Use **dash** in flag and parse them with **underscores**;  
E.g., we have used the flag as **`--my-data-files-name`** and parsed it as `args.`**`my_data_files_name`** ...

>**PRO**:
See `parse_cli_args()` function [used internally] inside the **util.py** file to write & parse more advanced flags.  
You can also import that function into your **quickstart** script and parse the **formal** flags into there to be used, as well.

```python
# inside quickstart script

from instapy.util import parse_cli_args


cli_args = parse_cli_args()
username = cli_args.username

print(username)
```
👆🏼👉🏼 as you will pass the _username_ like,
```erlang
python quickstart.py -u abc
```

</details>


## Extensions
[1. Session scheduling with Telegram](https://github.com/Tkd-Alex/Telegram-InstaPy-Scheduling)


### Custom geckodriver
By default, InstaPy downloads the latest version of the geckodriver.
Unless you need a specific version of the geckodriver, you're ready to go.

You can manually download the geckodriver binary and put the path as an argument to the InstaPy contructor:

```python
session = InstaPy(..., geckodriver_path = '/path/to/binary', ...)
```

### Using one of the templates

If you're interested in what other users setup looks like, feel free to check out the `quickstart_templates` folder which includes several working setups with different features.

In order to use them, just copy the desired file and put it next to the `quickstart.py` file in the, what is called root, directory.

Finally simply adjust the username and any tags or firend lists before executing it.
That's it.


### How not to be banned
Built-in delays prevent your account from getting banned. 
However, excessive use of this tool may result in action blocks or permanent bans.
Use the Quota Supervisor feature to set some fixed limits for the bot for maximum safety.


### Disable Image Loading
If you want to save some bandwidth, you can simply disable the image/video loading. This will lead to, if you watch InstaPy running, not downloading and displaying any more images and videos.

> Note: This can save a tremendous amount of data. This is turned off by default (`False`).

To do this simply pass the `disable_image_load=True` parameter in the InstaPy constructor like so:
```python
session = InstaPy(username=insta_username,
                  password=insta_password,
                  headless_browser=False,
		  disable_image_load=True,
                  multi_logs=True)
```

### Changing DB or location
If you want to change the location/path of the DB, simply head into the `instapy/settings.py` file and change the following lines.
Set these in instapy/settings.py if you're locating the library in the /usr/lib/pythonX.X/ directory.
```
Settings.database_location = '/path/to/instapy.db'
```

### Split SQLite by Username 
If you experience issue with multiple accounts Instapy.db lockup. You can add the following flag

`-sdb` when running in Command line

or 

To do this simply pass the `split_db=True` parameter in the InstaPy constructor like so:

```python
session = InstaPy(username=insta_username,
                  password=insta_password,
                  headless_browser=False,
		  split_db=True,
                  multi_logs=True)
```



### How to avoid _python_ & **pip** confusion

Sometimes you have **multiple** _python_ installations in your system.  
Then you'll obviously have crazy aliases linked to _python_ and **pip** commands.  

For example, let's assume you have _python_ 2.7 & _python_ 3.7 installed in your system,  

| _python_ version | _python_ alias | **pip** alias |
| ---------------- | -------------- | ------------- |
|       2.7        |     `py2`      |     `pip`     |
|       3.7        |    `python`    |     `pip3`    |

And once you install a package by the `pip` command and try to run it with `python` command, it will confuse you.  

Why? - cos,  
- `pip` command is for _python_ 2.7  
- `python` command is for _python_ 3.7  

To solve that confusion, use this **style** to install packages by **pip**,
```powershell
# install "instapy" package into python 3.7
python -m pip install instapy

# install "instapy" package into python 2.7
py2 -m pip install instapy
```

As you can see, it is,  
`python -m pip ...`  
rather than,  
`pip ...`

Other **pip** commands can be accomplished the same way, too.  
Such as,
```powershell
# update "instapy" package
python -m pip install instapy -U

# uninstall "instapy" package
python -m pip uninstall instapy

# show details of the "instapy" package installed by pip
python -m pip show instapy
```

Using this style, you will never have to worry about what is the correct alias of the **pip** for you specific _python_ installation and all you have to know is just the _python_'s alias you use.  

### Dealing with Selenium Common Exception Issues

##### selenium.common.exceptions.WebDriverException: Message: unknown error: Cannot read property 'entry_data' of undefined
This error could also caused by unstable Internet connection or Instagram's web changed their data-structure.

##### TL;DR - Make sure your chromedriver version is compatible with your Google Chrome version.
Occasionally *Instapy* will stop working because one of the issues below has been thrown.

>_Traceback (most recent call last):
....// File list with the exception trace
selenium.common.exceptions.WebDriverException: Message: unknown error: Cannot read property 'entry_data' of undefined
(Session info: headless **chrome=75.0.3770.80**)
(Driver info: **chromedriver=2.36.540469** (1881fd7f8641508feb5166b7cae561d87723cfa8),platform=Mac OS X 10.14.5 x86_64)

>_Traceback (most recent call last):
....// File list with the exception traceselenium.common.exceptions.WebDriverException: Message: unknown error: unknown sessionId
(Session info: headless **chrome=75.0.3770.80**)
(Driver info: **chromedriver=2.36.540469** (1881fd7f8641508feb5166b7cae561d87723cfa8),platform=Mac OS X 10.14.5 x86_64)

Notice that *chrome* version is **75** and the *chromedriver* version is **2.36**. 

According to the [release notes](https://chromedriver.storage.googleapis.com/2.36/notes.txt) for chromedriver, version 2.36 only supports Chrome versions 63-65.

Which means, there is a mismatch in chromedriver and Chrome that installed on my machine. 

There several steps to this fix.

1. Completely uninstall Google Chrome.
2. Download an older version.
3. Prevent Google Chrome from auto-updating.


#### MAC FIX
Since *Instapy* seems to work well, in my experience on my Mac, with chromedriver version 2.36, I will downgrade my Google Chrome. I do not use Google Chrome, so this isn't an issue.


1. **Uninstall Google Chrome**
	I used an app called [App Cleaner]("https://freemacsoft.net/appcleaner/") to remove Chrome.
	After you install App Cleaner, simply drag Google Chrome, from the Applications folder to App Cleaner and Remove All
	
2. **Download Chrome 65** *(Read this step completely before proceeding)*
	- Find and install Chrome 65 from [sllimjet.com]("https://www.slimjet.com/chrome/google-chrome-old-version.php") 

	- After you have installed Chrome 65, open and click the Apple Security Ok button that alerts you to the fact this was downloaded from the internet.
	- THEN, immediately close Google Chrome completely by holding **`CMD+Q`**. This is extremely important! Google Chrome will being its auto-update function. So it must be completely closed, not just the window.
	*We need Chrome to run first and put all its files where it needs them.*
	
3. **Prevent Google Chrome from updating**
	- Open **Terminal** and type 
	`sudo chmod -R 000 ~/Library/Google`
	
	- You will be asked for your computer password, enter it.
	
	- Next run the command
	`sudo rm -rf /Library/Google/`
	
	Google Chrome should not be able to auto-update now.

If for some reason Chrome is still updating, or you're unable to run the command in step 3, you can edit your `/etc/hosts file` to include the following line: `0.0.0.0 tools.google.com`


#### Windows Fix
Coming soon

#### Raspberry Pi Fix
Coming Soon


---

###### Have Fun & Feel Free to report any issues  
