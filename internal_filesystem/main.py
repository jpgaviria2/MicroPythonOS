import task_handler


import mpos.ui
mpos.ui.create_rootscreen()
mpos.ui.create_notification_bar()
mpos.ui.create_drawer(display)
mpos.ui.th = task_handler.TaskHandler(duration=5) # 5ms is recommended for MicroPython+LVGL on desktop

try:
    import freezefs_mount_builtin
except Exception as e:
    print("main.py: WARNING: could not import/run freezefs_mount_builtin: ", e)

from mpos import apps
apps.execute_script("builtin/system/button.py", True, False, False) # Install button handler through IRQ

def dummy():
    pass

import sys
if sys.platform == "esp32":
    apps.auto_connect()
else:
    # On unix/desktop, at least 24KB of stack size is needed in the REPL to make nostr work there
    #import _thread
    #_thread.stack_size(24*1024) # on unix/desktop, at least 24KB is needed for doing nostr connections from the REPL
    #_thread.start_new_thread(dummy, ()) # not just setting the stack_size but actually starting a thread to apply this globally
    pass

apps.restart_launcher()

# If we got this far without crashing, then no need to rollback the update:
try:
    import ota.rollback
    ota.rollback.cancel()
except Exception as e:
    print("main.py: warning: could not mark this update as valid:", e)
