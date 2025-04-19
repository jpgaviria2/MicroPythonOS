import lvgl as lv
import time
from machine import Pin, SPI
import st7789 
import lcd_bus
from micropython import const
import machine
import task_handler  # NOQA
import cst816s  # NOQA
import i2c  # NOQA
import network
import urequests

# Pin configuration
LCD_SCLK = 39
LCD_MOSI = 38
LCD_MISO = 40
LCD_DC = 42
LCD_CS = 45
LCD_BL = 1
TP_SDA = 48
TP_SCL = 47

TFT_HOR_RES=320
TFT_VER_RES=240

NOTIFICATION_BAR_HEIGHT=24
BUTTON_WIDTH=100
BUTTON_HEIGHT=40
PADDING_TINY=5
PADDING_SMALL=10
PADDING_MEDIUM=20
DRAWER_BUTTON_Y_OFFSET=60
DRAWER_ANIM_DURATION=300
SLIDER_MIN_VALUE=1
SLIDER_MAX_VALUE=100
SLIDER_DEFAULT_VALUE=80

DARKPINK=lv.color_hex(0xEC048C)
MEDIUMPINK=lv.color_hex(0xF480C5)
LIGHTPINK=lv.color_hex(0xF9E9F2)
DARKYELLOW=lv.color_hex(0xFBDC05)
PUREBLACK=lv.color_hex(0x000000)
COLOR_DRAWER_BG=MEDIUMPINK
COLOR_TEXT_WHITE=LIGHTPINK
COLOR_DRAWER_BUTTON_BG=DARKYELLOW
COLOR_DRAWER_BUTTONTEXT=PUREBLACK
COLOR_SLIDER_BG=LIGHTPINK
COLOR_SLIDER_KNOB=DARKYELLOW
COLOR_SLIDER_INDICATOR=LIGHTPINK

drawer=None
wifi_screen=None
drawer_open=False

lv.init()
spi_bus = machine.SPI.Bus(
    host=2,
    mosi=38,
    miso=40,
    sck=39
)
display_bus = lcd_bus.SPIBus(
    spi_bus=spi_bus,
    freq=40000000,
    dc=42,
    cs=45,
)
display = st7789.ST7789(
    data_bus=display_bus,
    display_width=240,
    display_height=320,
    backlight_pin=1,
    color_space=lv.COLOR_FORMAT.RGB565,
    color_byte_order=st7789.BYTE_ORDER_BGR,
    rgb565_byte_swap=True,
)
display.init()
display.set_power(True)
display.set_backlight(100)

i2c_bus = i2c.I2C.Bus(host=0, scl=47, sda=48, freq=100000, use_locks=False)
touch_dev = i2c.I2C.Device(bus=i2c_bus, dev_id=0x15, reg_bits=8)
indev=cst816s.CST816S(touch_dev,startup_rotation=lv.DISPLAY_ROTATION._180) # button in top left, good

th = task_handler.TaskHandler()
display.set_rotation(lv.DISPLAY_ROTATION._90)









import lvgl as lv
import uasyncio as asyncio
import utime
import gc

# Create a subwindow for the child script (half the 320x240 display)
screen = lv.screen_active()
subwindow = lv.obj(screen)
subwindow.set_size(160, 240)  # Half width, full height
subwindow.align(lv.ALIGN.LEFT_MID, 0, 0)  # Left side
subwindow.set_style_bg_color(lv.color_hex(0xDDDDDD), lv.PART.MAIN)

# Create a label for parent updates
parent_label = lv.label(screen)
parent_label.set_text("Parent: 0")
parent_label.set_style_text_font(lv.font_montserrat_12, 0)
parent_label.align(lv.ALIGN.TOP_RIGHT, -10, 10)

# Create a parent button
parent_button = lv.button(screen)
parent_button.set_size(80, 40)
parent_button.align(lv.ALIGN.BOTTOM_RIGHT, -10, -50)
parent_button_label = lv.label(parent_button)
parent_button_label.set_text("Parent Btn")
parent_button_label.set_style_text_font(lv.font_montserrat_12, 0)

# Create a parent slider
parent_slider = lv.slider(screen)
parent_slider.set_size(100, 10)
parent_slider.set_range(0, 100)
parent_slider.align(lv.ALIGN.BOTTOM_RIGHT, -10, -10)

# Parent button callback
def parent_button_cb(e):
    print("Parent button clicked")

parent_button.add_event_cb(parent_button_cb, lv.EVENT.CLICKED, None)

