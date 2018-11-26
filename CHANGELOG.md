# Changelog
The **goal** of this file is explaining to the users of our project the notable changes _relevant to them_ that occurred _between_ commits.

_The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)_.

## [Unreleased] - 2018-11-26
### Changed
- Switch mandatory_words from ALL to ANY

## [Unreleased] - 2018-11-22
### Fixed
- "Added location to image_text in the check_link method in like_util.py, so the script also searches for mandatory words in the location information.

## [Unreleased] - 2018-11-17
### Fixed
- "Cookie file not found, creating cookie..." bug fix

## [Unreleased] - 2018-11-07
### Changed
- Maintain names: 'person' for target user and 'username' for our running user
- Verify private users in get_links_for_username
- Changed behaviour of validate_username to check if a user is included in the blacklist. If yes will skip it and log why.


## [Unreleased] - 2018-11-01
### Added
- Interact with tagged images of users, and validation of a user to be optional
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
