---
title: Actions
---

### Like by Tags

```python
# Like posts based on hashtags
session.like_by_tags(['natgeo', 'world'], amount=10)
```

#### Parameters:
 `tags`: The tags that will be searched for and posts will be liked from

  `use_random_tags`: The tags that will be searched for and posts will be randomized

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
session.like_by_locations(['224442573'], amount=5, skip_top_posts=False, randomize=True)
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

### Follow by Tags

```python
# Follow user based on hashtags (without liking the image)

session.follow_by_tags(['tag1', 'tag2'], amount=10)
```

#### Parameters:
 `tags`: The tags that will be searched for and authors of the posts will be followed.

  `amount`: The amount of posts that the author of the post will be followed

  `skip_top_posts`: Determines whether the first 9 top users of posts should be followed or not (default is True)

  `use_smart_hashtags`: Make use of the [smart hashtag feature](#smart-hashtags)

  `use_smart_location_hashtags`: Make use of the [smart location hashtag feature](#smart-location-hashtags)

  `interact`: Defines whether the users of the given post should also be interacted with (needs `set_user_interact` to be also set)

  `randomize`: Determines whether the first `amount` of post authors should be liked or a random selection.

  `media`: Determines which media should be considered, Photo or Video (default is `None` which is all)


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

session.follow_by_list(followlist=['samantha3', 'larry_ok'],
                       times=2,
                       sleep_delay=600,
                       interact=True)
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

session.follow_likers(['user1' , 'user2'],
                      photos_grab_amount = 2,
                      follow_likers_per_photo = 3,
                      randomize=True,
                      sleep_delay=600,
                      interact=True)
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

### Interact by Likers
###### Get a user's posts, get the posts' likers and interact with them.

```python
session.interact_user_likers(usernames=["somebody", "other buddy"],
                             posts_grab_amount=10,
                             interact_likers_per_post=5,
                             randomize=True)
```
#### Parameters
`usernames`
: A list containing the _usernames_ of users on whose **posts'** _likers will be interacted with_;

`posts_grab_amount`
: Number of the posts to get from **each user** for getting its likers to interact with;

`interact_likers_per_post`
: Choose how many likers to get from **each post**;

`randomize`
: Shuffles the **order** of the **_posts_** from users' feed;


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
