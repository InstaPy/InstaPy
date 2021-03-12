---
title: Settings
---

### Liking
This method is only needed for the `interact_by_...` actions.
Posts will be liked by default when using `like_by_...` actions.

```python
# ~70% of the by InstaPy viewed posts will be liked

session.set_do_like(enabled=True, percentage=70)
```


### Commenting

```python
# enable comments (by default enabled=False) and set commenting probability to 25% so ~ every 4th image will be commented on

session.set_do_comment(enabled=True, percentage=25)
```
``` python
# Configure a simple list of optional comments, one will be selected at random when commenting:
session.set_comments(['Awesome', 'Really Cool', 'I like your stuff'])
```

Or configure conditional comments to provide a more contextual commenting based on the caption of the image:
Conditional comments are created as a list of dictionaries, each one contains a definition of
[mandatory words](#mandatory-words) and a list of comments.
The list of conditional comments is scanned until the first item that satisfies the mandatory words condition is found
and then one of the comments associated with that item is selected at random to be used.
This can best be understood with an example:
``` python
comments=[
    # either "icecave" OR "ice_cave" will satisfy this:
    {'mandatory_words': ["icecave", "ice_cave"], 'comments': ["Nice shot. Ice caves are amazing", "Cool. Aren't ice caves just amazing?"]},

    # either "high_mountain" OR ("high" AND "mountain") will satisfy this:
    {'mandatory_words': ["high_mountain", ["high", "mountain"]], 'comments': ["I just love high mountains"]},

    # Only ("high" AND "tide" together) will satisfy this:
    {'mandatory_words': [["high", "tide"]], 'comments': ["High tides are better than low"]}

    # Only "summer" AND ("lake" OR "occean") will satisfy this:
    {'mandatory_words': [["summer", ["lake", "occean"]], 'comments': ["Summer fun"]}

]
session.set_comments(comments)
```

You can also set comments for specific media types (Photo / Video)
``` python
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

<ins
  class="adsbygoogle"
  data-ad-layout="in-article"
  data-ad-format="fluid"
  data-ad-client="ca-pub-4875789012193531"
  data-ad-slot="9530237054"
></ins>
<script>
  (adsbygoogle = window.adsbygoogle || []).push({});
</script>

### Quota Supervisor
###### Take full control of the actions with the most sophisticated approaches

```python
session.set_quota_supervisor(enabled=True,
                            sleep_after=["likes", "comments_d", "follows", "unfollows", "server_calls_h"],
                            sleepyhead=True,
                            stochastic_flow=True,
                            notify_me=True,
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
will like the image if the mandatory words condition is met.
The mandatory words list can be a simple list of words or a nested structure of lists within lists.
* When using a simple word list the condition between the words is "OR" so if any of the words from the list exists in
the image text it will be matched.
* When using a nested list of lists the top level list condition is "OR" and the condition alternates between "AND"
and "OR" with every nesting level.

For example:
~~~
     # either "icecave" or "ice_cave" will satisfy this:
     ["icecave", "ice_cave"]

    # either "high_mountain" OR ("high" AND "mountain") will satisfy this:
    ["high_mountain", ["high", "mountain"]]

    # Only ("high" AND "tide" together) will satisfy this:
    [["high", "tide"]]

    # Only "summer" AND ("lake" OR "occean") will satisfy this:
    [["summer", ["lake", "occean"]]
~~~

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

<ins
  class="adsbygoogle"
  data-ad-layout="in-article"
  data-ad-format="fluid"
  data-ad-client="ca-pub-4875789012193531"
  data-ad-slot="9530237054"
></ins>
<script>
  (adsbygoogle = window.adsbygoogle || []).push({});
</script>

### Simulation
##### During indirect data retrieval, **simulation** happens to provide a _genuine_ activity flow triggered by a wise algorithm.
To **turn off** simulation or to **decrease** its occurrence frequency, use `set_simulation` setting:
```python
#use the value of `False` to permanently turn it off
session.set_simulation(enabled=False)

#use a desired occurrence percentage
session.set_simulation(enabled=True, percentage=66)
```


### Skipping user for private account, no profile picture, business account, bio keywords

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
                       dont_skip_business_categories=[],
                       skip_bio_keyword=[],
                       mandatory_bio_keywords=[])
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
                        dont_skip_business_categories=['Creators &  Celebrities'])
 ```
 This will skip all non business and business accounts except categories in _dont_skip_business_categories_.

###### Skip based on bio keywords
```python
session.set_skip_users(skip_bio_keyword=["lifestyle"],
                       mandatory_bio_keywords=["art", "photography"])
```
This will skip users that have "lifestyle" and users that don't have "art" or "photography" in their bio or username.
See the [Mandatory Words](#mandatory-words) section for details on how to define complex mandatory words conditions.

<ins
  class="adsbygoogle"
  data-ad-layout="in-article"
  data-ad-format="fluid"
  data-ad-client="ca-pub-4875789012193531"
  data-ad-slot="9530237054"
></ins>
<script>
  (adsbygoogle = window.adsbygoogle || []).push({});
</script>

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
> This will only comment on posts that contain **either** cat or dog in the post description or first comment.
> You can also require sets of words. See the [Commenting](#commenting) section for detains on how to do that


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


### Target Lists
#### This is used to parse text files containing target lists of users, hashtags, comments etc
For example:
```python
# Like posts based on hashtags
hashtags = session.target_list("C:\\Users\\......\\hashtags.txt")
session.like_by_tags(hashtags, amount=10)

# Follow the followers of each given user
users = session.target_list("C:\\Users\\......\\users.txt")
session.follow_user_followers(users, amount=10, randomize=False)
```
Note that your text file should look like this:
```
hashtag1
hashtag2
hashtag3
```
or
```
user1
user2
user3
```
Functions you can use ```target_list``` with:

```story_by_user```, ```story_by_tag```, ```like_by_tags```, ```follow_by_tags```, ```follow_user_followers```, ```follow_user_following```, ```follow_likers```, ```follow_commenters```, ```follow_by_list```, ```set_skip_users```, ```set_ignore_users```, ```set_dont_include```, ```interact_by_users```, ```interact_by_users_tagged_posts```, ```interact_user_followers```, ```interact_user_following```, ```interact_by_comments```, ```set_comments```, ```set_comment_replies```, ```set_mandatory_words```, ```unfollow_users```
