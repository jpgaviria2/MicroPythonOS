pkill -f "python.*mpremote"

appname="$1"

if [ -z "$appname" ]; then
	echo "Usage: $0 [appname]"
	echo "Example: $0"
	echo "Example: $0 launcher"
	echo "Example: $0 wificonf"
	echo "Example: $0 appstore"
	sleep 2
fi

pushd internal_filesystem/

if [ ! -z "$appname" ]; then
	echo "Installing one app: $appname"
	appdir="apps/com.example.$appname/"
        target="apps/"
	if [ ! -d "$appdir" ]; then
		echo "$appdir doesn't exist so taking the builtin/"
		appdir="builtin/apps/com.example.$appname/"
                target="builtin/apps/"
		if [ ! -d "$appdir" ]; then
			echo "$appdir also doesn't exist, exiting..."
			exit 1
		fi
	fi
        ~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py mkdir "/apps"
        ~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py mkdir "/builtin"
        ~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py mkdir "/builtin/apps"
	~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py fs cp -r "$appdir" :/"$target"
	echo "start_app(\"/$appdir\")"
	~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py
	popd
	exit
fi


~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py fs cp boot.py :/boot.py
~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py fs cp main.py :/main.py

#~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py fs cp main.py :/system/button.py
#~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py fs cp autorun.py :/autorun.py
#~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py fs cp -r system :/

~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py fs cp -r apps :/
~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py fs cp -r builtin :/
~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py fs cp -r lib :/
~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py fs cp -r resources :/
#~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py fs cp -r data :/

popd

~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py reset
