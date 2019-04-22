<p align="center">
  <img src="https://i.imgur.com/sJzfZsL.jpg" width="150">
  <h1 align="center">InstaPy</h1>
  <p align="center">Tooling that <b>automates</b> your social media interactions to “farm” Likes, Comments, and Followers on Instagram
Implemented in Python using the Selenium module.<p>
  <p align="center">
    <a href="https://github.com/timgrossmann/InstaPy/blob/master/LICENSE">
      <img src="https://img.shields.io/badge/license-GPLv3-blue.svg" />
    </a>
    <a href="https://github.com/SeleniumHQ/selenium">
      <img src="https://img.shields.io/badge/built%20with-Selenium-yellow.svg" />
    </a>
    <a href="https://www.python.org/">
    	<img src="https://img.shields.io/badge/built%20with-Python3-red.svg" />
    </a>
    <a href="https://travis-ci.org/timgrossmann/InstaPy">
	<img src="https://travis-ci.org/timgrossmann/InstaPy.svg?branch=master">
    </a>
    <a href="https://www.github.com/timgrossmann/InstaPy#backer">
	<img src="https://opencollective.com/instapy/backers/badge.svg">
    </a>
    <a href="https://www.github.com/timgrossmann/InstaPy#sponsors">
	<img src="https://opencollective.com/instapy/sponsors/badge.svg">
    </a>  
    <a href="https://discord.gg/FDETsht">
	<img src="https://img.shields.io/discord/510385886869979136.svg">
    </a>
  </p>
</p>


