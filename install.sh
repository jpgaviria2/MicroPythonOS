pkill -f "python.*mpremote"

~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py fs cp boot.py :/boot.py
~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py fs cp main.py :/main.py

~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py fs cp -r apps :/
~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py fs cp -r resources :/

~/sources/lvgl_micropython/lib/micropython/tools/mpremote/mpremote.py reset
