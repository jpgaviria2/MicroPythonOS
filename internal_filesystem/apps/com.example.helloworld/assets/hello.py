# START OF COPY-PASTE FROM https://sim.lvgl.io/v9.0/micropython/ports/webassembly/

# Initialize

import display_driver # not needed, but included because the LVGL simulator does it
import lvgl as lv

# Create a button with a label

scr = lv.obj()
btn = lv.button(scr)
btn.align(lv.ALIGN.CENTER, 0, 0)
label = lv.label(btn)
label.set_text('Hello World!')
lv.screen_load(scr)

# END OF COPY-PASTE FROM https://sim.lvgl.io/v9.0/micropython/ports/webassembly/


def janitor_cb(timer):
    if lv.screen_active() != scr:
        print("app backgrounded, cleaning up...")
        janitor.delete()
        # No cleanups to do, but in a real app, you might stop timers, deinitialize hardware devices you used, close network connections, etc.

janitor = lv.timer_create(janitor_cb, 1000, None)
