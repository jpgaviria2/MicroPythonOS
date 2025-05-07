pkill -f "python.*mpremote"

appname="$1"

pushd internal_filesystem/

if [ ! -z "$appname" ]; then
	echo "Installing one app: $appname"
	appdir="apps/com.example.$appname/"
	if [ ! -d "$appdir" ]; then
		echo "$appdir doesn't exist so taking the builtin/"
		appdir="builtin/apps/com.example.$appname/"
		if [ ! -d "$appdir" ]; then
			echo "$appdir also doesn't exist, exiting..."
			exit 1
		fi
	fi
	~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py fs cp -r "$appdir" :/apps/
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
~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py fs cp -r data :/

popd

~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py reset