# Parent slider callback
def parent_slider_cb(e):
    value = parent_slider.get_value()
    print("Parent slider value:", value)

parent_slider.add_event_cb(parent_slider_cb, lv.EVENT.VALUE_CHANGED, None)

# Function to execute the child script as a coroutine
async def execute_script(script_source, lvgl_obj):
    try:
        script_globals = {
            'lv': lv,
            'subwindow': lvgl_obj,
            'asyncio': asyncio,
            'utime': utime
        }
        print("Child script: Compiling")
        code = compile(script_source, "<string>", "exec")
        exec(code, script_globals)
        update_child = script_globals.get('update_child')
        if update_child:
            print("Child script: Starting update_child")
            await update_child()
        else:
            print("Child script error: No update_child function defined")
    except Exception as e:
        print("Child script error:", e)

# Child script buffer: updates label, adds button and slider
script_buffer = """
import asyncio
async def update_child():
    print("Child coroutine: Creating UI")
    # Label
    label = lv.label(subwindow)
    label.set_text("Child: 0")
    label.set_style_text_font(lv.font_montserrat_12, 0)
    label.align(lv.ALIGN.TOP_MID, 0, 10)
    # Button
    button = lv.button(subwindow)
    button.set_size(80, 40)
    button.align(lv.ALIGN.BOTTOM_MID, 0, -50)
    button_label = lv.label(button)
    button_label.set_text("Child Btn")
    button_label.set_style_text_font(lv.font_montserrat_12, 0)
    # Slider
    slider = lv.slider(subwindow)
    slider.set_size(100, 10)
    slider.set_range(0, 100)
    slider.align(lv.ALIGN.BOTTOM_MID, 0, -10)
    # Button callback
    def button_cb(e):
        print("Child button clicked")
    button.add_event_cb(button_cb, lv.EVENT.CLICKED, None)
    # Slider callback
    def slider_cb(e):
        value = slider.get_value()
        print("Child slider value:", value)
    slider.add_event_cb(slider_cb, lv.EVENT.VALUE_CHANGED, None)
    # Update loop
    count = 0
    while True:
        count += 1
        print("Child coroutine: Updating label to", count)
        label.set_text(f"Child: {count}")
        await asyncio.sleep_ms(2000)  # Update every 2s
"""

# Parent coroutine: updates parent label every 1 second
async def update_parent():
    count = 0
    while True:
        count += 1
        print("Parent coroutine: Updating label to", count)
        parent_label.set_text(f"Parent: {count}")
        gc.collect()
        print("Parent coroutine: Free memory:", gc.mem_free())
        await asyncio.sleep_ms(1000)  # Update every 1s

# Main async function to run all tasks
async def main():
    print("Main: Starting tasks")
    asyncio.create_task(update_parent())
    asyncio.create_task(execute_script(script_buffer, subwindow))
    while True:
        await asyncio.sleep_ms(100)

# Run the event loop
gc.collect()
print("Free memory before loop:", gc.mem_free())
try:
    asyncio.run(main())
except Exception as e:
    print("Main error:", e)














# Fetch Bitcoin block height from mempool.space
def get_block_height():
    try:
        response = urequests.get("https://mempool.space/api/blocks/tip/height")
        if response.status_code == 200:
            height = response.text.strip()  # Returns plain text (e.g., "853123")
            response.close()
            return height
        else:
            response.close()
            return "Error: HTTP " + str(response.status_code)
    except Exception as e:
        return "Error: " + str(e)

def show_block_height():
	# Create a label for block height
	label = lv.label(scr)
	label.set_text("Bitcoin Block Height: Fetching...")
	label.set_style_text_color(lv.color_make(0, 255, 0), 0)  # Green text
	label.set_style_text_font(lv.font_montserrat_16, 0)  # Larger font (if available)
	label.align(lv.ALIGN.TOP_LEFT, 10, 200)
	#label.center()
	
	# Style for label background
	style = lv.style_t()
	style.init()
	style.set_bg_color(lv.palette_main(lv.PALETTE.DARK))  # Dark background
	style.set_border_width(2)
	style.set_border_color(lv.color_make(255, 255, 255))  # White border
	style.set_pad_all(10)
	style.set_radius(10)
	label.add_style(style, 0)
	
	height = get_block_height()
	label.set_text(f"Block Height: {height}")
	

# Connect to Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect("SSIDHERE", "PASSWORDHERE")
    print("Connecting to Wi-Fi...", end="")
    for _ in range(30):  # Wait up to 30 seconds
        if wlan.isconnected():
            print(" Connected!")
            print("IP:", wlan.ifconfig()[0])
            return True
        time.sleep(1)
        print(".", end="")
    print(" Failed to connect!")
    return False

