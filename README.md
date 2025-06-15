MicroPythonOS
=======

This is an operating system for microcontrollers like the ESP32.

It's written entirely in MicroPython, including device drivers, interrupt handlers, boot code, multitasking, display handling.

The architecure is inspired by the Android operating system for smartphones:
- 'thin' operating system with facilities for apps
- 'everything is an app' idea
- making it as simple as possible for developers to build new apps

## Installation

See https://install.MicroPythonOS.com

## Apps

The operating system comes with a few apps built-in that are necessary to bootstrap:
- launcher: to be able to start apps
- wificonf: to be able to connect to the wifi
- appstore: to be able to download and install new apps
- osupdate: to download and install operating system updates

Other apps are available in the AppStore.

See https://apps.MicroPythonOS.com/

## Supported hardware

### ESP32 computers
- https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-2

### Desktop computers
- Linux desktop (uses SDL)
- MacOS should work. Untested.

### Raspberry Pi
- Should work, especially if it's running a Linux desktop like Raspbian. Untested.

## Architecture

- boot.py: initializes the hardware on ESP32 / boot_unix.py: initializes the hardware on linux desktop
- main.py: initializes the User Interface, contains helper functions for apps, and starts the launcher app

## Filesystem layout:

- /apps: new apps are downloaded and installed here
- /apps/com.example.app1: example app1 installation directory
- /apps/com.example.app1/MANIFEST.MF: info about app1 such as Name, Start-Script
- /apps/com.example.app1/mipmap-mdpi: medium dpi images for app1
- /apps/com.example.app1/mipmap-mdpi/icon_64x64.bin: icon for app1 (64x64 pixels)
- /builtin/: read-only filesystem that's compiled in and mounted at boot by main.py
- /builtin/apps: apps that are builtin and necessary for minimal facilities (launcher, wificonf, appstore etc)
- /builtin/res/mipmap-mdpi/default_icon_64x64.bin: default icon for apps that don't have one
- /data/: place where apps store their data
- /data/images/: place where apps (like the camera) store their images
- /data/com.example.app1/: storage (usually config.json) specific to com.example.app1

# Building

Prepare all the sources:

```
mkdir ~/MicroPythonOS
cd ~/MicroPythonOS

git clone https://github.com/MicroPythonOS/MicroPythonOS.git

git clone https://github.com/MicroPythonOS/freezeFS

git clone https://github.com/cnadler86/micropython-camera-API
echo 'include("~/MicroPythonOS/lvgl_micropython/build/manifest.py")' >> micropython-camera-API/src/manifest.py

git clone https://github.com/MicroPythonOS/lvgl_micropython

git clone https://github.com/MicroPythonOS/secp256k1-embedded-ecdh
```


Start the build for ESP32:

```
cd ~/projects/MicroPythonOS/MicroPythonOS
```


```
./scripts/build_lvgl_micropython.sh esp32 prod
```

Or if you want to build for development, so without any preinstalled files, do:

```
./scripts/build_lvgl_micropython.sh esp32 dev
```

Now make sure your ESP32 is in bootloader mode (long-press the BOOT button if you're already running MicroPythonOS) and install it with:

```
./scripts/flash_over_usb.sh
```

If you made a 'devbuild', then you probably want to install all files and apps manually:

```
./scripts/install.sh
```

Release checklist
=================
- Make sure CURRENT_OS_VERSION in main.py is incremented
- Make sure version numbers of apps that have been changed are incremented:
	# everything that changed:
	git diff --stat 0.0.4
	# manifests that might have already had their version number incremented:
	git diff 0.0.4 -- internal_filesystem/apps/*/META-INF/*
	git diff 0.0.4 -- internal_filesystem/builtin/apps/*/META-INF/*
- Update CHANGELOG
- commit and push all code
- tag MicroPythonOS and external apps like LightningPiggy
- ./scripts/bundle_apps.sh
- ./scripts/build_lvgl_micropython.sh esp32 prod
- ./scripts/release_to_updates.sh
- ./scripts/release_to_install.sh

Building for desktop
====================
Building to run as an app on the Linux desktop or MacOS (untested) is supported.

To do so, make sure you have the necessary dependencies:
- see https://github.com/MicroPythonOS/lvgl-micropython/
- sudo apt install libv4l-dev # for webcam.c

...and then run:

```
cd ~/projects/MicroPythonOS/MicroPythonOS/

```
./scripts/build_lvgl_micropython.sh unix dev
```

or

```
./scripts/build_lvgl_micropython.sh macOS dev
```

Then to run it, do:

```
./scripts/run_desktop.sh
```
