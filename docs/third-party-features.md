---
title: Third Party Features
---

### Clarifai ImageAPI

<img src="https://clarifai.com/cms-assets/20180311184054/Clarifai_Pos.svg" width="200" align="right" />

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

##### Check out [https://clarifai.com/demo](https://clarifai.com/demo) to see some of the available tags.


### Text Analytics
#### Yandex Translate API

<img src="https://yastatic.net/www/_/Q/r/sx-Y7-1azG3UMxG55avAdgwbM.svg" width="196" align="right" />

<img src="https://yastatic.net/s3/home/logos/services/1/translate.svg" width="66" align="left" />

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

#### MeaningCloud Sentiment Analysis API
<img src="https://www.meaningcloud.com/developer/img/LogoMeaningCloud210x85.png" width="210" align="right" />

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
is not able to send messages as long as you haven't done at least one `/start`.
