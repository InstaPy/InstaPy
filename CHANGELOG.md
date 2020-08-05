# Changelog

The **goal** of this file is explaining to the users of our project the notable changes _relevant to them_ that occurred _between_ commits.

_The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)_.

## Unreleased

### Fixed
- Unfollowing of users that haven't posted anything
- `get_links` xpath for yet another change
- Path for Obtaining user id


## [0.6.10] - 2020-07-30

### Added
- Generallize mandatory words and add mandatory_bio_keywords

### Changed 
- Update xpath for like/unlike and comment
- Fix `like_by_feed()` xpath
- `get_like_on_feed()` improve function readability

### Fixed
- "UnboundLocalError: local variable 'commenting_approved' referenced before assignment" error when bot tries to comment
- Typo updating configuration object. Changed nofity into notify
- Add specific firefox preference agent data to prevent error
- Smart location url 
- Error "Hide Selenium Extension: Error" mentioned in #5304
- XPATH for like svg

## [0.6.9] - 2020-06-12

### Added

- Additional parameter `browser_executable_path` now available when initializing InstaPy. Use it to run a specific installation of Firefox.
- A new feature - `target_list()` to parse text files containing target lists of users, hashtags etc.


### Changed
- Remove `view-source` which stops bot from proceeding 
- Remove instagram status check


## [0.6.8] - 2020-01-28

### Fixed

- xPath for breaking LIKE and COMMENT


## [0.6.7] - 2020-01-05

### Fixed

- Adjusted follow xPath


## [0.6.6] - 2019-11-11

### Changed

- Additional web checks default `False` to avoid erros on runtime


## [0.6.5] - 2019-10-20

### Added

- Additional CLI-Argument for connection checks

### Changed

- Post types now as Enum in separate file

### Fixed

- Internet connection checks
- Small typos in documentation
- Firefox Proxy error


## [0.6.4] - 2019-09-15

### Fixed

- prettyfied code
- fixed onetap account page on login
- fix minor bug in unfollow function


## [0.6.3] - 2019-09-08

### Added

- Improved documentation
- Added "no_comments" for Pods
- Improved Tox / Travis testing
- Improved random sleep delay
- Telegram support

### Fixed

- Able to use Domains as a Proxy
- jsonschema requrements version
- skip_top_posts function
- Backup plan for graphql additional / shared data


## [0.6.2] - 2019-08-30

### Added

- New bypass challenge approach (choose sms or email option)
- Show InstaPy version on initialization

### Fixed

- Login xpath update


## [0.6.1] - 2019-08-12

### Added

- Add log information about the non-working feature (unfollow with All Following option enabled)

### Fixed

- Fix an issue with screen shot file creation
- Fix an issue with JSON file state creation
- Fix Get Query Hash function to work on all Python 3.x versions
- Fix Unfollow with option nonFollowers


## [0.6.0] - 2019-08-12

### Added

- Firefox Extension which hides Selenium
- Black code formatter
- Mobile user agent
- Mobile Mode to enable mobile features
- Screen shots (rotative screen shots are taken and saved in your InstaPy user folder)
- Connection State

### Breaking Changes

- removed chromedriver
- signature changes:
  - set_action_delays(random_range) -> (random_range_from, random_range_to)
  - set_delemit_liking(max, min) ->(max_likes, min_likes)
  - set_delemit_commenting(max, min) ->(max_comments, min_comments)
  - unfollow_users(customList, instapyfollowed) -> (custom_list_enabled, custom_list, custom_list_param, instapy_followed_enabled, instapy_followed_param)
  - set*quota_supervisor(peak*_) ->(peak\_\_\_hourly, peak_\*\_daily)

### Fixed

- Fix follow_likers feature
- Fix follow_user_followers
- Fix comment_image feature
- Update dont_unfollow_active_users to Mobile Mode
- Fix scroll down (util) function
- Remove bypass_by_mobile, it will auto detect the mobile if required now
- Update profile scrapping to use GraphQL (get_users_through_dialog_with_graphql)

## [0.5.8] - 2019-08-01

### Added

- skip user based on profile bio

### Fixed

