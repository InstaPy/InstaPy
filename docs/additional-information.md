---
title: Additional Information
---

### Advanced Installation
#### 🛠 Install or update to the unreleased version
For example, there is a **bug** and its **fix** is _merged to the repo_ but a newer version of _InstaPy_ [_containing_ that **fix**] is not yet released to _PyPI_ to be able to be _installed_ or _updated_ by **pip**.

Then, you can do this to install the **actual state** of the _repo_ 😋
```erlang
pip install -I https://github.com/timgrossmann/InstaPy/zipball/master
```

Worths to note that, this installation option does not require _Git_ to be installed, too.
`-I` flag in there is used to _ignore the installed_ packages and _reinstall_ them instead.

<details>
  <summary>
    <b>
      Learn why <code>-I</code> flag is required 🔎
    </b>
  </summary>

Since _InstaPy_'s version is not yet being incremented which is the reason you're installing it from a _zipball_, then if you don't use the `-I` flag, **pip** will complain saying,
- "_Hey, I have already installed the x.y.z version! Skipping installation..._"

But obviously, even though the version is the same, _zipball_ has the current state of the repository.
That's why you will be able to install the actual state of the repo using the `-I` flag.

</details>

<br />

>**PRO** Tip:
  Read the section - [How to avoid _python_ & **pip** confusion](#how-to-avoid-python--pip-confusion) 😄

<br />

#### ⚗ Install manually and manage using advanced git commands
###### For those who want to tweak or enhance _InstaPy_.

**1**. Clone _InstaPy_ repository into your computer
```erlang
git clone https://github.com/timgrossmann/InstaPy.git
```

**2**. Navigate to the _InstaPy_ project root directory
```erlang
cd InstaPy
```

**3**. Install the _local_ **instapy** package
```erlang
pip install -e .
```
<details>
  <summary>
    <b>
      Learn why <code>-e</code> flag is required 🔎
    </b>
  </summary>

Since you're gonna install the local version of _InstaPy_ you'll probably change its code per your need which is the reason you do an advanced installation from a _Git_ source, then if you don't use the `-e` flag, you'll have to install that local package by **pip** every time after making a change.

But fortunately, `-e` flag comes to help;
`-e` means _editable_ install, so that after editing files you don't need to re-install the package again since it will always refer to the edited files cos with the _editable_ install, it just **links** the project's location to **pip**'s install location _rather than_ adding them to **pip** location separately..
<br />
</details>
or

```erlang
python setup.py install
```

<br />

#### ⛑ Install into a Virtual Environment

###### The best way to install _InstaPy_ is to create a virtual environment and install _InstaPy_ there, then, run it from a separate file.

<details>
  <summary>
    <b>
      Guide for <b>Pythons</b> >= 3.6 🔎
    </b>
  </summary>

##### Mac/Linux

**1**. Clone _InstaPy_ repository into your computer
```erlang
git clone https://github.com/timgrossmann/InstaPy.git
```

**2**. Navigate to the _InstaPy_ project root directory
```erlang
cd InstaPy
```

**3**. Make a virtual environment
```erlang
python3 -m venv venv
```

**4**. Activate the virtual environment
```erlang
source venv/bin/activate
```

**5**. Install the _local_ **instapy** package
```erlang
pip install -e .
```



##### Windows

**1**. Clone _InstaPy_ repository into your computer
```erlang
git clone https://github.com/timgrossmann/InstaPy.git
```

**2**. Navigate to the _InstaPy_ project root directory
```erlang
cd InstaPy
```

**3**. Make a virtual environment
```erlang
python3 -m venv venv
```

**4**. Activate the virtual environment
```erlang
venv\Scripts\activate.bat
```

**5**. Install the _local_ **instapy** package
```erlang
pip install -e .
```


If you're not _familiar_ with **venv**, please [read about it here](https://docs.python.org/3/library/venv.html) and use it to your advantage;

- Running `source venv/bin/activate` will _activate_ the correct _python_ to run _InstaPy_. To exit an activated **venv** run `deactivate`.
- Now, copy & paste the **quickstart.py** _python_ code below and then run your first _InstaPy_ script.
  Remember to run it with _python_ from the **venv**.
- To make sure which _python_ is used, run `which python` which will tell you the active version of _python_.
- Whenever you run the script, the virtual environment must be _active_.

</details>


<details>
  <summary>
    <b>
      Guide for <b>Pythons</b> greater 3.6 🔎
    </b>
  </summary>

**1**. Make a virtual environment
```erlang
virtualenv venv
```

**2**. Activate the virtual environment
```erlang
source venv/bin/activate
```

**3**. Install the **instapy** package from _Git_ by using **pip**
```erlang
pip install git+https://github.com/timgrossmann/InstaPy.git
```


If you're not _familiar_ with **virtualenv**, please [read about it here](https://virtualenv.pypa.io/en/stable/) and use it to your advantage;

In essence,
 - This is be the **only** _python_ library you should install as `root` (_e.g., with `sudo`_).
 - All other _python_ libraries should be inside a **virtualenv**.
 - Running `source venv/bin/activate` will activate the correct _python_ to run _InstaPy_.
    And to exit an activated **virtualenv** run `deactivate`.
 - Now, copy & paste the **quickstart.py** _python_ code below and run your first _InstaPy_ script.
 Remember to run it with _python_ from the **virtualenv**, so from **venv/bin/python**.
 - To make sure which _python_ is used, run `which python` which would tell you the active version of _python_.

</details>

<br />

#### **Install** a _**specific** version_
```elm
pip install instapy==0.1.1
```

#### **Uninstall**
```elm
pip uninstall instapy
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

## Workspace folders
### Migrating your data to the workspace folder
After installing InstaPy with pip, you have to run it once by calling `python quickstart.py`. Once the web browser opens, you can abort the session by closing the browser or your terminal.

You will now find an `InstaPy` folder located at the above mentioned home folder.
Simply copy and paste the content of your logs folder into that workspace folder in order to assure that all your data is migrated.

> Please note that you only have to do this once. After that, you can get rid of your old, downloaded version of this repository since the InstaPy folder in your home folder will now be the default location for your data.


###### _InstaPy_ stores user's data files inside the **workspace** folder.

By default, it is gonna be the **InstaPy** folder at your home folder.
Such as, if your username is `Cherry`, let's show where your InstaPy folder would be,

|   OS    |       home folder     | _InstaPy_ **workspace** folder |
| ------- | --------------------- | ------------------------------ |
| Windows | `C:\\Users\\Cherry\\` | `C:\\Users\\Cherry\\InstaPy\\` |
|   Mac   |    `/Users/Cherry/`   |    `/Users/Cherry/InstaPy/`    |
|  Linux  |    `/home/Cherry/`    |    `/home/Cherry/InstaPy/`     |

Note that, at the start of each run, it shows you the **workspace** folder in use.

<br />

<details>
  <summary>
    <b>
      What will be stored at the <b>workspace</b> folder? 🔍
    </b>
  </summary>

Anything that is _user's **data file**_ will be stored in there.
Such as,
- **logs** folder - _log and other storage files_
- **assets** folder - _e.g. user chosen chromedriver executable(s)_
- **db** folder - _databases_
- etc.

</details>


### Set a _custom_ workspace folder
You can use `set_workspace()` function to set a custom **workspace** folder,
```python
from instapy import InstaPy
from instapy import set_workspace

set_workspace("C:\\My\\Custom\\Path\\InstaPy\\")

session = InstaPy(...)
```

<details>
  <summary>
    <b>
      Rules 🔎
    </b>
  </summary>

**1**-) You have to set your custom **workspace** folder before instantiates _InstaPy_.
**2**-) Your custom **workspace** folder must have `InstaPy` (*_case sensitive_) word in its name.
+ If your path does not have it,
`set_workspace("C:\\Other\\Path\\InstaPie\\")`
then your **workspace** folder will be named and made as,
`"C:\\Other\\Path\\InstaPie\\InstaPy\\"`
👆🏼 `InstaPy` directory will be added as a new subdirectory in there, and be your **workspace** folder.

+ If your custom **workspace** folder name has a case-insensitive default name in it- `Instapy`, `instapy`, `instaPY`, etc.,
`set_workspace("C:\\Other\\Path\\instapy2\\")`
then your **workspace** folder will be,
`"C:\\Other\\Path\\InstaPy2\\"`
as you can see, it normalizes name and sets the **workspace** folder.


##### _Why naming is so important?_
 - It will help to easily adapt to the flexible _InstaPy_ usage with that default formal name.

</details>


### Set a custom **workspace** folder _permanently_ with ease
If you want to set your custom **workspace** folder permanently and more easily, add a new environmental variable named `INSTAPY_WORKSPACE` with the value of the path of the desired **workspace** folder to your operating system.
Then that will be the default **workspace** folder in all sessions [unless you change it using `set_workspace()` or so].


### _Get_ the location of the workspace folder in use
If you ever want to **get** the _location_ of your **workspace** folder, you can use
the `get_workspace()` function,
```python
from instapy import InstaPy
from instapy import smart_run
from instapy import set_workspace
from instapy import get_workspace

set_workspace(path="C:\\Custom\\Path\\InstaPy_super\\")

session = InstaPy(username="abc", password="123")

with smart_run(session):
    # lots of code
    workspace_in_use = get_workspace()
    print(workspace_in_use["path"])
    # code code
```
Note that, `get_workspace()` is a function used _internally_ and makes a **workspace** folder [by default at home folder] if not exists.
It means, you must use only the `set_workspace()` feature to set a custom **workspace** folder and not try to use `get_workspace()` for that purpose..


### Set a custom _location_
You can set any of the **custom** _locations_ you like, **any time**!
E.g. setting the _location_ of the **database** file,
```python
from instapy import InstaPy
from instapy import set_workspace
from instapy import Settings


set_workspace(...)   # if you will set a custom workspace, set it before anything
Settings.db_location = "C:\\New\\Place\\DB\\instapy.db"

session = InstaPy(...)
# code code
```


<details>
  <summary>
    <b>
      Restrictions 🔎
    </b>
  </summary>

**a**-) You cannot set a custom **workspace** folder after _InstaPy_ has been instantiated;
_E.g. while instantiating _InstaPy_, you make a logger at that given location and trying to change the_ `log_location` _really needs to restart the LOGGER adapter and make another logger instance, but it can be achieved in future_.

**b**-) If you set a custom **workspace** once and then set it again then your data locations will still use the previous locations:
```python
from instapy import InstaPy
from instapy import set_workspace
from instapy import Settings

# first time settings custom workspace folder
set_workspace("C:\\Users\\MMega\\Desktop\\My_InstaPy\\")
# second time settings custom workspace folder
set_workspace("C:\\Users\\MMega\\Documents\\My_InstaPy\\")

# locations of data files, e.g. chromedriver executable, logfolder, db will use first custom workspace locations.
# if you still want to change their location to second one, then do this one by one:
Settings.log_location = "C:\\Users\\MMega\\Documents\\My_InstaPy\\logs\\"
Settings.database_location = "C:\\Users\\MMega\\Documents\\My_InstaPy\\db\\instapy.db"
Settings.chromedriver_location = "C:\\Users\\MMega\\Documents\\My_InstaPy\\logs\\chromedriver.exe"
```
As you can see, you have to use `set_workspace()` only once.
Why it is so difficult in those 👆🏼 regards?
 - It's to preserve custom location assignments alive (`Settings.*`) cos otherwise setting another **workspace** would override any previously _manually_ assigned location(s).

</details>


### Pass arguments by CLI
###### It is recommended to pass your credentials from command line interface rather than storing them inside quickstart scripts.

Note that, arguments passed from the CLI has higher priorities than the arguments inside a **quickstart** script.
E.g., let's assume you have,
```python
# inside quickstart script

session = InstaPy(username="abc")
```
and you start that **quickstart** script as,
```erlang
python quickstart.py -u abcdef -p 12345678
```
Then, your _username_ will be set as `abcdef` rather than `abc`.
_And obviously, if you don't pass the flag, it'll try to get that argument from the **quickstart** script [if any]_.

#### Currently these _flags_ are supported:
  🚩 `-u` abc, `--username` abc
   - Sets your username.

  🚩 `-p` 123, `--password` 123
   - Sets your password.

  🚩 `-pd` 25, `--page-delay` 25
   - Sets the implicit wait.

  🚩 `-pa` 192.168.1.1, `--proxy-address` 192.168.1.1
   - Sets the proxy address.

  🚩 `-pp` 8080, `--proxy-port` 8080
   - Sets the proxy port.

  🚩 `-hb`, `--headless-browser`
   - Enables headless mode.

  🚩 `-dil`, `--disable-image-load`
   - Disables image load.

  🚩 `-bsa`, `--bypass-suspicious-attempt`
   - Bypasses suspicious attempt.

  🚩 `-bwm`, `--bypass-with-mobile`
   - Bypasses with mobile phone.

To get the list of available commands, you can type,
```erlang
python quickstart.py -h
# or
python quickstart.py --help
```

#### Examples
⚽ Let's quickly set your username and password right by CLI,
```erlang
python quickstart.py -u Toto.Lin8  -p 4X27_Tibor
# or
python quickstart.py --username Toto.Lin8  --password 4X27_Tibor
# or
python quickstart.py -u "Toto.Lin8"  -p "4X27_Tibor"
```

<details>
<summary>
  <b>
    Advanced 🔎
  </b>
</summary>

You can **pass** and then **parse** the **_custom_** CLI arguments you like right inside the **quickstart** script.
To do it, open up your **quickstart** script and add these lines,
```python
# inside quickstart script

import argparse

my_parser = argparse.ArgumentParser()
# add the arguments as you like WHICH you will pass
# e.g., here is the simplest example you can see,
my_parser.add_argument("--my-data-files-name")
args, args_unknown = my_parser.parse_known_args()

filename = args.my_data_files_name

# now you can print it
print(filename)

# or open that file
with open(filename, 'r') as f:
    my_data = f.read()
```
After adding your custom arguments to the **quickstart** script, you can now **pass** them by CLI, comfortably,
```erlang
python quickstart.py --my-data-files-name "C:\\Users\\Anita\\Desktop\\data_file.txt"
```
>**NOTE**:
Use **dash** in flag and parse them with **underscores**;
E.g., we have used the flag as **`--my-data-files-name`** and parsed it as `args.`**`my_data_files_name`** ...

>**PRO**:
See `parse_cli_args()` function [used internally] inside the **util.py** file to write & parse more advanced flags.
You can also import that function into your **quickstart** script and parse the **formal** flags into there to be used, as well.

```python
# inside quickstart script

from instapy.util import parse_cli_args


cli_args = parse_cli_args()
username = cli_args.username

print(username)
```
👆🏼👉🏼 as you will pass the _username_ like,
```erlang
python quickstart.py -u abc
```

</details>

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

## Extensions
[1. Session scheduling with Telegram](https://github.com/Tkd-Alex/Telegram-InstaPy-Scheduling)


### Custom geckodriver
By default, InstaPy downloads the latest version of the geckodriver.
Unless you need a specific version of the geckodriver, you're ready to go.

You can manually download the geckodriver binary and put the path as an argument to the InstaPy contructor:

```python
session = InstaPy(..., geckodriver_path = '/path/to/binary', ...)
```

### Using one of the templates

If you're interested in what other users setup looks like, feel free to check out the `quickstart_templates` folder which includes several working setups with different features.

In order to use them, just copy the desired file and put it next to the `quickstart.py` file in the, what is called root, directory.

Finally simply adjust the username and any tags or firend lists before executing it.
That's it.


### How not to be banned
Built-in delays prevent your account from getting banned.
However, excessive use of this tool may result in action blocks or permanent bans.
Use the Quota Supervisor feature to set some fixed limits for the bot for maximum safety.


### Disable Image Loading
If you want to save some bandwidth, you can simply disable the image/video loading. This will lead to, if you watch InstaPy running, not downloading and displaying any more images and videos.

> Note: This can save a tremendous amount of data. This is turned off by default (`False`).

To do this simply pass the `disable_image_load=True` parameter in the InstaPy constructor like so:
```python
session = InstaPy(username=insta_username,
                  password=insta_password,
                  headless_browser=False,
                  disable_image_load=True,
                  multi_logs=True)
```

### Changing DB or location
If you want to change the location/path of the DB, simply head into the `instapy/settings.py` file and change the following lines.
Set these in instapy/settings.py if you're locating the library in the /usr/lib/pythonX.X/ directory.
```
Settings.database_location = '/path/to/instapy.db'
```

### Split SQLite by Username
If you experience issue with multiple accounts Instapy.db lockup. You can add the following flag

`-sdb` when running in Command line

or

To do this simply pass the `split_db=True` parameter in the InstaPy constructor like so:

```python
session = InstaPy(username=insta_username,
                  password=insta_password,
                  headless_browser=False,
                  split_db=True,
                  multi_logs=True)
```



### How to avoid _python_ & **pip** confusion

Sometimes you have **multiple** _python_ installations in your system.
Then you'll obviously have crazy aliases linked to _python_ and **pip** commands.

For example, let's assume you have _python_ 2.7 & _python_ 3.7 installed in your system,

| _python_ version | _python_ alias | **pip** alias |
| ---------------- | -------------- | ------------- |
|       2.7        |     `py2`      |     `pip`     |
|       3.7        |    `python`    |     `pip3`    |

And once you install a package by the `pip` command and try to run it with `python` command, it will confuse you.

Why? - cos,
- `pip` command is for _python_ 2.7
- `python` command is for _python_ 3.7

To solve that confusion, use this **style** to install packages by **pip**,
```powershell
# install "instapy" package into python 3.7
python -m pip install instapy

# install "instapy" package into python 2.7
py2 -m pip install instapy
```

As you can see, it is,
`python -m pip ...`
rather than,
`pip ...`

Other **pip** commands can be accomplished the same way, too.
Such as,
```powershell
# update "instapy" package
python -m pip install instapy -U

# uninstall "instapy" package
python -m pip uninstall instapy

# show details of the "instapy" package installed by pip
python -m pip show instapy
```

Using this style, you will never have to worry about what is the correct alias of the **pip** for you specific _python_ installation and all you have to know is just the _python_'s alias you use.

### Dealing with Selenium Common Exception Issues

##### selenium.common.exceptions.WebDriverException: Message: unknown error: Cannot read property 'entry_data' of undefined
This error could also caused by unstable Internet connection or Instagram's web changed their data-structure.

##### TL;DR - Make sure your chromedriver version is compatible with your Google Chrome version.
Occasionally *Instapy* will stop working because one of the issues below has been thrown.

>_Traceback (most recent call last):
....// File list with the exception trace
selenium.common.exceptions.WebDriverException: Message: unknown error: Cannot read property 'entry_data' of undefined
(Session info: headless **chrome=75.0.3770.80**)
(Driver info: **chromedriver=2.36.540469** (1881fd7f8641508feb5166b7cae561d87723cfa8),platform=Mac OS X 10.14.5 x86_64)

>_Traceback (most recent call last):
....// File list with the exception traceselenium.common.exceptions.WebDriverException: Message: unknown error: unknown sessionId
(Session info: headless **chrome=75.0.3770.80**)
(Driver info: **chromedriver=2.36.540469** (1881fd7f8641508feb5166b7cae561d87723cfa8),platform=Mac OS X 10.14.5 x86_64)

Notice that *chrome* version is **75** and the *chromedriver* version is **2.36**.

According to the [release notes](https://chromedriver.storage.googleapis.com/2.36/notes.txt) for chromedriver, version 2.36 only supports Chrome versions 63-65.

Which means, there is a mismatch in chromedriver and Chrome that installed on my machine.

There several steps to this fix.

1. Completely uninstall Google Chrome.
2. Download an older version.
3. Prevent Google Chrome from auto-updating.


#### MAC FIX
Since *Instapy* seems to work well, in my experience on my Mac, with chromedriver version 2.36, I will downgrade my Google Chrome. I do not use Google Chrome, so this isn't an issue.


1. **Uninstall Google Chrome**
	I used an app called [App Cleaner](https://freemacsoft.net/appcleaner/) to remove Chrome.
	After you install App Cleaner, simply drag Google Chrome, from the Applications folder to App Cleaner and Remove All

2. **Download Chrome 65** *(Read this step completely before proceeding)*
	- Find and install Chrome 65 from [sllimjet.com](https://www.slimjet.com/chrome/google-chrome-old-version.php)

	- After you have installed Chrome 65, open and click the Apple Security Ok button that alerts you to the fact this was downloaded from the internet.
	- THEN, immediately close Google Chrome completely by holding **`CMD+Q`**. This is extremely important! Google Chrome will being its auto-update function. So it must be completely closed, not just the window.
	*We need Chrome to run first and put all its files where it needs them.*

3. **Prevent Google Chrome from updating**
	- Open **Terminal** and type
	`sudo chmod -R 000 ~/Library/Google`

	- You will be asked for your computer password, enter it.

	- Next run the command
	`sudo rm -rf /Library/Google/`

	Google Chrome should not be able to auto-update now.

If for some reason Chrome is still updating, or you're unable to run the command in step 3, you can edit your `/etc/hosts file` to include the following line: `0.0.0.0 tools.google.com`


#### Windows Fix
Coming soon

#### Raspberry Pi Fix
Coming Soon


---

###### Have Fun & Feel Free to report any issues
### [Windows Task Scheduler](https://msdn.microsoft.com/en-us/library/windows/desktop/aa383614(v=vs.85).aspx)
### [Windows Task Scheduler](https://msdn.microsoft.com/en-us/library/windows/desktop/aa383614(v=vs.85).aspx)
### [Windows Task Scheduler](https://msdn.microsoft.com/en-us/library/windows/desktop/aa383614(v=vs.85).aspx)

You can use Window's built in Task Scheduler to automate InstaPy, using a variety of trigger types: time, login, computer idles, etc. To schedule a simple daily run of an Instapy script follow the below directions
1. Open [Windows Task Scheduler](https://msdn.microsoft.com/en-us/library/windows/desktop/aa383614(v=vs.85).aspx)
2. Select "Create Basic Task"
3. Fill out "Name" and "Description" as desired, click "Next"
4. On "Trigger" screen select how frequently to run, click "Next" (Frequency can be modified later)
5. On "Daily" screen, hit "Next"
6. "Action Screen" select "Start a program" and then click "Next"
7. "Program/script" enter the path, or browse to select the path to python. ([How to find python path on Windows](https://stackoverflow.com/questions/647515/how-can-i-get-python-path-under-windows))
8. "Add arguments" input the InstaPy script path you wish to run. (Example: C:\Users\USER_NAME\Documents\GitHub\InstaPy\craigquick.py)
9. "Start in" input Instapy install location (Example: C:\Users\USER_NAME\Documents\GitHub\InstaPy\). Click "Next"
10. To finish the process, hit "Finish"

### `cron`
You can add InstaPy to your crontab, so that the script will be executed regularly. This is especially useful for servers, but be sure not to break Instagrams follow and like limits.

```
# Edit or create a crontab
crontab -e
# Add information to execute your InstaPy regularly.
# With cd you navigate to your InstaPy folder, with the part after &&
# you execute your quickstart.py with python. Make sure that those paths match
# your environment.
45 */4 * * * cd /home/user/InstaPy && /usr/bin/python ./quickstart.py
```


### [Schedule](https://github.com/dbader/schedule)
> Schedule is an in-process scheduler for periodic jobs that uses the builder pattern for configuration. Schedule lets you run Python functions periodically at pre-determined intervals using a simple, human-friendly syntax.

```shell
pip install schedule
```

```python
from instapy import InstaPy
from instapy import smart_run
from instapy import set_workspace
import schedule
import time

#your login credentials
insta_username=''
insta_password=''

#path to your workspace
set_workspace(path=None)

def job():
  session = InstaPy(username=insta_username, password=insta_password)
  with smart_run(session):
    session.set_do_comment(enabled=True, percentage=20)
    session.set_comments(['Well done!'])
    session.set_do_follow(enabled=True, percentage=5, times=2)
    session.like_by_tags(['love'], amount=100, media='Photo')


schedule.every().day.at("6:35").do(job)
schedule.every().day.at("16:22").do(job)

while True:
  schedule.run_pending()
  time.sleep(10)
```

You can use Window's built in Task Scheduler to automate InstaPy, using a variety of trigger types: time, login, computer idles, etc. To schedule a simple daily run of an Instapy script follow the below directions
1. Open [Windows Task Scheduler](https://msdn.microsoft.com/en-us/library/windows/desktop/aa383614(v=vs.85).aspx)
2. Select "Create Basic Task"
3. Fill out "Name" and "Description" as desired, click "Next"
4. On "Trigger" screen select how frequently to run, click "Next" (Frequency can be modified later)
5. On "Daily" screen, hit "Next"
6. "Action Screen" select "Start a program" and then click "Next"
7. "Program/script" enter the path, or browse to select the path to python. ([How to find python path on Windows](https://stackoverflow.com/questions/647515/how-can-i-get-python-path-under-windows))
8. "Add arguments" input the InstaPy script path you wish to run. (Example: C:\Users\USER_NAME\Documents\GitHub\InstaPy\craigquick.py)
9. "Start in" input Instapy install location (Example: C:\Users\USER_NAME\Documents\GitHub\InstaPy\). Click "Next"
10. To finish the process, hit "Finish"

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
