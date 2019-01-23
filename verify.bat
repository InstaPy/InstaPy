@ECHO OFF

REM[Checking if python is installed. If not, let the user know and quit.]
python --version
if ERRORLEVEL 1 GOTO :pythonNotInstalledExit
if not ERRORLEVEL 1 GOTO :pythonInstalled

:pythonInstalled
echo python installed

REM[Checking if pip is installed, If not, install it.]
pip --version
if ERRORLEVEL 1 GOTO :errorNoPip
if not ERRORLEVEL 1 GOTO :pipInstalled

:errorNoPip
echo Error^: Pip not installed, installing now
REM[The following two lines download and install pip.]
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py

:pipInstalled
echo pip installed

REM[Checking for chrome in the program file x86 version of the chrome standard directory]
cd "C:\Program Files (x86)\Google\Chrome\Application"
if ERRORLEVEL 1 GOTO :checkChromeV2
if not ERRORLEVEL 1 echo directory found.. checking for chrome
if EXIST "chrome.exe" GOTO :chromeInstalled
if not EXIST "chrome.exe" GOTO :chromeNotInstalledExit

REM[Checking for chrome in the program files version of the chrome standard directory]
:checkChromeV2
cd "C:\Program Files\Google\Chrome\Application"
if ERRORLEVEL 1 GOTO :chromeNotInstalledExit
if not ERRORLEVEL 1 echo directory found.. checking for chrome
if EXIST "chrome.exe" GOTO :chromeInstalled
if not EXIST "chrome.exe" GOTO :chromeNotInstalledExit

:chromeInstalled
echo chrome installed

pip install instapy
cls

echo BATCH SESSION SUCCESSFUL(PYTHON, PIP, CHROME, AND INSTAPY ALL VERIFIED AND INSTALLED) YOU MAY EXIT NOW
pause
GOTO :EOF

REM[This goto is used when python is not installed on the users machine.]
REM[Since it is a vital asset to InstaPy, the script is not allowed to continue until python is verified and installed on the machine]
:pythonNotInstalledExit
echo python not installed
echo you must install python before using InstaPy. please visit https://www.python.org/downloads/ and download the latest version of python 3 for your operating system.
echo python installed: no
echo pip installed: unchecked
echo chrome installed: unchecked
echo InstaPy installation: incompleted
pause
GOTO :EOF

REM[this is used when chrome is not installed on the users machine.]
REM[Since it is a vital asset to InstaPy, the script is not allowed to continue until chrome is verified and installed on the machine]
:chromeNotInstalledExit
echo chrome not installed
echo you must install chrome before using InstaPy. please visit https://www.google.com/chrome/ and download the correct version for your operating system.
echo python installed: yes
echo pip installed: yes
echo chrome installed: no
echo InstaPy installation: incompleted
pause