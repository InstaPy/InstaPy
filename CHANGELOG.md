# Changelog
The **goal** of this file is explaining to the users of our project the notable changes _relevant to them_ that occurred _between_ commits.

_The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)_.

## [Unreleased] - 2018-11-01
### Added
- Interact with tagged images of users, and validation of a user to be optional

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
