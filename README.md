MicroPythonOS
=======

This is an operating system for microcontrollers like the ESP32.

It's written entirely in MicroPython, including device drivers, interrupt handlers, boot code, multitasking, display handling.

The architecure is inspired by the Android operating system for smartphones:
- 'thin' operating system with facilities for apps
- 'everything is an app' idea
- making it as simple as possible for developers to build new apps

## Apps

The operating system comes with a few apps built-in that are necessary to bootstrap:
- launcher: to be able to start apps
- wificonf: to be able to connect to the wifi
- appstore: to be able to download and install new apps

Furthermore, these apps are also built-in for convenience:
- osupdate: to download and install operating system updates
- camera: to take pictures and videos
- imutest: to test the Inertial Measurement Unit (accelerometer)

## Supported hardware

- https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-2 

## Architecture

- boot.py: initializes the hardware
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

# Building

Prepare all the sources:

```
mkdir ~/sources/
cd ~/sources/

git clone https://github.com/MicroPythonOS/MicroPythonOS.git

git clone https://github.com/bixb922/freezeFS
~/sources/MicroPythonOS/scripts/freezefs_mount_builtin.sh

git clone https://github.com/cnadler86/micropython-camera-API
echo 'include("~/sources/lvgl_micropython/build/manifest.py")' >> micropython-camera-API/src/manifest.py

git clone https://github.com/lvgl-micropython/lvgl_micropython
cp ~/sources/MicroPythonOS/patches/lv_conf.h lvgl_micropython/lib/

cd lvgl_micropython/lib/micropython
patch -p1 < ~/sources/MicroPythonOS/patches/lvgl_micropython*.patch
```

Start the build:

```
~/sources/MicroPythonOS/scripts/build_lvgl_micropython.sh
```

Or if you want to build for development, so without any preinstalled files, do:

```
~/sources/MicroPythonOS/scripts/build_lvgl_micropython.sh devbuild
```

Now install it with:

```
~/sources/MicroPythonOS/scripts/flash_over_usb.sh
```

If you made a 'devbuild', then you probably want to install all files and apps manually:

```
~/sources/MicroPythonOS/scripts/install.sh
```

Release checklist
=================
- Make sure CURRENT_OS_VERSION in main.py is incremented
- Make sure version numbers of apps that have been changed are incremented
- commit and push all code
- ./scripts/bundle_apps.sh
- ./scripts/freezefs_mount_builtin.sh
- ./scripts/build_lvgl_micropython.sh
- copy_apps_to_server.sh
- copy_build_to_server.sh
- copy ~/sources/lvgl_micropython/build/lvgl_micropy_ESP32_GENERIC_S3-SPIRAM_OCT-16.bin to webinstaller
- update manifest of webinstaller
- push webinstaller

Building for desktop
====================
Building to run as an app on the Linux desktop or MacOS (untested) is supported.

To do so, make sure you have the necessary dependencies:
- see https://github.com/lvgl-micropython/
- sudo apt install libv4l-dev # for webcam.c

...and then run:

```
~/sources/MicroPythonOS/scripts/build_lvgl_micropython.sh unix
```

or

```
~/sources/MicroPythonOS/scripts/build_lvgl_micropython.sh macOS
```

To run it, it's recommended to symlink your ~/.micropython/lib folder into this project's lib:

```
ln -sf $(readlink -f internal_filesystem/lib) ~/.micropython/lib
```

Then to run it, do:

```
./scripts/run_desktop.sh
```