[Twitter of InstaPy](https://twitter.com/InstaPy) | [Twitter of Tim](https://twitter.com/timigrossmann) | [Discord Channel](https://discord.gg/FDETsht) | [How it works (Medium)](https://medium.freecodecamp.com/my-open-source-instagram-bot-got-me-2-500-real-followers-for-5-in-server-costs-e40491358340) |   
[Talk about automating your Instagram](https://youtu.be/4TmKFZy-ioQ) | [Talk about doing Open-Source work](https://www.youtube.com/watch?v=A_UtST302Og&t=0s&list=PLa4P1NPX9hthXV-wko0xyxFpbhYZFkW7o) | [Listen to the "Talk Python to me"-Episode](https://talkpython.fm/episodes/show/142/automating-the-web-with-selenium-and-instapy)


**Newsletter: [Sign Up for the Newsletter here!](http://eepurl.com/cZbV_v)**   
**Offical Video Guide: [Get it here!](https://www.udemy.com/instapy-guide/?couponCode=INSTAPY_OFFICIAL)**


## **Installation**
```elm
pip install instapy
```
**That's it! 🚀**   
If you're on Ubuntu, read the specific guide on [Installing on Ubuntu (64-Bit)](https://github.com/InstaPy/instapy-docs/blob/master/How_Tos/How_To_DO_Ubuntu_on_Digital_Ocean.md). If you're on a Raspberry Pi, read the [Installing on RaspberryPi](https://github.com/InstaPy/instapy-docs/blob/master/How_Tos/How_to_Raspberry.md) guide instead.

Download a **[quickstart](https://github.com/InstaPy/instapy-quickstart)** script of your choice to your machine. It tells InstaPy how it should run, and this is the file you'll be working on when changing how InstaPy works.

- [Here is the easiest **quickstart** script you can use](https://github.com/InstaPy/instapy-quickstart/blob/master/quickstart.py)  

- [And here you can find lots of sophisticated **quickstart** templates shared by the community!](https://github.com/InstaPy/instapy-quickstart/tree/master/quickstart_templates) 

You can put in your account details now by passing the username and password parameters to the `InstaPy()` function in your **quickstart** script, like so: 
```python
InstaPy(username="abc", 
        password="123")
```
Or you can [pass them using the Command Line Interface (CLI)](#pass-arguments-by-cli).

> If you've used _InstaPy_ before installing it by **pip**, you have to move your _old_ data to the new **workspace** folder for once.
[Read how to do this here](./DOCUMENTATION.md#migrating-your-data-to-the-workspace-folder).

To run InstaPy, you'll need to run the **[quickstart](https://github.com/InstaPy/instapy-quickstart)** script you've just downloaded.

```elm
python quickstart.py
-- or
python quickstart.py --username abc --password 123
```

InstaPy will now open a browser window and start working.

> If want InstaPy to run in the background pass the `--headless-browser` option when running from the CLI   
Or add the `headless_browser=True` parameter to the `InstaPy(headless_browser=True)` constructor.

#### Updating InstaPy
```elm
pip install instapy -U
```

## Guides

#### Video tutorials:
**[Official InstaPy Guide on Udemy](https://www.udemy.com/instapy-guide/?couponCode=INSTAPY_OFFICIAL)**

**[Installation on Windows](https://www.youtube.com/watch?v=9DkEl2MrFQk&list=PLa4P1NPX9hthXV-wko0xyxFpbhYZFkW7o&index=11&t=40s)**

**[Installation on MacOS](https://www.youtube.com/watch?v=TqQWM63Hhh4&t=11s&list=PLa4P1NPX9hthXV-wko0xyxFpbhYZFkW7o&index=12)**

**[Installation on Linux](https://www.youtube.com/watch?v=sZ-SFy9vKHg&list=PLa4P1NPX9hthXV-wko0xyxFpbhYZFkW7o&index=10&t=28s)**

**[Installation on DigitalOcean Server](https://www.youtube.com/watch?v=my0FM5hra_s&t=14s&list=PLa4P1NPX9hthXV-wko0xyxFpbhYZFkW7o&index=9)**

#### Written Guides:
**[How to Ubuntu (64-Bit)](https://github.com/InstaPy/instapy-docs/blob/master/How_Tos/How_To_DO_Ubuntu_on_Digital_Ocean.md) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**

**[How to RaspberryPi](https://github.com/InstaPy/instapy-docs/blob/master/How_Tos/How_to_Raspberry.md) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**


#### External Tools:

**[InstaPy Dashboard](https://github.com/converge/instapy-dashboard)**
> InstaPy Dashboard is an Open Source project developed by [@converge](https://github.com/converge/) to visualize Instagram accounts progress and real-time InstaPy logs on the browser.



## Documentation
A list of **all features** of InstaPy [can be found here](./DOCUMENTATION.md). 


## Support

### Do you need help ?
If you should encounter any issue, please first [search for similar issues](https://github.com/timgrossmann/InstaPy/issues) and only if you can't find any, create a new issue or use the [discord channel](https://discord.gg/FDETsht) for help.

<a href="https://discord.gg/FDETsht">
  <img hspace="3" alt="Discord channel" src="https://camo.githubusercontent.com/e4a739df27356a78e9cae2e2dda642d118567e7c/68747470733a2f2f737465616d63646e2d612e616b616d616968642e6e65742f737465616d636f6d6d756e6974792f7075626c69632f696d616765732f636c616e732f32373039303534312f386464356339303766326130656563623733646336613437373666633961323538373865626364642e706e67" width=214/>
</a>

### Do you want to support us ?

<a href="https://opencollective.com/instapy/donate" target="_blank">
  <img align="left" hspace="10" src="https://opencollective.com/instapy/contribute/button@2x.png?color=blue" width=300 />
</a>

<a href="https://www.paypal.me/supportInstaPy">
  <img hspace="14" alt="paypalme" src="http://codeinpython.com/tutorials/wp-content/uploads/2017/09/PayPal-ME-300x300.jpg.png" width=100 />
</a>

**Help build InstaPy!**      
Check out this short guide on [how to start contributing!](https://github.com/InstaPy/instapy-docs/blob/master/CONTRIBUTORS.md).

## Credits
### Contributors

This project exists thanks to all the people who contribute. [[Contribute](https://github.com/timgrossmann/InstaPy/wiki/How-to-Contribute)].

<a href="https://github.com/timgrossmann/InstaPy/graphs/contributors"><img src="https://opencollective.com/instapy/contributors.svg?width=890&button=false" /></a>

### Backers

Thank you to all our backers! 🙏 [[Become a backer](https://opencollective.com/instapy#backer)]

<a href="https://opencollective.com/instapy#backers" target="_blank"><img src="https://opencollective.com/instapy/backers.svg?width=890"></a>

### Sponsors

Support this project by becoming a sponsor. Your logo will show up here with a link to your website. [[Become a sponsor](https://opencollective.com/instapy#sponsor)]

<a href="https://www.chancetheapp.com" target="_blank">
	<img src="https://user-images.githubusercontent.com/16529337/52699787-dbb17f80-2f76-11e9-9657-c103d4e89d88.png" height=75 />
</a>

---

> **Disclaimer**: Please Note that this is a research project. I am by no means responsible for any usage of this tool. Use on your own behalf. I'm also not responsible if your accounts get banned due to extensive use of this tool.
