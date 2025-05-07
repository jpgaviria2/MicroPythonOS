PiggyOS
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

git clone https://github.com/LightningPiggy/PiggyOS.git

git clone https://github.com/bixb922/freezeFS
~/sources/PiggyOS/scripts/freezefs_mount_builtin.sh

git clone https://github.com/cnadler86/micropython-camera-API
echo 'include("~/sources/lvgl_micropython/build/manifest.py")' >> micropython-camera-API/src/manifest.py

git clone https://github.com/lvgl-micropython/lvgl_micropython
cp ~/sources/PiggyOS/patches/lv_conf.h lvgl_micropython/lib/

cd lvgl_micropython/lib/micropython
patch -p1 < ~/sources/PiggyOS/patches/lvgl_micropython*.patch
```

Start the build:

```
~/sources/PiggyOS/scripts/build_lvgl_micropython.sh
```

Or if you want to build for development, so without any preinstalled files, do:

```
~/sources/PiggyOS/scripts/build_lvgl_micropython.sh devbuild
```

Now install it with:

```
~/sources/PiggyOS/scripts/flash_over_usb.sh
```

If you made a 'devbuild', then you probably want to install all files and apps manually:

```
~/sources/PiggyOS/scripts/install.sh
```


