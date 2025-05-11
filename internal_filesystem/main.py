import task_handler
th = task_handler.TaskHandler(duration=5) # 5ms is recommended for MicroPython+LVGL on desktop

from mpos import ui
ui.create_rootscreen()
ui.create_notification_bar()
ui.create_drawer(display)

try:
    import freezefs_mount_builtin
except Exception as e:
    print("main.py: WARNING: could not import/run freezefs_mount_builtin: ", e)

from mpos import apps
apps.execute_script_new_thread("builtin/system/button.py", True, False, False) # Button handling through IRQ
apps.auto_connect()
apps.restart_launcher()

# If we got this far without crashing, then no need to rollback the update:
try:
    import ota.rollback
    ota.rollback.cancel()
except Exception as e:
    print("main.py: warning: could not mark this update as valid:", e)
