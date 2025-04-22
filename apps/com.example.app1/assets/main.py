print("running app1")

import time
print("Child coroutine: Creating UI")
# Label
label = lv.label(subwindow)
label.set_text("App1: 0")
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
# Quit flag
should_continue = True
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
    label.set_text(f"App1: {count}")
    time.sleep_ms(100) # shorter makes it more responive to the quit button
print("Child coroutine: Exiting")


