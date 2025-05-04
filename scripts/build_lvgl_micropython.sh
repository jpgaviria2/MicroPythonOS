# Build for https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-2:
# --ota: support Over-The-Air updates
# --partition size: both OTA partitions are 4MB
# --flash-size: total flash size is 16MB
# 
pushd ~/sources/lvgl_micropython

python3 make.py --ota --partition-size=4194304 --flash-size=16 esp32 BOARD=ESP32_GENERIC_S3 BOARD_VARIANT=SPIRAM_OCT DISPLAY=st7789 INDEV=cst816s USER_C_MODULE="/home/user/sources/micropython-camera-API/src/micropython.cmake" FROZEN_MANIFEST=~/sources/PiggyOS/manifest.py

# dev build:
#python3 make.py --ota --partition-size=4194304 --flash-size=16 esp32 BOARD=ESP32_GENERIC_S3 BOARD_VARIANT=SPIRAM_OCT DISPLAY=st7789 INDEV=cst816s USER_C_MODULE="/home/user/sources/micropython-camera-API/src/micropython.cmake" 

popd
