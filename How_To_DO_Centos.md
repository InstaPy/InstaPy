# How to run InstaPy on a digital ocean CentOS 7 droplet
- ### Make sure to use the 1GB RAM version

## General dependencies
1. yum update
1. yum -y install unzip yum-utils epel-release git
1. yum-builddep python
1. yum -y install python34 python34-devel 
1. yum -y install Xvfb libXfont Xorg
1. yum -y groupinstall "X Window System" "Desktop" "Fonts" "General Purpose Desktop"
1. yum install python-devel

## Python-pip
1. curl https://bootstrap.pypa.io/get-pip.py | python

## Chrome-stable
1. cd ~
1. wget http://chrome.richardlloyd.org.uk/install_chrome.sh
1. chmod u+x install_chrome.sh
1. ./install_chrome.sh

## InstaPy
1. git clone https://github.com/timgrossmann/InstaPy.git
1. wget "http://chromedriver.storage.googleapis.com/2.29/chromedriver_linux64.zip"
1. unzip chromedriver_linux64
1. mv chromedriver InstaPy/assets/chromedriver
1. chmod +x InstaPy/assets/chromedriver
1. chmod 755 InstaPy/assets/chromedriver
1. pip install .


### Make sure to uncommented the display lines on instapy/instapy.py (self.display)
