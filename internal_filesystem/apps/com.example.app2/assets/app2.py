print("app2 is running")

import time
import _thread
print("App2 running")

# Quit flag
should_continue = True

def app2_thread():
	count=0
	while should_continue and appscreen == lv.screen_active():
		print(f"app2_thread: thread_id {_thread.get_ident()} - {count}")
		count+=1
		time.sleep(1)

_thread.start_new_thread(app2_thread, ())


# Label
label = lv.label(subwindow)
label.set_text("App2: 0")
label.align(lv.ALIGN.TOP_MID, 0, 10)
# Button
button = lv.button(subwindow)
button.set_size(100, 60)
button.align(lv.ALIGN.CENTER, 0, 0)
button_label = lv.label(button)
button_label.set_text("Quit")
button_label.center()
# Slider
slider = lv.slider(subwindow)
slider.set_range(0, 100)
slider.set_value(50, lv.ANIM.OFF)
slider.align(lv.ALIGN.BOTTOM_MID, 0, -30)
# Button callback
def button_cb(e):
    global should_continue
    print("Quit button clicked, exiting child")
    should_continue = False
button.add_event_cb(button_cb, lv.EVENT.CLICKED, None)
# Slider callback
def slider_cb(e):
    value = slider.get_value()
    #print("Child slider value:", value)
slider.add_event_cb(slider_cb, lv.EVENT.VALUE_CHANGED, None)
# Update loop
count = 0
while should_continue:
    count += 1
    #print("Child coroutine: Updating label to", count)
    label.set_text(f"App2: {count}")
    time.sleep_ms(1000) # shorter makes it more responive to the quit button
print("Child coroutine: Exiting")