- xpath error likers from photo

## [0.5.7] - 2019-07-24

### Fixed

- user agent error in firefox

## [0.5.6] - 2019-07-22

### Fixed

- xpath compile multiple errors

### Added

- feature watch stories
- always use the lastest user-agent

## [0.5.5] - 2019-07-11

### Fixed

- `get_action_delay` check for uninitialized delays in settings

## [0.5.4] - 2019-07-03

### Changed

- Always start chromedriver with --no-sandbox to fix #4607

### Fixed

- `get_action_delay` method always returning default values #4540

## [0.5.3] - 2019-07-02

### Fixed

- Argument Being Interpreted as Sequence in `bypass_suspicious_login`

## [0.5.2] - 2019-06-28

### Fixed

- `session.get_relationship_counts()` broken behavior

## [0.5.1] - 2019-06-18

### Added

- Documentation for basic Selenium Errors
- Import `Settings` in docs

### Fixed

- `session.follow_user_following()` broken behavior

## [0.5.0] - 2019-06-03

### Added

- Additional check for like block.

### Changed

- Remove support for python2
- Information regarding the nogui parameter in documentation.
- XPath Isolation
- Remove redundant assignment of pod_post_ids
- Remove address var assigned multiple times without intermediate usage
- `set_mandatory_language` can maintain multiple character sets
- Feature finetuning comments for pods

### Fixed

- Interact_by_comments aborts when self.abort is true
- Media type filter (Photo, Video) in get_links
- 'Failed to get comments' issue
- Threaded session ending with exception `ValueError: signal only works in main thread`
- `like_image` in dev has this arg
- Verifying mandatory words when the script can not get post description
- Codacy checks for unused var, out of scope, and missing args

## [0.4.3] - 2019-05-15

### Fixed

- Commenting issue #4409

## [0.4.2] - 2019-04-15

### Fixed

- Fail of whole pod run on exception

## [0.4.1] - 2019-04-06

### Added

- Support for split database with -sdb flag to avoid SQLite lock up

### Fixed

- "Failed to find login button" when trying to login (add KEYS.ENTER to submit login data)

## [0.4.0] - 2019-04-03

### Added

- Improved info provided by log messages in instapy.py and like_util.py
- Possibility to skip non bussiness accounts

### Changed

- Remove docker from core, moved into instapy-docker repo
- Remove quickstart templates and only reference instapy-quickstart
- Restructure README and add new DOCUMENTATION file

### Fixed

- "UnboundLocalError: local variable 'tag' referenced before assignment" when there is no smart-hastag genereated
- xPath to dialog_address

## [0.3.4] - 2019-03-17

### Added

- (re) add page_reload, after cookie load, on login_user()

### Fixed

- "Failed to load desired amount of users" when trying to read long follower lists

## [0.3.3] - 2019-03-14

### Added

- Add additional exception catch to Login check

### Changed

- Set language on the browser (no clicks required)

### Fixed

- Get_active_users hotfix

## [0.3.2] - 2019-03-12

### Fixed

- Hot fix problems with browser abstraction class

## [0.3.1] - 2019-03-12

### Fixed

- Removed retry decorator

## [0.3.0] - 2019-03-11

### Added

- Allowing `follow_by_tags` to interact with the user
- Context manager to interaction calls in `like_by_tags` and `follow_likers`
- Engagement pods feature 🙌
- Smart Hashtags based on locations `set_smart_location_hashtags`
- Verify action for unfollow and follow actions
- Browser abstraction and Decorator that handles Selenium Browser exceptions by reloading
- Add delay unfollow of follow backers

### Changed

- Expose `threaded_session` of Instapy.end()

### Fixed

- `follow_likers` always fetches zero likers
- Prevent division by zero in `validate_username`

## [0.2.3] - 2019-03-01

### Changed

- Made Log in text checking more resilient

## [0.2.2] - 2019-02-21

### Fixed

- Chromedriver requirement now >= 2.44 instead of == 2.44

## [0.2.1] - 2019-02-21

### Fixed

- xPath for Log In button

## [0.2.0] - 2019-02-18

### Added

