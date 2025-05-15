# Build for https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-2:
# --ota: support Over-The-Air updates
# --partition size: both OTA partitions are 4MB
# --flash-size: total flash size is 16MB
# 

buildtype="$1"

echo "Usage: $0 [devbuild/unix]"
echo "Example: $0"
echo "Example: $0 devbuild"
echo
echo "Adding 'devbuild' will build without any preinstalled files or builtin/ filsystem, so it will just start with a black screen and you'll have to do: ./scripts/install.sh to install the User Interface."
sleep 2

pushd ~/sources/lvgl_micropython

manifest="FROZEN_MANIFEST=/home/user/sources/PiggyOS/manifest.py"
if [ "$buildtype" == "devbuild" ]; then
	manifest=""
fi

if [ "$buildtype" != "unix" -a "$buildtype" != "macOS" ]; then
	python3 make.py --ota --partition-size=4194304 --flash-size=16 esp32 BOARD=ESP32_GENERIC_S3 BOARD_VARIANT=SPIRAM_OCT DISPLAY=st7789 INDEV=cst816s USER_C_MODULE="/home/user/sources/micropython-camera-API/src/micropython.cmake" "$manifest"
else
	# build for desktop
	python3 make.py "$buildtype" DISPLAY=sdl_display INDEV=sdl_pointer INDEV=sdl_keyboard
fi

popd
