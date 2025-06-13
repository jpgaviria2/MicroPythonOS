# Hardware initialization for Unix and MacOS systems

import lcd_bus
import lvgl as lv
import sdl_display
import task_handler


# Add lib/ to the path for modules, otherwise it will only search in ~/.micropython/lib and /usr/lib/micropython
import sys
sys.path.append('lib/')


import mpos.ui


#TFT_HOR_RES=640
#TFT_VER_RES=480
TFT_HOR_RES=320
TFT_VER_RES=240

def window_cb(args): # doesn't get called
    print(f"Window callback: {args}")

bus = lcd_bus.SDLBus(flags=0)
bus.register_window_callback(window_cb)

# bus.set_window_size(320,240,-1,False) # -1 might be 25 but it always becomes black, except for format 0

buf1 = bus.allocate_framebuffer(TFT_HOR_RES * TFT_VER_RES * 2, 0)

display = sdl_display.SDLDisplay(data_bus=bus,display_width=TFT_HOR_RES,display_height=TFT_VER_RES,frame_buffer1=buf1,color_space=lv.COLOR_FORMAT.RGB565)
display.init()

import sdl_pointer
mouse = sdl_pointer.SDLPointer()

import sdl_keyboard
sdlkeyboard = sdl_keyboard.SDLKeyboard()

#indev.set_read_cb(keypad_cb)

# seems indev isn't properly initialized
def keypad_cb(indev, indev_data):
    global sdlkeyboard
    #print(f"keypad_cb {indev} {indev_data}")
    #key = indev.get_key() # always 0
    #print(f"key {key}")
    #key = indev_data.get("key")
    #print(f"key {key}")
    pressed, code = sdlkeyboard._get_key()
    print(f"periodic pressed: {pressed}, code: {code}")
    sdlkeyboard._read(indev, indev_data)
    # I mean we could read the key and put it in the textarea but I want some kind of keypress :-/

sdlkeyboard._indev_drv.set_read_cb(keypad_cb) # check for escape

def keyboard_cb(event):
    event_code=event.get_code()
    print(f"keyboard_test YES: code={event_code}") # target={event.get_target()}, user_data={event.get_user_data()}, param={event.get_param()}


def button_cb(event):
    event_code=event.get_code()
    name = mpos.ui.get_event_name(event_code)
    print(f"button_cb YES: code={event_code} and name {name}")

# for some reason, this text areas is receiving mouse events, and draw events, but not key events...
def ta_callback_again(event):
    event_code=event.get_code()
    if event_code in [19,23,25,26,27,28,29,30,49]:
        return
    name = mpos.ui.get_event_name(event_code)
    print(f"ta_callback_again {event_code} and {name}")
    #print(f"ta_callback_again: code={event_code}") # target={event.get_target()}, user_data={event.get_user_data()}, param={event.get_param()}

sdlkeyboard.add_event_cb(keyboard_cb, lv.EVENT.ALL, None)


#group = lv.group_create()
#group = keyboard.get_group()

th = task_handler.TaskHandler(duration=5) # 5ms is recommended for MicroPython+LVGL on desktop

screen = lv.screen_active()

b = lv.button(screen)
b.center()
b.add_event_cb(button_cb, lv.EVENT.ALL, None)
#group.add_obj(b)

ta = lv.textarea(screen)
ta.set_one_line(True)
ta.align(lv.ALIGN.TOP_LEFT,0,0)
ta.add_event_cb(ta_callback_again, lv.EVENT.ALL, None)

#group.add_obj(ta)

takeyboard = lv.keyboard(screen)
takeyboard.set_textarea(ta)


# this does something, but just gives indev 0, being error...
#indev = lv.indev_create()
#indev.set_type(lv.INDEV_TYPE.KEYPAD)
#indev.set_read_cb(keypad_cb) # check for escape



#keyboard.set_group(group)
