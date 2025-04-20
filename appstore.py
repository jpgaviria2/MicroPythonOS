import lvgl as lv
from machine import Pin, SPI
import st7789 
import lcd_bus
import machine
import task_handler
import cst816s
import i2c
import network
import urequests

# Pin configuration
SPI_BUS = 2
SPI_FREQ = 40000000
LCD_SCLK = 39
LCD_MOSI = 38
LCD_MISO = 40
LCD_DC = 42
LCD_CS = 45
LCD_BL = 1

I2C_BUS = 0
I2C_FREQ = 100000
TP_SDA = 48
TP_SCL = 47
TP_ADDR = 0x15
TP_REGBITS = 8

TFT_HOR_RES=320
TFT_VER_RES=240

lv.init()
spi_bus = machine.SPI.Bus(
    host=SPI_BUS,
    mosi=LCD_MOSI,
    miso=LCD_MISO,
    sck=LCD_SCLK
)
display_bus = lcd_bus.SPIBus(
    spi_bus=spi_bus,
    freq=SPI_FREQ,
    dc=LCD_DC,
    cs=LCD_CS,
)
display = st7789.ST7789(
    data_bus=display_bus,
    display_width=TFT_VER_RES,
    display_height=TFT_HOR_RES,
    backlight_pin=LCD_BL,
    color_space=lv.COLOR_FORMAT.RGB565,
    color_byte_order=st7789.BYTE_ORDER_BGR,
    rgb565_byte_swap=True,
)
display.init()
display.set_power(True)
display.set_backlight(100)

# Touch handling:
i2c_bus = i2c.I2C.Bus(host=I2C_BUS, scl=TP_SCL, sda=TP_SDA, freq=I2C_FREQ, use_locks=False)
touch_dev = i2c.I2C.Device(bus=i2c_bus, dev_id=TP_ADDR, reg_bits=TP_REGBITS)
indev=cst816s.CST816S(touch_dev,startup_rotation=lv.DISPLAY_ROTATION._180) # button in top left, good

th = task_handler.TaskHandler()
display.set_rotation(lv.DISPLAY_ROTATION._90)

# Custom touch interrupt handler:
indev._write_reg(0xEC,0x06)
indev._write_reg(0xFA,0x50)
irq_pin=machine.Pin(46,machine.Pin.IN,machine.Pin.PULL_UP)
# gesture ids:
# 0: press
# 1: swipe from left to USB port
# 2: swipe from USB port to left
# 3: top to bottom
# 4: bottom to top
# 5: release
# 12: long press
def handle_gesture(pin):
    indev._read_reg(0x01)
    gesture_id=indev._rx_buf[0]
    indev._read_reg(0x02)
    finger_num=indev._rx_buf[0]
    indev._read_reg(0x03)
    x_h=indev._rx_buf[0]
    indev._read_reg(0x04)
    x_l=indev._rx_buf[0]
    x=((x_h&0x0F)<<8)|x_l
    indev._read_reg(0x05)
    y_h=indev._rx_buf[0]
    indev._read_reg(0x06)
    y_l=indev._rx_buf[0]
    y=((y_h&0x0F)<<8)|y_l
    #print(f"GestureID={gesture_id},FingerNum={finger_num},X={x},Y={y}")
    if gesture_id==0x04:
        #print("Swipe Up Detected")
        close_drawer()
    elif gesture_id==0x03:
        #print("Swipe Down Detected")
        open_drawer()

irq_pin.irq(trigger=machine.Pin.IRQ_FALLING,handler=handle_gesture)







# GUI:

# Below works at https://sim.lvgl.io/v9.0/micropython/ports/webassembly/index.html

import time

# Constants
TFT_HOR_RES=320
TFT_VER_RES=240
NOTIFICATION_BAR_HEIGHT=24
BUTTON_WIDTH=100
BUTTON_HEIGHT=40
PADDING_TINY=5
PADDING_SMALL=10
PADDING_MEDIUM=20
PADDING_LARGE=30
DRAWER_ANIM_DURATION=300
SLIDER_MIN_VALUE=1
SLIDER_MAX_VALUE=100
SLIDER_DEFAULT_VALUE=80
OFFSET_WIFI_ICON = -60
OFFSET_BATTERY_ICON = -40
TIME_UPDATE_INTERVAL = 1000

