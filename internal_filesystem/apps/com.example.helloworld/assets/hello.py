import mpos.ui

def button_click(e):
    print("Button clicked!")

scr = lv.obj()

# Create a button with a label
btn = lv.button(scr)
btn.align(lv.ALIGN.CENTER, 0, 0)
#btn.set_size(lv.pct(100),lv.pct(100))
btn.add_event_cb(button_click,lv.EVENT.CLICKED,None)
label = lv.label(btn)
label.set_text('Hello World!')

mpos.ui.load_screen(scr)

# Optional janitor that cleans up when the app is backgrounded:
def janitor_cb(timer):
    if lv.screen_active() != scr:
        print("app backgrounded, cleaning up...")
        janitor.delete()
        # No cleanups to do, but in a real app, you might stop timers, deinitialize hardware devices you used, close network connections, etc.

janitor = lv.timer_create(janitor_cb, 1000, None)
