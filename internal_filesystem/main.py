import task_handler
import _thread
import lvgl as lv

# Allow LVGL M:/path/to/file or M:relative/path/to/file to work for image set_src etc
import fs_driver
fs_drv = lv.fs_drv_t()
fs_driver.fs_register(fs_drv, 'M')

import mpos.apps
import mpos.config
import mpos.ui

prefs = mpos.config.SharedPreferences("com.micropythonos.settings")

# Load and set theme:
theme_light_dark = prefs.get_string("theme_light_dark", "light") # default to a light theme
theme_dark_bool = ( theme_light_dark == "dark" )
primary_color = lv.theme_get_color_primary(None)
color_string = prefs.get_string("theme_primary_color")
if color_string:
    try:
        color_string = color_string.replace("0x", "").replace("#", "").strip().lower()
        color_int = int(color_string, 16)
        print(f"Setting primary color: {color_int}")
        primary_color = lv.color_hex(color_int)
    except Exception as e:
        print(f"Converting color setting '{color_string}' to lv_color_hex() got exception: {e}")
theme = lv.theme_default_init(display._disp_drv, primary_color, lv.color_hex(0xFBDC05), theme_dark_bool, lv.font_montserrat_12)

#display.set_theme(theme)

mpos.ui.init_rootscreen()
mpos.ui.create_notification_bar()
mpos.ui.create_drawer(display)
mpos.ui.handle_back_swipe()
mpos.ui.handle_top_swipe()
mpos.ui.th = task_handler.TaskHandler(duration=5) # 5ms is recommended for MicroPython+LVGL on desktop

try:
    import freezefs_mount_builtin
except Exception as e:
    # This will throw an exception if there is already a "/builtin" folder present
    print("main.py: WARNING: could not import/run freezefs_mount_builtin: ", e)

from mpos import apps

apps.execute_script("builtin/system/button.py", True) # Install button handler through IRQ

try:
    import mpos.wifi
    import mpos.apps
    _thread.stack_size(mpos.apps.good_stack_size())
    _thread.start_new_thread(mpos.wifi.WifiService.auto_connect, ())
except Exception as e:
    print(f"Couldn't start mpos.wifi.WifiService.auto_connect thread because: {e}")

apps.restart_launcher()

# If we got this far without crashing, then no need to rollback the update:
try:
    import ota.rollback
    ota.rollback.cancel()
except Exception as e:
    print("main.py: warning: could not mark this update as valid:", e)
