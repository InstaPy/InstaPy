# Appium Testing enviroment 

![Instapy](https://i.imgur.com/sJzfZsL.jpg)

This guide describes how to setup an enviroment for testing the new appium instapy refactoring.

1. Install the appium python wrapper on your terminal: `pip install Appium-Python-Client`

2. Download and install [appium](https://github.com/appium/appium-desktop/releases/tag/v1.13.0)

3. Download and install [Andriod Studio](https://developer.android.com/studio)

4.  Download [instagrams' apk](https://apkpure.com/instagram/com.instagram.android/download/169474968-APK?from=variants%2Fversion)
  
    Note: make sure to map the correct apk variant with the CPU/ABI flavor of your android device

5. Start a new Android Studio (AS) project:
	- Launch AS
	- Click "Configure -> AVD Manager"
	
6.  Create a new emulator in the AVD manager by Click "Create Virtual Device" and follow it steps
7. Go to the android studio terminal (bottom of the screen): `cd C:\Users\YOUR NAME HERE\AppData\Local\Android\Sdk\platform-tools`  or whatever path you have to the `platform-tools` folder

8. Install the instagram apk: `adb install [INSERT THE PATH TO YOUR DOWNLOADED INSTAGRAM APK]`

9. Add the `ANDROID_HOME` variable to your environment variables with path being the path to `[FULL PATH HERE]/Sdk/` mentioned in earlier steps

For Ubuntu: Dont use the symbol '~' in the path, because the appium parser doesnt seem to recognize it.

10. Start your appium server with default settings

11. Launch the emulator

12. Give it time for the emulator to setup everything (AS will stop showing messages in the bottom)

13. Make sure you enter the right device name on your test file (You can find it by running `adb devices` in the android terminal) along with your instagram credentials

14. Test your script

# Running Android on Raspberry Pi

[See here](https://www.raspberrypi.org/magpi/android-raspberry-pi/)

## Disclaimers & Requirements

- If you are trying to use development tools, make sure you have JDK 8 or below 
- Make sure GPU acceleration is turned off when you create your emulator (use software option)
