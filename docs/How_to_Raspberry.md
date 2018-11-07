# How to run InstaPy on a RaspberryPi

_NOTE: If you add an empty file named ssh to the boot directory, ssh will be enabled when you first start your RPi (more info on the official website - section 3 - [here](https://www.raspberrypi.org/documentation/remote-access/ssh/)). If you do this, you can connect your RPi via ethernet, ssh in (once you have your ip) and skip right to the update step below (step 7). If you do not want to do this, follow the initial setup instructions to connect peripherals below._

1. connect rpi3 to monitor via HDMI
1. connect internet via cat5
1. insert usb for wireless keyboard and mouse (if using)
1. plug in rpi3 with sd card preloaded with NOOBs
1. select country & install Raspbian
1. open terminal --> sudo raspi-config -->interfacing options --> SSH -->enable (allows ssh connection from MacBook); then navigate to VNC --> enable (allows GUI access)
1. sudo apt-get update && sudo apt-get upgrade
1. mkdir Projects
1. cd Projects
1. git clone https://github.com/timgrossmann/InstaPy.git
1. cd InstaPy
1. sudo pip install . (encountered some errors and resulting 3 commands below (13-15), all may not be necessary)
1. sudo apt-get build-dep python-imaging
1. sudo apt-get install libjpeg8 libjpeg62-dev libfreetype6 libfreetype6-dev
1. sudo pip install .
1. sudo apt-get install tightvncserver (to view GUI from MacBook)

## For Chrome
> This assumes you're using the latest version of raspbian (stretch). Note that this works best running headless.

1. Switch to the root user `sudo su`
1. Update apt source lists `echo "deb http://security.debian.org/debian-security stretch/updates main" >> /etc/apt/sources.list`
1. Update `apt-get update`
1. Install the browser `apt-get install chromium-browser`
1. Install the driver `apt-get install chromedriver`
1. Move the driver into the InstaPy/assets directory `mv /usr/bin/chromedriver /path/to/InstaPy/assets/chromedriver`
1. nano instapy/settings.py
1. change "chromedriver_min_version = 2.36" to "chromedriver_min_version = 2.33" & save file

> The combination of the versions of chromium-browser and chromdriver is important. This combination is currently working 
> * Chromium 65.0.3325.181 Built on Raspbian , running on Raspbian 9.4
> * ChromeDriver 2.36 (a81166ad79e68fbfe7cf5ba243192d6412e26b37) 

## For Firefox
> Remove any versions of Firefox as it will conflict with the correct one installed below:

1. sudo apt-get remove firefox-esr
1. sudo apt-get remove iceweasel
1. sudo apt-get remove firefox

> found the following commands to install Firefox here; https://www.q4os.org/forum/viewtopic.php?id=912

1. echo 'deb http://q4os.org/qextrepo q4os-rpi-firefox-cn main' | sudo tee /etc/apt/sources.list.d/qextrepo.list
1. wget -nv -O- http://q4os.org/qextrepo/q4a-q4os.gpg.pub | sudo apt-key add -
1. sudo apt-get update
1. sudo apt-get install firefox
> Update GeckoDriver if needed. Instructions at the end of this document.

> Firefox is not currently working correctly on Pi 2, to install a working version the following commands should be used:

Pi2.1. wget https://launchpad.net/~ubuntu-mozilla-security/+archive/ubuntu/ppa/+build/10930950/+files/firefox_49.0+build4-0ubuntu0.14.04.1_armhf.deb

Pi2.2 sudo dpkg -i firefox_49.0+build4-0ubuntu0.14.04.1_armhf.deb

## Finishing Up

> Encountered some errors when trying to run the quickstart.py and ran the next 3 commands (all may not be necessary)

24. sudo pip install future
25. sudo apt-get install xvfb
26. sudo pip install pyvirtualdisplay
27. sudo reboot (may not be required, but no harm)


> Assuming you've modified quickstart.py to your liking and added your Instagram login to instapy.py

28. sudo xvfb-run python quickstart.py
>I installed TMUX to help run this headless, so that I can disconnect from the session and have the program continue to run on the rpi3

29. sudo apt-get install tmux (more info found here: https://github.com/tmux/tmux)

30. If using firefox, follow the example seen in `examples\firefoxExample.py` to set the default browser as Firefox



# How to update GeckoDriver on Raspbian

> New releases can be found in https://github.com/mozilla/geckodriver/releases

31. wget https://github.com/mozilla/geckodriver/releases/download/v0.18.0/geckodriver-v0.18.0-arm7hf.tar.gz
32. tar -xvzf geckodriver-v*
33. chmod +x geckodriver
34. sudo cp geckodriver /usr/local/bin/



# Installation with raspbian stretch lite (v4.14)

1. `sudo apt-get update && sudo apt-get upgrade`
2. `sudo apt-get install chromium-browser python-pip git`
3. `git clone https://github.com/timgrossmann/InstaPy.git instapy`
4. in the instapy folder: `pip install .`
5. in the assets folder: `wget https://github.com/electron/electron/releases/download/v3.0.0-beta.5/chromedriver-v3.0.0-beta.5-linux-armv7l.zip`
6. also in the assets folder: `unzip chromedriver-v3.0.0-beta.5-linux-armv7l.zip`
7. 🎉


# Solve Ensure chromedriver is installed at .. (Tested on Raspberry Pi 3 B+)
1. Follow the complete installation above.
2. Remove the chromedriver currently in the assets folder: 'rm chromedriver'
3. Inside the assets folder: 'wget https://github.com/electron/electron/releases/download/v3.0.0-beta.5/chromedriver-v3.0.0-beta.5-linux-armv7l.zip'
4. Inside the assets folder: 'unzip chromedriver-v3.0.0-beta.5-linux-armv7l.zip'
5. 'sudo apt-get remove chromium'