# Color palette
DARKPINK = lv.color_hex(0xEC048C)
MEDIUMPINK = lv.color_hex(0xF480C5)
LIGHTPINK = lv.color_hex(0xF9E9F2)
DARKYELLOW = lv.color_hex(0xFBDC05)
LIGHTYELLOW = lv.color_hex(0xFBE499)
PUREBLACK = lv.color_hex(0x000000)

COLOR_DRAWER_BG=MEDIUMPINK
COLOR_TEXT_WHITE=LIGHTPINK
COLOR_NOTIF_BAR_BG = DARKPINK
COLOR_DRAWER_BUTTON_BG=DARKYELLOW
COLOR_DRAWER_BUTTONTEXT=PUREBLACK
COLOR_SLIDER_BG=LIGHTPINK
COLOR_SLIDER_KNOB=DARKYELLOW
COLOR_SLIDER_INDICATOR=LIGHTPINK



drawer=None
wifi_screen=None
drawer_open=False

scr = lv.screen_active()
scr.set_style_bg_color(lv.color_hex(0x000000), 0)

# Create a button (using lv.obj as a base)
btn = lv.button(scr)
btn.set_size(100, 50)
#btn.align(lv.ALIGN.LEFT_MID, 60, 60) doesnt work in web version?

# Add button style
style = lv.style_t()
style.init()
style.set_bg_color(lv.palette_main(lv.PALETTE.BLUE))
style.set_border_width(2)
style.set_border_color(lv.palette_darken(lv.PALETTE.BLUE, 3))
btn.add_style(style, 0)

# Add a label to the button
label = lv.label(btn)
label.set_text("Click Me")
label.center()

# Button event callback
def btn_event_cb(evt):
    if evt.get_code() == lv.EVENT.CLICKED:
        print("Button clicked!")

# Register the event callback
btn.add_event_cb(btn_event_cb, lv.EVENT.CLICKED, None)




# Create a slider
slider = lv.slider(scr)
slider.set_size(200, 20)
slider.set_range(0, 100)
slider.set_value(50, lv.ANIM.OFF)
slider.align(lv.ALIGN.BOTTOM_MID, 0, -40)

slider_label=lv.label(scr)
slider_label.set_text("80%")
slider_label.set_style_text_color(COLOR_TEXT_WHITE,0)
slider_label.align_to(slider,lv.ALIGN.OUT_TOP_MID,0,-5)

def slider_event(e):
    value=slider.get_value()
    print("slider value:")
    print(value)
    slider_label.set_text(f"{value}%")
    #display.set_backlight(value) doesnt do anything and doesnt work in web version

slider.add_event_cb(slider_event,lv.EVENT.VALUE_CHANGED,None)


# Style for the slider background
bg_style = lv.style_t()
bg_style.init()
bg_style.set_bg_color(lv.palette_main(lv.PALETTE.GREY))
bg_style.set_border_width(1)
bg_style.set_border_color(lv.color_make(50, 50, 50))
bg_style.set_radius(10)
slider.add_style(bg_style, lv.PART.MAIN)

# Style for the slider indicator (track)
indic_style = lv.style_t()
indic_style.init()
indic_style.set_bg_color(lv.palette_main(lv.PALETTE.BLUE))
indic_style.set_radius(10)
slider.add_style(indic_style, lv.PART.INDICATOR)

# Style for the slider knob
knob_style = lv.style_t()
knob_style.init()
knob_style.set_bg_color(lv.palette_main(lv.PALETTE.RED))
knob_style.set_border_width(2)
knob_style.set_border_color(lv.color_make(50, 50, 50))
knob_style.set_radius(100)  # Circular knob
knob_style.set_pad_all(5)
slider.add_style(knob_style, lv.PART.KNOB)


#show_block_height()

# Connect to Wi-Fi and fetch block height
#if connect_wifi():
#else:
#    label.set_text("Block Height: Wi-Fi Error")



