# Tutorial for InstaPy with Python 3.7 and venv

## Basic Raspbian Configuration
NOTE: _If you add an empty file named ssh to the boot directory, ssh will be enabled when you first start your RPi (more info on the official website - section 3 - [here](https://www.raspberrypi.org/documentation/remote-access/ssh/)). If you do this, you can connect your RPi via ethernet, ssh in (once you have your ip) and skip right to the update step below (step 7). If you do not want to do this, follow the initial setup instructions to connect peripherals below._

1. connect rpi3 to monitor via HDMI
2. connect internet via cat5
3. insert usb for wireless keyboard and mouse (if using)
4. plug in rpi3 with sd card preloaded with NOOBs
5. select country & install Raspbian
6. open terminal --> ```sudo raspi-config``` -->interfacing options --> SSH -->enable (allows ssh connection from MacBook); then navigate to VNC --> enable (allows GUI access)
7. ```sudo apt-get update && sudo apt-get upgrade```


## Python 3.7 install guide
**STEP 1:** _First install the dependencies needed to build._

1. ```sudo apt-get update```
2. ```sudo apt-get install -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev```

**STEP 2:** _Compile (takes a while!)_

3. ```wget https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tar.xz```
4. ```tar xf Python-3.7.0.tar.xz```
5. ```cd Python-3.7.0```
6. ```./configure --prefix=/usr/local/opt/python-3.7.0```
7. ```make -j 4```

**STEP 3:** _Install_

8. ```sudo make altinstall```

**STEP 4:** _Make Python 3.7 the default version, make aliases_

9. ```sudo ln -s /usr/local/opt/python-3.7.0/bin/pydoc3.7 /usr/bin/pydoc3.7```
10. ```sudo ln -s /usr/local/opt/python-3.7.0/bin/python3.7 /usr/bin/python3.7```
11. ```sudo ln -s /usr/local/opt/python-3.7.0/bin/python3.7m /usr/bin/python3.7m```
12. ```sudo ln -s /usr/local/opt/python-3.7.0/bin/pyvenv-3.7 /usr/bin/pyvenv-3.7```
13. ```sudo ln -s /usr/local/opt/python-3.7.0/bin/pip3.7 /usr/bin/pip3.7```
14. ```alias python3='/usr/bin/python3.7'```
15. ```echo "alias python3='/usr/bin/python3.7'" >>  ~/.bashrc```

**STEP 5:** _Remove install files_

15. ```cd ..```
16. ```sudo rm -r Python-3.7.0```
17. ```rm Python-3.7.0.tar.xz```


## Install InstaPy

1. ```sudo apt-get update && sudo apt-get upgrade```
2. ```mkdir Projects```
3. ```cd Projects```
4. ```python3 -m venv /home/pi/Projects/venv37```
5. ```git clone https://github.com/timgrossmann/InstaPy.git```
6. ```cd InstaPy```
7. ```python3 -m pip install --user .```

NOTE: _the last step (7.) takes quite a while!_


## For Chrome

_Navigate to the assets folder:_

8. ```wget https://github.com/electron/electron/releases/download/v3.0.0-beta.5/chromedriver-v3.0.0-beta.5-linux-armv7l.zip```
9. ```unzip chromedriver-v3.0.0-beta.5-linux-armv7l.zip```
10. ```chmod 755 chromedriver```
11. ```chmod +x chromedriver```
12. ```sudo apt-get remove chromium```


## For Firefox

_Remove any versions of Firefox as it will conflict with the correct one installed below:_

1. ```sudo apt-get remove firefox-esr```
2. ```sudo apt-get remove iceweasel```
3. ```sudo apt-get remove firefox```

4. ```echo 'deb http://q4os.org/qextrepo q4os-rpi-firefox-cn main' | sudo tee /etc/apt/sources.list.d/qextrepo.list```
5. ```wget -nv -O- http://q4os.org/qextrepo/q4a-q4os.gpg.pub | sudo apt-key add -```
6. ```sudo apt-get update```
7. ```sudo apt-get install firefox```

_Update GeckoDriver if needed. Instructions at the end of this document._

_Firefox is not currently working correctly on Pi 2, to install a working version the following commands should be used:_
Pi2.1. ```wget https://launchpad.net/~ubuntu-mozilla-security/+archive/ubuntu/ppa/+build/10930950/+files/firefox_49.0+build4-0ubuntu0.14.04.1_armhf.deb```

Pi2.2 ```sudo dpkg -i firefox_49.0+build4-0ubuntu0.14.04.1_armhf.deb```


## Finishing up the Firefox installation

_Encountered some errors when trying to run the quickstart.py and ran the next 3 commands (all may not be necessary)_

8. ```sudo pip install future```
9. ```sudo apt-get install xvfb```
10. ```sudo pip install pyvirtualdisplay```
11. ```sudo reboot (may not be required, but no harm)```

_Assuming you've modified quickstart.py to your liking and added your Instagram login to instapy.py_

12. ```sudo xvfb-run python quickstart.py```

_I installed TMUX to help run this headless, so that I can disconnect from the session and have the program continue to run on the rpi3_

13. ```sudo apt-get install tmux (more info found here: https://github.com/tmux/tmux)```
14. If using firefox, follow the example seen in `examples\firefoxExample.py` to set the default browser as Firefox


## How to update GeckoDriver on Raspbian

_New releases can be found in:_ https://github.com/mozilla/geckodriver/releases

1. ```wget https://github.com/mozilla/geckodriver/releases/download/v0.18.0/geckodriver-v0.18.0-arm7hf.tar.gz```
2. ```tar -xvzf geckodriver-v*```
3. ```chmod +x geckodriver```
4. ```sudo cp geckodriver /usr/local/bin/```
