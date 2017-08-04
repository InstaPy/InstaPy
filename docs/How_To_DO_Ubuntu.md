# How to run InstaPy on a digital ocean Ubuntu droplet
> Use https://m.do.co/c/be9ec19b28c1 to get 10$ free to start your InstaPy journey :wink:

- #### Make sure to use the 1GB RAM version (or better)

- #### Make sure to set ```nogui=True``` in your InstaPy file

### General dependencies

```sh
$ sudo apt-get update
$ sudo apt-get -y upgrade
$ sudo apt-get -y install unzip python3-pip python3-dev build-essential libssl-dev libffi-dev xvfb
$ sudo pip3 install --upgrade pip
$ export LANGUAGE=en_US.UTF-8
$ export LANG=en_US.UTF-8
$ export LC_ALL=en_US.UTF-8
$ locale-gen en_US.UTF-8
$ sudo dpkg-reconfigure locales
$ pip3 install --upgrade pip
```

### Chrome-stable

```sh
$ cd ~
$ wget "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
$ sudo dpkg -i google-chrome-stable_current_amd64.deb
$ sudo apt-get install -y -f
$ sudo rm google-chrome-stable_current_amd64.deb
```

### InstaPy

```bash
$ git clone https://github.com/timgrossmann/InstaPy.git
$ wget "http://chromedriver.storage.googleapis.com/2.29/chromedriver_linux64.zip"
$ unzip chromedriver_linux64
$ mv chromedriver InstaPy/assets/chromedriver
$ chmod +x InstaPy/assets/chromedriver
$ chmod 755 InstaPy/assets/chromedriver
$ cd InstaPy
$ pip install .
```