scr = lv.screen_active()
scr.set_style_bg_color(lv.color_hex(0x000000), 0)

# Create a button (using lv.obj as a base)
btn = lv.button(scr)
btn.set_size(100, 50)
btn.align(lv.ALIGN.LEFT, 60, 60)

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
    display.set_backlight(value)

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



print(os.listdir('/')) 

try:
    with open('/boot.py', 'r') as file:
        print("Contents of /boot.py:")
        print("-" * 20)
        for line in file:
            print(line.rstrip())  # Remove trailing newlines for clean output
except OSError as e:
    print("Error reading /boot.py:", e)

#with open('/block_height.txt', 'w') as f:
#    f.write('853123')


# Color palette
DARKPINK = lv.color_hex(0xEC048C)
MEDIUMPINK = lv.color_hex(0xF480C5)
LIGHTPINK = lv.color_hex(0xF9E9F2)
DARKYELLOW = lv.color_hex(0xFBDC05)
LIGHTYELLOW = lv.color_hex(0xFBE499)
PUREBLACK = lv.color_hex(0x000000)

COLOR_NOTIF_BAR_BG = DARKPINK
COLOR_TEXT_WHITE = LIGHTPINK

# Constants
NOTIFICATION_BAR_HEIGHT = 40
PADDING_TINY = 5
PADDING_SMALL = 10
OFFSET_WIFI_ICON = -40
OFFSET_BATTERY_ICON = -20
TIME_UPDATE_INTERVAL = 1000

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
    notif_icon.align_to(time_label, lv.ALIGN.OUT_RIGHT_MID, PADDING_SMALL, 0)
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
    # Timer to update time every second
    def update_time(timer):
        ticks = time.ticks_ms()
        hours = (ticks // 3600000) % 24
        minutes = (ticks // 60000) % 60
        time_label.set_text(f"{hours:02d}:{minutes:02d}")
    lv.timer_create(update_time, TIME_UPDATE_INTERVAL, None)



# Create the notification bar
create_notification_bar()



indev._write_reg(0xEC,0x06)
indev._write_reg(0xFA,0x50)
irq_pin=machine.Pin(46,machine.Pin.IN,machine.Pin.PULL_UP)

# gesture id:
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
    print(f"GestureID={gesture_id},FingerNum={finger_num},X={x},Y={y}")
    if gesture_id==0x04:
        print("Swipe Up Detected")
        close_drawer()
    elif gesture_id==0x03:
        print("Swipe Down Detected")
        open_drawer()



def create_drawer():
    print('-1')
    global drawer,wifi_screen
    print('0')
    drawer=lv.obj(lv.screen_active())
    print('1')
    drawer.set_size(TFT_HOR_RES,TFT_VER_RES-NOTIFICATION_BAR_HEIGHT)
    print('2')
    drawer.set_pos(0,-TFT_VER_RES+NOTIFICATION_BAR_HEIGHT)
    print('3')
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
    print('4')
    slider_label=lv.label(drawer)
    slider_label.set_text("80%")
    slider_label.set_style_text_color(COLOR_TEXT_WHITE,0)
    slider_label.align_to(slider,lv.ALIGN.OUT_TOP_MID,0,-5)
    print('5')
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
    wifi_btn.align(lv.ALIGN.TOP_LEFT,PADDING_SMALL,DRAWER_BUTTON_Y_OFFSET)
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
    settings_btn=lv.button(drawer)
    settings_btn.set_size(BUTTON_WIDTH,BUTTON_HEIGHT)
    settings_btn.align(lv.ALIGN.TOP_RIGHT,-PADDING_SMALL,DRAWER_BUTTON_Y_OFFSET)
    settings_btn.set_style_bg_color(COLOR_DRAWER_BUTTON_BG,0)
    settings_label=lv.label(settings_btn)
    settings_label.set_text(lv.SYMBOL.SETTINGS+" Settings")
    settings_label.center()
    settings_label.set_style_text_color(COLOR_DRAWER_BUTTONTEXT,0)
    print('40')
    def settings_event(e):
        global drawer_open
        close_drawer()
        drawer_open=False
    settings_btn.add_event_cb(settings_event,lv.EVENT.CLICKED,None)

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


irq_pin.irq(trigger=machine.Pin.IRQ_FALLING,handler=handle_gesture)

create_drawer()
