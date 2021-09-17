---
title: Installing firefox
---

### Installing firefox-esr

#### On Windows

Go to [here](https://www.mozilla.org/en-US/firefox/all/#product-desktop-esr) and download the "Firefox Extended Support Release".
If you already have an installation of firefox then go to [here](#Already have an installation).

#### On Linux

Run `sudo apt install firefox-esr`. You can use `brew` or any other thing that does a similar task.

### Already have an installation

It only matters on windows. In this case we need to download a protable firefox-esr browser.
A portable firefox-esr is a download of the firefox-esr browser the contains only one directory.
Using the portable install won't affect any other part of the system, and to uninstall it you simply delete the folder.
Download the version from [here](https://portableapps.com/apps/internet/firefox-portable-legacy-78), then run it and install it in a desired location.
Next time you run `instapy`, add the following: `InstaPy(username, password, "{installation_location}\\App\\Firefox\\firefox.exe")`.

#### Installed in a non-default location

Next time you run `instapy`, add the following: `InstaPy(username, password, "{executable_location}")`.
