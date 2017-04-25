# How to run InstaPy on a digital ocean CentOS 7 droplet
> Use https://m.do.co/c/be9ec19b28c1 to get 10$ free to start your InstaPy journey :wink:

- #### Make sure to use the 1GB RAM version

- #### Make sure to set ```nogui=True``` in your InstaPy file

## General dependencies

```sh
$ yum update
$ yum -y install unzip yum-utils epel-release git
$ yum-builddep python
$ yum -y install python34 python34-devel
$ yum -y install Xvfb libXfont Xorg
$ yum -y groupinstall "X Window System" "Desktop" "Fonts" "General Purpose Desktop"
$ yum install python-devel
```

## Python-pip

```sh
$ curl https://bootstrap.pypa.io/get-pip.py | python
```

## Chrome-stable

```sh
$ cd ~
$ wget http://chrome.richardlloyd.org.uk/install_chrome.sh
$ chmod u+x install_chrome.sh
$ ./install_chrome.sh
```

## InstaPy

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
