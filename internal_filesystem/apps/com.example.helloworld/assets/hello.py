import time
myscreen = lv.screen_active()

print("Hello World running!")

label = lv.label(myscreen)
label.set_text("Hello World!")

while lv.screen_active() == myscreen
    time.sleep_ms(100)

