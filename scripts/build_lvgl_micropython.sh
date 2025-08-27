
target="$1"
buildtype="$2"


if [ -z "$target" -o -z "$buildtype" ]; then
	echo "Usage: $0 <esp32 or unix or macos> <dev or prod>"
	echo "Example: $0 unix dev"
	echo "Example: $0 esp32 prod"
	echo
	echo "A 'dev' build is without any preinstalled files or builtin/ filsystem, so it will just start with a black screen and you'll have to do: ./scripts/install.sh to install the User Interface."
	echo "A 'prod' build has the files from manifest*.py frozen in. Don't forget to run: ./scripts/freezefs_mount_builtin.sh !"
	exit 1
fi

if [ "$buildtype" == "prod" ]; then
	./scripts/freezefs_mount_builtin.sh
fi

pushd ~/projects/MicroPythonOS/lvgl_micropython

manifest=""

if [ "$target" == "esp32" ]; then
	if [ "$buildtype" == "prod" ]; then
		manifest="FROZEN_MANIFEST=/home/user/projects/MicroPythonOS/MicroPythonOS/manifest.py"
	else
		echo "Note that you can also prevent the builtin filesystem from being mounted by umounting it and creating a builtin/ folder."
	fi
	# Build for ESP32-S3 3.5 inch Capacitive Touch Display (320×480 HVGA)
	# Updated from Waveshare ESP32-S3-Touch-LCD-2 (320×240 QVGA)
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
	python3 make.py --ota --partition-size=4194304 --flash-size=16 esp32 BOARD=ESP32_GENERIC_S3 BOARD_VARIANT=SPIRAM_OCT DISPLAY=st7789 INDEV=cst816s USER_C_MODULE=/home/user/projects/MicroPythonOS/micropython-camera-API/src/micropython.cmake USER_C_MODULE=/home/user/projects/MicroPythonOS/secp256k1-embedded-ecdh/micropython.cmake USER_C_MODULE=/home/user/projects/MicroPythonOS/MicroPythonOS/c_mpos/micropython.cmake CONFIG_FREERTOS_USE_TRACE_FACILITY=y CONFIG_FREERTOS_VTASKLIST_INCLUDE_COREID=y CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS=y "$manifest"
elif [ "$target" == "unix" -o "$target" == "macos" ]; then
	if [ "$buildtype" == "prod" ]; then
		manifest="FROZEN_MANIFEST=/home/user/projects/MicroPythonOS/MicroPythonOS/manifest_unix.py"
	fi
	# build for desktop
	#python3 make.py "$target"  DISPLAY=sdl_display INDEV=sdl_pointer INDEV=sdl_keyboard "$manifest"
	# LV_CFLAGS are passed to USER_C_MODULES
	# STRIP= makes it so that debug symbols are kept
	python3 make.py "$target" LV_CFLAGS="-g -O0 -ggdb -ljpeg" STRIP=  DISPLAY=sdl_display INDEV=sdl_pointer INDEV=sdl_keyboard "$manifest"
else
	echo "invalid target $target"
fi

popd
