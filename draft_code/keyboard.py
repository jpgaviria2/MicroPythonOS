

appscreen = lv.screen_active()
appscreen.clean()

password_ta=lv.textarea(appscreen)
password_ta.set_size(200,30)
password_ta.set_one_line(True)
password_ta.align(lv.ALIGN.TOP_MID, 5, 30)
password_ta.set_text("bla")
password_ta.set_placeholder_text("Password")

#password_ta.add_event_cb(password_ta_cb,lv.EVENT.CLICKED,None)

#oskeyboard=lv.keyboard(appscreen)
#oskeyboard.set_size(lv.pct(100),120)
#oskeyboard.align(lv.ALIGN.BOTTOM_LEFT,0,0)
#oskeyboard.set_textarea(password_ta)

#keyboard.add_event_cb(keyboard_cb,lv.EVENT.READY,None)
#keyboard.add_event_cb(keyboard_cb,lv.EVENT.CANCEL,None)
#keyboard.add_event_cb(keyboard_value_changed_cb,lv.EVENT.VALUE_CHANGED,None)

#oskeyboard.add_event_cb(touch_cb, lv.EVENT.ALL, None)



import sdl_keyboard
keyboard = sdl_keyboard.SDLKeyboard()

def keyboard_cb(event):
    global canvas
    event_code=event.get_code()
    print(f"boot_unix: code={event_code}") # target={event.get_target()}, user_data={event.get_user_data()}, param={event.get_param()}

keyboard.add_event_cb(keyboard_cb, lv.EVENT.ALL, None)
keyboard.group.add_obj(password_ta)
#keyboard.group.add_obj(oskeyboard)


def touch_cb(event):
    global canvas
    event_code=event.get_code()
    print(f"keyboard.py: code={event_code}") # target={event.get_target()}, user_data={event.get_user_data()}, param={event.get_param()}

password_ta.add_event_cb(touch_cb, lv.EVENT.ALL, None)
