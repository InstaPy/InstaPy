# Changelog
The **goal** of this file is explaining to the users of our project the notable changes _relevant to them_ that occurred _between_ commits.

_The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)_.


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
-  User without timestamp will use the timestamp of previous user.


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
