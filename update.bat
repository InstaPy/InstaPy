@echo off

pip install -U instapy
if ERRORLEVEL 1 GOTO :failure
if not ERRORLEVEL 1 GOTO :success

REM[used when update failed]
:failure
cls
echo an error occured. please try again. if the error persists please contact a developer.
pause
GOTO :EOF

REM[used when update is successful. also displays instapy version]
:success
cls
pip show instapy
echo.
echo update successful! the version of instapy is displayed above.
pause