# Hardware initialization for Unix and MacOS systems

import lcd_bus
import lvgl as lv
import sdl_display

# Add lib/ to the path for modules, otherwise it will only search in ~/.micropython/lib and /usr/lib/micropython
import sys
sys.path.append('lib/')

import mpos.ui
import mpos.clipboard

# Same as Waveshare ESP32-S3-Touch-LCD-2
TFT_HOR_RES=320
TFT_VER_RES=240

#TFT_HOR_RES=640
#TFT_VER_RES=480

# 4:3 DVD resolution:
#TFT_HOR_RES=720
#TFT_VER_RES=576

# 16:9 resolution:
#TFT_HOR_RES=1024
#TFT_VER_RES=576

# 16:9 good resolution but fairly small icons:
#TFT_HOR_RES=1280
#TFT_VER_RES=720

# Even HD works:
#TFT_HOR_RES=1920
#TFT_VER_RES=1080

bus = lcd_bus.SDLBus(flags=0)

buf1 = bus.allocate_framebuffer(TFT_HOR_RES * TFT_VER_RES * 2, 0)

display = sdl_display.SDLDisplay(data_bus=bus,display_width=TFT_HOR_RES,display_height=TFT_VER_RES,frame_buffer1=buf1,color_space=lv.COLOR_FORMAT.RGB565)
# display.set_dpi(65) # doesn't seem to change the default 130...
display.init()
# display.set_dpi(65) # doesn't seem to change the default 130...

import sdl_pointer
mouse = sdl_pointer.SDLPointer()

def catch_escape_key(indev, indev_data):
    global sdlkeyboard
    #print(f"keypad_cb {indev} {indev_data}")
    #key = indev.get_key() # always 0
    #print(f"key {key}")
    #key = indev_data.key
    #state = indev_data.state
    #print(f"indev_data: {state} and {key}") # this catches the previous key release instead of the next key press
    pressed, code = sdlkeyboard._get_key() # get the current key and state
    print(f"catch_escape_key caught: {pressed}, {code}")
    if pressed == 1 and code == 27:
        mpos.ui.back_screen()
    sdlkeyboard._read(indev, indev_data)

import sdl_keyboard
sdlkeyboard = sdl_keyboard.SDLKeyboard()
sdlkeyboard._indev_drv.set_read_cb(catch_escape_key) # check for escape
sdlkeyboard.set_paste_text_callback(mpos.clipboard.paste_text)

#def keyboard_cb(event):
 #   global canvas
  #  event_code=event.get_code()
   # print(f"boot_unix: code={event_code}") # target={event.get_target()}, user_data={event.get_user_data()}, param={event.get_param()}
#keyboard.add_event_cb(keyboard_cb, lv.EVENT.ALL, None)

# On the Waveshare ESP32-S3-Touch-LCD-2, the camera is hard-wired to power on,
# so it needs a software power off to prevent it from staying hot all the time and quickly draining the battery.
# 1) Initialize camera, otherwise it doesn't reply to I2C commands:
try:
    from camera import Camera
    cam = Camera(data_pins=[12,13,15,11,14,10,7,2],vsync_pin=6,href_pin=4,sda_pin=21,scl_pin=16,pclk_pin=9,xclk_pin=8,xclk_freq=20000000,powerdown_pin=-1,reset_pin=-1,pixel_format=PixelFormat.RGB565,frame_size=FrameSize.R240X240,grab_mode=GrabMode.LATEST)
    cam.deinit()
except Exception as e:
    print(f"camera init for power off got exception: {e}")
# 2) Soft-power off camera, otherwise it uses a lot of current for nothing:
try:
    from machine import Pin, I2C
    i2c = I2C(1, scl=Pin(16), sda=Pin(21))  # Adjust pins and frequency
    devices = i2c.scan()
    print("Scan of I2C bus on scl=16, sda=21:")
    print([hex(addr) for addr in devices]) # finds it on 60 = 0x3C after init
    camera_addr = 0x3C # for OV5640
    reg_addr = 0x3008
    reg_high = (reg_addr >> 8) & 0xFF  # 0x30
    reg_low = reg_addr & 0xFF         # 0x08
    power_off_command = 0x42 # Power off command
    i2c.writeto(camera_addr, bytes([reg_high, reg_low, power_off_command]))
except Exception as e:
    print(f"Warning: powering off camera got exception: {e}")

print("boot_unix.py finished")
