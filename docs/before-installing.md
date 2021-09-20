---
title: Installing Requirements
---

# Installing Requirements
1. [Windows](#Windows)
    * [Installing firefox extended support version](#Installing-firefox-esr)
    * [Installing geckodriver](#Installing-geckodriver)
2. [Linux](#Linux)
3. [MacOS](#MacOS)
4. [Other](#Other)

**NOTE** - any firefox version below 88 will work

## **Windows**

### **Installing firefox-78.14**

Go to [here](https://www.mozilla.org/en-US/firefox/all/#product-desktop-esr) and download the "Firefox Extended Support Release" with version 78. If you already have firefox installed, keep reading.

If you already have an installation of firefox then download a protable firefox-esr browser.
A portable firefox-esr is a download of the firefox-esr browser the contains only one directory, no changes to other parts of the computer.

Download the version from [here](https://portableapps.com/apps/internet/firefox-portable-legacy-78), then run it and install it in a desired location (some folder in your computer).

Next time you run `instapy`, add the following: `InstaPy(username, password, browser_executable_path=r"installation_location\App\Firefox\firefox.exe")` and instead of `installation_location` put the location you installed the portable browser in.


### **Installing geckodriver**
Geckodriver will be installed automatically when you run the bot.

## **Linux**
The version that should be installed is firefox-esr-78.14.0 with geckodriver
First, check if geckodriver is installed with `which geckodriver`

If it is installed run `sudo add-apt-repository ppa:mozillateam/ppa;sudo apt-get update -y ; sudo apt-get install -y firefox-esr-geckodriver=78.14.0*`
If it is not installed, run `sudo add-apt-repository ppa:mozillateam/ppa;sudo apt-get update -y ; sudo apt-get install -y firefox-esr=78.14.0*`

If you have another installation of firefox, then next time you run `instapy`, add the following: `InstaPy(username, password, browser_executable_path=r"executable file")` and instead of `executable file` place the location of the executable file (result of `which firefox-esr`).

## **Other systems**
Install firefox version 87 or lower and install geckodriver.
