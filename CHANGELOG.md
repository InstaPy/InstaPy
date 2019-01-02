# Changelog
The **goal** of this file is explaining to the users of our project the notable changes _relevant to them_ that occurred _between_ commits.

_The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)_.

## [Unreleased] - 2019-01-01
### Changed
- PEP8 layout changes

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
