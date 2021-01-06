---
title: Instance Settings
---

### Running on a Headless Browser

Use `headless_browser` parameter to run the bot via the CLI. Works great if running the scripts locally, or to deploy on a server. No GUI, less CPU intensive. [Example](http://g.recordit.co/BhEgXANLhJ.gif)

**Warning:** Some users discourage the use of this feature as Instagram could [detect](https://antoinevastel.com/bot%20detection/2017/08/05/detect-chrome-headless.html) this headless mode!

```python
session = InstaPy(username='test', password='test', headless_browser=True)
```

**(Alternative)**
If the web driver you're using doesn't support headless mode (or the headless mode becomes very detectable), you can use the `nogui` parameter which displays the window out of view. Keep in mind, this parameter lacks support and ease of use, only supporting Linux based operating systems (or those that have Xvfb, Xephyr and Xvnc display software).

```python
session = InstaPy(username='test', password='test', nogui=True)
```

### Bypass Suspicious Login Attempt

InstaPy detects automatically if the Security Code Challenge
is active, if yes, it will ask you for the Security Code on
the terminal.

The Security Code is send to your Email or SMS by Instagram, Email is the defaul option, but you can choose SMS also with:

`bypass_security_challenge_using='sms'` or `bypass_security_challenge_using='email'`

```python
InstaPy(username=insta_username,
        password=insta_password,
        bypass_security_challenge_using='sms')
```

### Two Factor Authentication
InstaPy detects automatically if the account is protected with the Two Factor Authentication, if yes InstaPy user need to provide the Security codes in the session constructor; at least one code is required.

Security codes can be found in: `Settings` -> `Security` -> `Two-Factor-Authentication` -> `Backup Codes`

```python
InstaPy(username=insta_username,
        password=insta_password,
        security_codes=["01234567", "76543210", "01237654"],)
```

<ins
  class="adsbygoogle"
  data-ad-layout="in-article"
  data-ad-format="fluid"
  data-ad-client="ca-pub-4875789012193531"
  data-ad-slot="9530237054"
></ins>
<script>
  (adsbygoogle = window.adsbygoogle || []).push({});
</script>

### Use a proxy

You can use InstaPy behind a proxy by specifying server address, port and/or proxy authentication credentials. It works with and without ```headless_browser``` option.

Simple proxy setup example:

```python
session = InstaPy(username=insta_username,
                  password=insta_password,
                  proxy_address='8.8.8.8',
                  proxy_port=8080)
```

Proxy setup with authentication example:

```python
session = InstaPy(username=insta_username,
                  password=insta_password,
                  proxy_username='',
                  proxy_password='',
                  proxy_address='8.8.8.8',
                  proxy_port=4444)
```

### Running internet connection checks
InstaPy can perform a few checks online, including you connection and the availability of Instagram servers. These checks sometimes fail because Instapy uses third party services to perform these checks. If this should be the case. you can override these checks with this variable: `want_check_browser`.

`want_check_browser` default is False, you can set it to True at session start. Recommend to do this if you want to add additional checks for the connection to the web and Instagram.

For example:

```python
session = InstaPy(username=insta_username,
                  password=insta_password,
                  want_check_browser=True)
```

### Running in threads
If you're running InstaPy in threads and get exception `ValueError: signal only works in main thread` , you have to properly close the session.
There is two ways to do it:

Closing session in smart_run context:

```python
session = InstaPy()
with smart_run(session, threaded=True):
    """ Activity flow """
    # some activity here ...
```

Closing session with `end()` method

```python
session = InstaPy()
session.login()
# some activity here ...
session.end(threaded_session=True)
```

### Choose the browser version
If you have more than one Firefox version on your system or if you are using a portable version you can instruct InstaPy to use that version using the `browser_executable_path` argument in the class initializer.

Specifying the Firefox executable path can also help you if you are getting the following error message:

`selenium.common.exceptions.SessionNotCreatedException: Message: Unable to find a matching set of capabilities`

Example on a Windows machine (with the right path also works on Linux and macOS)

```python
session = InstaPy(username=insta_username,
                  password=insta_password,
                  browser_executable_path=r"D:\Program Files\Mozilla Firefox\firefox.exe")
```

<ins
  class="adsbygoogle"
  data-ad-layout="in-article"
  data-ad-format="fluid"
  data-ad-client="ca-pub-4875789012193531"
  data-ad-slot="9530237054"
></ins>
<script>
  (adsbygoogle = window.adsbygoogle || []).push({});
</script>
