# Appium Testing enviroment 

![Instapy](https://i.imgur.com/sJzfZsL.jpg)

This guide describes how to setup an enviroment for testing the new appium instapy refactoring.

1. Install the appium python wrapper on your terminal: `pip install Appium-Python-Client`
2.  Download and install [appium](https://github.com/appium/appium-desktop/releases/tag/v1.13.0)
3.  Download and install [Andriod Studio](https://developer.android.com/studio)
4.  Download [instagrams' apk](https://apkpure.com/instagram/com.instagram.android/download/169474968-APK?from=variants%2Fversion)
5. Start a new Android Studio (AS) project:
	- Launch AS
	- Start new AS project
	- Add no activity
	- Leave default settings, with Java as a language
	- Check "this project will support instant apps"
	- Finish
6.  Let graddle finish building and sync (takes a few minutes)
7. Create a new emulator in the AVD manager
8.  Go to the android studio terminal (bottom of the screen): `cd C:\Users\YOUR NAME HERE\AppData\Local\Android\Sdk\platform-tools`  or whatever path you have to the `platform-tools` folder
9. Install the instagram apk: `adb install [INSERT THE PATH TO YOUR DOWNLOADED INSTAGRAM APK]`
10.  Add the `ANDROID_HOME` variable to your enviromental varibles with path being the path to `[FULL PATH HERE]/Sdk/` mentioned in earlier steps
11. Start your appium server with default settings
12. Launch the emulator
13. Give it time for the emulator to setup everything (AS will stop showing messages in the bottom)
14. Make sure you enter the right device name on your test file (You can find it by running `adb devices` in the android terminal) along with your instagram credentials
15. Test your script

## Disclaimers & Requirements

- If you are trying to use development tools, make sure you have JDK 8 or below 
- Make sure GPU acceleration is turned off when you create your emulator (use software option)