- Accept pending follow requests for private account
- Feature to `follow_by_locations`
- Proxy Authentication support for Firefox

### Fixed

- Only import instapy-chromedriver package when needed
- Avoid user errors providing user names with caps
- Fix get_active_users wrong behavior on videos
- Bug in _CLI_ **argparsing** - `proxy_port` & `page_delay` are integers and not strings.
- Selectors for finding comments and liking comments on posts
- Temporarily turn off follow for `like_by_tags` interaction

### Changed

- Enable users interact by the comments of their own profiles.
- Moved elements from docs folder to instapy-docs and instapy-research repositories

## [0.1.3] - 2019-02-05

### Fixed

- Fix "_Failed to load desired amount of users!_" issue.

### Added

- Add _Progress Tracker_ to `get_users_through_dialog()` function.
- Add Proxy Authentication for Firefox

## [0.1.2] - 2019-02-04

### Fixed

- Fix for scrollIntoView error.

## [0.1.1] - 2019-02-04

### Added

- **Workspace** folders; Now user's data files will be stored at the **workspace** folder.
- _InstaPy_ has been published to _PyPI_; Now, can install/manage it by **pip** as **instapy** package.
- _Github_ releases has been initiated; Will be released in-parallel with _PyPI_ deployments.
- Add Universal Testing Framework- **tox** with **pytest** & **flake8**.
- Upgrade _Travis CI_ usage (_**tox** as build script_).
- Send messages to _Discord_ #**status** channel about jobs' build states from _Travis CI_.
- Add instapy-chromedriver package if no chromedriver is in path.
- Add _argparsing_ feature. Users are now able to provide credentials (_and more_) through CLI args.
- Turn off verification based on _relationship bounds_ **by default**, completely (_see #757815f commit_).
- Simplify the default **quickstart** script much more.

## [Unreleased] - 2019-01-27

### Changed

- Add track post/profile
- Avoid prints for only one user

### Fixed

- No posts exception when scraping likes

## [Unreleased] - 2019-01-22

### Added

- Now `set_dont_unfollow_active_users()` feature also has a Progress Tracker support.

### Fixed

- Fix `set_dont_unfollow_active_users()` feature completely.

## [Unreleased] - 2019-01-17

### Changed

- Optimizing Dockerfile for smaller docker image.

### Fixed

- Fix "_Unable to locate element: ...xpath","selector":"//div[text()=\'Likes\'..._" error.

## [Unreleased] - 2019-01-16

### Fixed

- Fix "_Failed to load desired amount of users!_" issue.

## [Unreleased] - 2019-01-15

### Fixed

- Handle A/B-Test for comments (graphql edge).

## [Unreleased] - 2019-01-13

### Fixed

- Adjust docker-compose.yml according to new Dockerfile.

## [Unreleased] - 2019-01-11

### Fixed

- Correctly mount Docker volume, make it work properly with chromedriver installed in assets folder.

## [Unreleased] - 2019-01-10

### Added

- Feature to remove outgoing unapproved follow requests from private accounts.

## [Unreleased] - 2019-01-05

### Changed

- Resolve security warning with new pyyaml version, updated pyyaml to version 4.2b1.

## [Unreleased] - 2019-01-04

### Fixed

- Fix for non-authenticated proxies in chrome headless browser.

## [Unreleased] - 2019-01-02

### Fixed

- User without timestamp will use the timestamp of previous user.

## [Unreleased] - 2019-01-01

### Changed

- PEP8 layout changes.

## [Unreleased] - 2018-12-17

### Added

- A new setting - `set_do_reply_to_comments()` to control replying to comments.
- A new feature - `run_time()` to get information of how many seconds the _session_ is running; Added to "_Sessional Live Report_" and can also be manually requested like `session.run_time()` from **quickstart** scripts, any time.

### Changed

- A few visual changes to source code for PEP8 compliance.
- Rename `set_reply_comments()` to `set_comment_replies()` out of revised design.

### Fixed

- Fix bug off #3318 which hit python 2 saying, "_TypeError: can't multiply sequence by non-int of type 'float'_" (_raised & solved at #3451_).
- Fix error occured while liking a comment (raised at #3594).
- Fix Follow-Likers feature which couldn't fetch likers properly (raised at #3573).

## [Unreleased] - 2018-12-16

### Added

- Save account progress information into database adding the possibility for external tools to collect and organize the account progress.

## [Unreleased] - 2018-12-10

### Fixed

- Fix `person_id` missing in post_unfollow_cleanup() [line 1152].

## [Unreleased] - 2018-12-08

### Fixed

- Remove https://i.instagram.com/api/v1/users/{}/info/ as it not working and killing the unfollow with error.
- Fix logging uncertain having no userid nor time log, will be important for sync feature.
- Fix get active users when Video have no likes button / no posts in page.

## [Unreleased] - 2018-12-08

### Added

- Full docker-compose and complex template + documentation.

### Fixed

- Fixes likers_from_photo when liked counter is "liked by X and N others".

## [Unreleased] - 2018-12-06

### Fixed

- Fix for python 2.7 users, ceil returns a float in python 2.

## [Unreleased] - 2018-12-05

### Added

- Added mandatory_language (updated check_link definition in like_util).

### Fixed

- Add self.aborts for the follow followers and follow following because otherwise InstaPy won't exit properly on them.

## [Unreleased] - 2018-11-28

### Added

- A new feature - Interact By Comments to **auto-like** comments, **auto-reply** to them, etc. (_see **README**_).
- New text analytics - MeaningCloud Sentiment Analysis API & Yandex Translate API (_Language Detection & Translation_) integrated into **InstaPy** for doing _sophisticated_ text analysis (_see **README**_).

### Changed

- Speed up _logging in_ at least 25 (_default `page_delay`_) seconds (_see #ee6acba commit_).
- Upgrades to `live_report()` feature (_"Sessional Live Report" uses it.._). Now it is more smarter.
- Lots of visual changes to source code for PEP8 compliance.
- Modify `check_authorization()` to dismiss redundant navigations to profile pages. The gain is a few seconds (_~2-3_) saved which is so good.

### Fixed

- Fix a little misbehaviour in `set_relationship_bounds()` with min_posts & max_posts. Now `enabled` parameter controls the whole setting.
- Update `grpcio` package's version in **requirements.txt** to `1.16.1`. Its `1.16.0` had a bug duplicating logger messages.

## [Unreleased] - 2018-11-26

### Changed

- Switch `mandatory_words` from ALL to ANY.

## [Unreleased] - 2018-11-22

### Fixed

- Added location to image_text in the `check_link()` method of **like_util.py**, so the script also searches for the mandatory words in location information.

## [Unreleased] - 2018-11-17

### Fixed

- "_Cookie file not found, creating cookie..._" bug fixed.

## [Unreleased] - 2018-11-07

### Changed

- Maintain names: 'person' for target user and 'username' for our running user.
- Verify private users in get_links_for_username.
- Changed behaviour of validate_username to check if a user is included in the blacklist. If yes will skip it and log why.

## [Unreleased] - 2018-11-01

### Added

- Interact with tagged images of users, and validation of a user to be optional.
- Use Clarifai to check video content. By default deactivated and should only be used if necessary.

## [Unreleased] - 2018-10-29

### Added

- This CHANGELOG file to hopefully serve as a useful resource for InstaPy fellas to stay up-to-date with the changes happened so far.
- **Custom action delays** capability (_see **README**_).
- Now follow engine has the same compact _action verification procedure_ used in the unfollow engine.
- Lots of stability in action verification steps which are held at newly added `verify_action` function.
- New quickstart templates from 11 different people shared at #3033.

### Changed

- Now "_already followed_" state is being tracked by the _following status_ result rather than catching a `NoSuchElementException`.

### Fixed

- Stale element reference error raised at #3173 (occured after #3159).
- Invalid like element issue (occured after IG introduced comment _liking_ to its web interface).

## [0.1.0] - 2016-10-12

### Added

- Working version with basic features.
- Use Clarifai to check the images for inappropriate content.

---

Please, don't dump raw git logs into this file - which is intended for users rather than developers.