#print(os.listdir('/')) 
#try:
#    with open('/boot.py', 'r') as file:
#        print("Contents of /boot.py:")
#        print("-" * 20)
#        for line in file:
#            print(line.rstrip())  # Remove trailing newlines for clean output
#except OSError as e:
#    print("Error reading /boot.py:", e)
#with open('/block_height.txt', 'w') as f:
#    f.write('853123')


def create_notification_bar():
    # Create notification bar object
    notification_bar = lv.obj(lv.screen_active())
    notification_bar.set_style_bg_color(COLOR_NOTIF_BAR_BG, 0)
    notification_bar.set_size(320, NOTIFICATION_BAR_HEIGHT)
    notification_bar.set_pos(0, 0)
    notification_bar.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
    notification_bar.set_scroll_dir(lv.DIR.VER)
    notification_bar.set_style_border_width(0, 0)
    notification_bar.set_style_radius(0, 0)
    # Time label
    time_label = lv.label(notification_bar)
    time_label.set_text("12:00")
    time_label.align(lv.ALIGN.LEFT_MID, PADDING_TINY, 0)
    time_label.set_style_text_color(COLOR_TEXT_WHITE, 0)
    # Notification icon (bell)
    notif_icon = lv.label(notification_bar)
    notif_icon.set_text(lv.SYMBOL.BELL)
    notif_icon.align_to(time_label, lv.ALIGN.OUT_RIGHT_MID, PADDING_LARGE, 0)
    notif_icon.set_style_text_color(COLOR_TEXT_WHITE, 0)
    # WiFi icon
    wifi_icon = lv.label(notification_bar)
    wifi_icon.set_text(lv.SYMBOL.WIFI)
    wifi_icon.align(lv.ALIGN.RIGHT_MID, OFFSET_WIFI_ICON, 0)
    wifi_icon.set_style_text_color(COLOR_TEXT_WHITE, 0)
    # Battery icon
    battery_icon = lv.label(notification_bar)
    battery_icon.set_text(lv.SYMBOL.BATTERY_FULL)
    battery_icon.align(lv.ALIGN.RIGHT_MID, OFFSET_BATTERY_ICON, 0)
    battery_icon.set_style_text_color(COLOR_TEXT_WHITE, 0)
    # Battery percentage
    battery_label = lv.label(notification_bar)
    battery_label.set_text("100%")
    battery_label.align(lv.ALIGN.RIGHT_MID, 0, 0)
    battery_label.set_style_text_color(COLOR_TEXT_WHITE, 0)
    openbutton = lv.button(notification_bar)
    openbutton.align(lv.ALIGN.TOP_MID, -20, -8)
    openbutton.add_event_cb(lambda event: open_drawer(), lv.EVENT.CLICKED, None)
    closebutton = lv.button(notification_bar)
    closebutton.align(lv.ALIGN.TOP_MID, 20, -8)
    closebutton.add_event_cb(lambda event: close_drawer(), lv.EVENT.CLICKED, None)
    # Timer to update time every second
    def update_time(timer):
        ticks = time.ticks_ms()
        hours = (ticks // 3600000) % 24
        minutes = (ticks // 60000) % 60
        seconds = (ticks // 1000) % 60
        time_label.set_text(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    lv.timer_create(update_time, TIME_UPDATE_INTERVAL, None)



# Create the notification bar
create_notification_bar()


# Subwindow is created before drawer so that drawer is on top
screen = lv.screen_active()
subwindow = lv.obj(screen)
subwindow.set_size(TFT_HOR_RES, TFT_VER_RES - NOTIFICATION_BAR_HEIGHT)
subwindow.set_pos(0, NOTIFICATION_BAR_HEIGHT)
subwindow.set_style_border_width(0, 0)
subwindow.set_style_pad_all(0, 0)



def create_drawer():
    global drawer,wifi_screen
    drawer=lv.obj(lv.screen_active())
    drawer.set_size(TFT_HOR_RES,TFT_VER_RES-NOTIFICATION_BAR_HEIGHT)
    drawer.set_pos(0,-TFT_VER_RES+NOTIFICATION_BAR_HEIGHT)
    drawer.set_style_bg_color(COLOR_DRAWER_BG,0)
    drawer.set_scroll_dir(lv.DIR.NONE)
    slider=lv.slider(drawer)
    slider.set_range(SLIDER_MIN_VALUE,SLIDER_MAX_VALUE)
    slider.set_value(SLIDER_DEFAULT_VALUE,False)
    slider.set_width(TFT_HOR_RES-PADDING_MEDIUM)
    slider.align(lv.ALIGN.TOP_MID,0,PADDING_SMALL)
    slider.set_style_bg_color(COLOR_SLIDER_BG,lv.PART.MAIN)
    slider.set_style_bg_color(COLOR_SLIDER_INDICATOR,lv.PART.INDICATOR)
    slider.set_style_bg_color(COLOR_SLIDER_KNOB,lv.PART.KNOB)
    slider_label=lv.label(drawer)
    slider_label.set_text("80%")
    slider_label.set_style_text_color(COLOR_TEXT_WHITE,0)
    slider_label.align_to(slider,lv.ALIGN.OUT_TOP_MID,0,-5)
    # works here
    def slider_event(e):
        slider=e.get_target()
        label=e.get_user_data()
        value=slider.get_value()
        label.set_text(f"{value}%")
        display.set_backlight(value)
    # this crashes it: slider.add_event_cb(slider_event,lv.EVENT.VALUE_CHANGED,slider_label)
    # this crashes it: slider.add_event_cb(slider_event,lv.EVENT.VALUE_CHANGED,slider_label)
    wifi_btn=lv.button(drawer)
    wifi_btn.set_size(BUTTON_WIDTH,BUTTON_HEIGHT)
    wifi_btn.align(lv.ALIGN.LEFT_MID,PADDING_SMALL,0)
    wifi_btn.set_style_bg_color(COLOR_DRAWER_BUTTON_BG,0)
    wifi_label=lv.label(wifi_btn)
    wifi_label.set_text(lv.SYMBOL.WIFI+" WiFi")
    wifi_label.center()
    wifi_label.set_style_text_color(COLOR_DRAWER_BUTTONTEXT,0)
    def wifi_event(e):
        global drawer_open
        #wifi_screen.set_y(0) # TODO: make this
        close_drawer()
        drawer_open=False
    wifi_btn.add_event_cb(wifi_event,lv.EVENT.CLICKED,None)
    #
    settings_btn=lv.button(drawer)
    settings_btn.set_size(BUTTON_WIDTH,BUTTON_HEIGHT)
    settings_btn.align(lv.ALIGN.RIGHT_MID,-PADDING_SMALL,0)
    settings_btn.set_style_bg_color(COLOR_DRAWER_BUTTON_BG,0)
    settings_label=lv.label(settings_btn)
    settings_label.set_text(lv.SYMBOL.SETTINGS+" Settings")
    settings_label.center()
    settings_label.set_style_text_color(COLOR_DRAWER_BUTTONTEXT,0)
    def settings_event(e):
        global drawer_open
        close_drawer()
        drawer_open=False
    settings_btn.add_event_cb(settings_event,lv.EVENT.CLICKED,None)
    #
    launcher_btn=lv.button(drawer)
    launcher_btn.set_size(BUTTON_WIDTH,BUTTON_HEIGHT)
    launcher_btn.align(lv.ALIGN.BOTTOM_LEFT,PADDING_SMALL,0)
    launcher_btn.set_style_bg_color(COLOR_DRAWER_BUTTON_BG,0)
    launcher_label=lv.label(launcher_btn)
    launcher_label.set_text(lv.SYMBOL.HOME+" Launcher")
    launcher_label.center()
    launcher_label.set_style_text_color(COLOR_DRAWER_BUTTONTEXT,0)
    def launcher_event(e):
    	print("Launcher button pressed!")
        global drawer_open
        close_drawer()
        drawer_open=False
        run_app(launcher_script,False)
    launcher_btn.add_event_cb(launcher_event,lv.EVENT.CLICKED,None)
    #
    restart_btn=lv.button(drawer)
    restart_btn.set_size(BUTTON_WIDTH,BUTTON_HEIGHT)
    restart_btn.align(lv.ALIGN.BOTTOM_RIGHT,-PADDING_SMALL,0)
    restart_btn.set_style_bg_color(COLOR_DRAWER_BUTTON_BG,0)
    restart_label=lv.label(restart_btn)
    restart_label.set_text(lv.SYMBOL.POWER+" Reset")
    restart_label.center()
    restart_label.set_style_text_color(COLOR_DRAWER_BUTTONTEXT,0)
    def launcher_event(e):
    	print("Reset button pressed!")
        global drawer_open
        close_drawer()
        drawer_open=False
        run_app(launcher_script,False)
    restart_btn.add_event_cb(lambda event: machine.reset(),lv.EVENT.CLICKED,None)

def open_drawer():
    global drawer_open
    if not drawer_open:
        drawer.set_y(NOTIFICATION_BAR_HEIGHT)
        drawer_open=True


def close_drawer():
    global drawer_open
    if drawer_open:
        drawer.set_y(-TFT_VER_RES+NOTIFICATION_BAR_HEIGHT)
        drawer_open=False



create_drawer()







# uasyncio and _thread aren't available on web

import _thread

# Function to execute the child script as a coroutine
def execute_script(script_source, is_file, lvgl_obj, return_to_launcher):
    thread_id = _thread.get_ident();
    print(f"Thread {thread_id}: executing script")
    try:
        script_globals = {
            'lv': lv,
            'subwindow': lvgl_obj,
            'run_app': run_app,
            'app1_script': app1_script,
            'app2_script': app2_script
        }
        if is_file:
            print(f"Thread {thread_id}: reading script from file: {script_source}")
	        with open(script_source, 'r') as f:
                script_source = f.read()
        print(f"Thread {thread_id}: starting script")
        exec(script_source, script_globals)
        print(f"Thread {thread_id}: script finished")
        if return_to_launcher:
        	print(f"Thread {thread_id}: running launcher_script")
        	run_app(launcher_script,False,False)
    except Exception as e:
        print(f"Thread {thread_id}: error ", e)


def run_app(scriptname,is_file,return_to_launcher=True):
	# Start the event loop in a background thread
	gc.collect()
	print("Free memory before starting new script thread:", gc.mem_free())
	try:
    	# 168KB maximum at startup but 136KB after loading display, drivers, LVGL gui etc so let's go for 128KB for now, still a lot...
    	# But then no additional threads can be created. So 32KB seems like a good balance, allowing for 4 threads in apps...
    	subwindow.clean()
    	_thread.stack_size(32768)
    	_thread.start_new_thread(execute_script, (scriptname, False, subwindow, return_to_launcher))
    	print("Event loop started in background thread")
	except Exception as e:
    	print("Error starting event loop thread:", e)


# app1: updates label, adds button and slider
app1_script = """
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
"""

app2_script = """
import time
print("Child coroutine: Creating UI")
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
    label.set_text(f"App2: {count}")
    time.sleep_ms(100) # shorter makes it more responive to the quit button
print("Child coroutine: Exiting")
"""


launcher_script = """
print("Launcher script running")
app1_button = lv.button(subwindow)
app1_button.set_size(120, 40)
app1_button.align(lv.ALIGN.LEFT_MID, 20, 0)
app1_button_label = lv.label(app1_button)
app1_button_label.set_text("Start App 1")
app1_button_label.center()
app1_button.add_event_cb(lambda event: run_app(app1_script,False), lv.EVENT.CLICKED, None)
app2_button = lv.button(subwindow)
app2_button.set_size(120, 40)
app2_button.align(lv.ALIGN.RIGHT_MID, -20, 0)
app2_button_label = lv.label(app2_button)
app2_button_label.set_text("Start App 2")
app2_button_label.center()
app2_button.add_event_cb(lambda event: run_app(app2_script,False), lv.EVENT.CLICKED, None)
print("Launcher script exiting")
"""


run_app(launcher_script,False,False)
