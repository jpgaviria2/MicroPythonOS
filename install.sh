pkill -f "python.*mpremote"

pushd internal_filesystem/

~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py fs cp boot.py :/boot.py
~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py fs cp main.py :/main.py
~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py fs cp autostart.py :/autostart.py

~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py fs cp -r apps :/
~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py fs cp -r lib :/
~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py fs cp -r resources :/
~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py fs cp -r data :/

popd

~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py reset
