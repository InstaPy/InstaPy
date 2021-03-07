---
title: Relationship Tools
---

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

`verified_only`:
Gives the _option_ to only return followers with a Verified status.
* `verified_only=True`:
    + Only returns followers that contain `is_verified` key
* `verified_only=False`:
    + Default option, Returns all followers for user


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
