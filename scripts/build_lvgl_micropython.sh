
target="$1"
buildtype="$2"


if [ -z "$target" -o -z "$buildtype" ]; then
	echo "Usage: $0 <esp32 or unix or macos> <dev or prod>"
	echo "Example: $0"
	echo "Example: $0 devbuild"
	echo
	echo "A 'dev' build is without any preinstalled files or builtin/ filsystem, so it will just start with a black screen and you'll have to do: ./scripts/install.sh to install the User Interface."
	echo "A 'prod' build has the files from manifest*.py frozen in."
	exit 1
fi

pushd ~/sources/lvgl_micropython

manifest=""

if [ "$target" == "esp32" ]; then
	if [ "$buildtype" == "prod" ]; then
		manifest="FROZEN_MANIFEST=/home/user/sources/PiggyOS/manifest.py"
	fi
	# Build for https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-2.
	# See https://github.com/lvgl-micropython/lvgl_micropython
	# --ota: support Over-The-Air updates
	# --partition size: both OTA partitions are 4MB
	# --flash-size: total flash size is 16MB
	# --debug: enable debugging from ESP-IDF but makes copying files to it very slow
	# --dual-core-threads: disabled GIL, run code on both CPUs
	# --task-stack-size={stack size in bytes}
	# CONFIG_* sets ESP-IDF options
	# listing processes on the esp32 still doesn't work because no esp32.vtask_list_threads() or something
	# CONFIG_FREERTOS_USE_TRACE_FACILITY=y
	# CONFIG_FREERTOS_VTASKLIST_INCLUDE_COREID=y
	# CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS=y
	#python3 make.py --ota --partition-size=4194304 --flash-size=16 esp32 BOARD=ESP32_GENERIC_S3 BOARD_VARIANT=SPIRAM_OCT DISPLAY=st7789 INDEV=cst816s USER_C_MODULE="/home/user/sources/micropython-camera-API/src/micropython.cmake" CONFIG_FREERTOS_USE_TRACE_FACILITY=y CONFIG_FREERTOS_VTASKLIST_INCLUDE_COREID=y CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS=y "$manifest"
	python3 make.py --ota --partition-size=4194304 --flash-size=16 esp32 BOARD=ESP32_GENERIC_S3 BOARD_VARIANT=SPIRAM_OCT DISPLAY=st7789 INDEV=cst816s USER_C_MODULE=/home/user/sources/micropython-camera-API/src/micropython.cmake USER_C_MODULE=/home/user/sources/PiggyOS/c_mpos/secp256k1-embedded_kdmukai/micropython.cmake CONFIG_FREERTOS_USE_TRACE_FACILITY=y CONFIG_FREERTOS_VTASKLIST_INCLUDE_COREID=y CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS=y "$manifest"
elif [ "$target" == "unix" -o "$target" == "macos" ]; then
	if [ "$buildtype" == "prod" ]; then
		manifest="FROZEN_MANIFEST=/home/user/sources/PiggyOS/manifest_unix.py"
	fi
	# build for desktop
	python3 make.py "$target" DISPLAY=sdl_display INDEV=sdl_pointer INDEV=sdl_keyboard "$manifest"
else
	echo "invalid target $target"
fi

popd
