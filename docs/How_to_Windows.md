# Installation guide for windows:

#### 0. Prerequisites:

##### 0.1 Google Chrome
- Download and install newest version of Google Chrome.
- Proceed with standard installation.
> [https://www.google.it/chrome/browser/desktop/index.html]

##### 0.2 Microsoft Build Tools 2015 
- Download and install Microsoft Build Tools 2015.
- Proceed with standard installation.
- Restart PC (recommended).
> [https://www.microsoft.com/en-us/download/details.aspx?id=48159]

##### 0.3 Microsoft Visual C++ 2015 Build Tools 
- Download and install Microsoft Visual C++ 2015 Build Tools.
- Proceed with standard installation.
- Restart PC (recommended).
> [http://landinghub.visualstudio.com/visual-cpp-build-tools]

##### 0.4 Microsoft .NET Framework V.3.5 (Including: .NET Framework 2.0 and 3.0, and includes .NET Framework 2.0 service pack 1 and .NET Framework 3.0 service pack 1)
- Download and install Microsoft .NET Framework V.3.5.
- Proceed with standard installation.
- Restart PC (recommended).
> [https://www.microsoft.com/it-it/download/details.aspx?id=21]

##### 0.5 GitHub Desktop 
- Download and install newest version of GitHub Desktop. 
> [https://desktop.github.com/]


#### 1. Install python:
- Download and install newest version of python (if you do the custom install don't forget to install the pip tool)
- recommended path C:\\Program Files (x86)\\
- Proceed with standard installation.
- Restart PC (recommended).
> [https://www.python.org/downloads/release/python-361/]


#### 2. Set python evironment:
- Open Control Panel » System » Advanced » Environment Variables.
- Click New and type the path where you have installed Python + /Scripts
- Usually PATH: C:\\Program Files (x86)\\Python36-32\\Scripts\\ and C:\\Program Files (x86)\\Python36-32\\
- Win7 and Win10 PATH: C:\\Users\\YOUR_USER_NAME\\AppData\\Local\\Programs\\Python\\Python36\\ and C:\\Users\\YOUR_USER_NAME\\AppData\\Local\\Programs\\Python\\Python36\\Scripts\\
- Restart PC (recommended).

#### 3.x Setup:

##### 3.1 Install Selenium
- Go to C:\\Program Files (x86)\\Python36-32\\Scripts
- press Shift + Right click and open command window (with admin rights !!) and type
- pip install selenium
- python -m pip install pyvirtualdisplay
- py get-pip.py

##### 3.2 Download the GUI (optional)
- Download the zip-File from the GUI-tool-for-InstaPy-script.
- follow the install instructions on this page.
- don't forget to copy the \*.exe files in the folder InstaPy-master.
> [https://github.com/Nemixalone/GUI-tool-for-InstaPy-script]

##### 3.3 Download the latest chromedriver
- Download the newest chrome driver.
- copy it in the folder \\assets
> [https://sites.google.com/a/chromium.org/chromedriver/downloads]


#### 4. Edit the instapy.py file
- Open file instapy.py an disabling the clarifai import
- comment the line "from .clarifai_util import check_image"
> `from .clarifai_util import check_image`


#### 5. Starting the script
- Start the Gui by clicking at the file InstaPy.exe
- Insert your parameters and press run
- After the first run the file quickstart.py is filled with your parameters
- now you can edit them manually in a editor (e.g. notepad pro)

### Now you can also start the script by opening a command window and running start.bat
