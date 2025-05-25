# Hardware initialization for Unix and MacOS systems

import lcd_bus
import lvgl as lv
import sdl_display

import mpos.ui

#TFT_HOR_RES=640
#TFT_VER_RES=480
TFT_HOR_RES=320
TFT_VER_RES=240

bus = lcd_bus.SDLBus(flags=0)

buf1 = bus.allocate_framebuffer(TFT_HOR_RES * TFT_VER_RES * 2, 0)

display = sdl_display.SDLDisplay(data_bus=bus,display_width=TFT_HOR_RES,display_height=TFT_VER_RES,frame_buffer1=buf1,color_space=lv.COLOR_FORMAT.RGB565)
display.init()

import sdl_pointer
mouse = sdl_pointer.SDLPointer()

#import sdl_keyboard
#keyboard = sdl_keyboard.SDLKeyboard()


#def keyboard_cb(event):
 #   global canvas
  #  event_code=event.get_code()
   # print(f"boot_unix: code={event_code}") # target={event.get_target()}, user_data={event.get_user_data()}, param={event.get_param()}

#keyboard.add_event_cb(keyboard_cb, lv.EVENT.ALL, None)

print("boot_unix.py finished")

