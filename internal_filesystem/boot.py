from machine import Pin, SPI
import st7789 
import lcd_bus
import machine
import cst816s
import i2c

import lvgl as lv
import task_handler

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
    backlight_on_state=st7789.STATE_PWM,
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

lv.init()
display.set_rotation(lv.DISPLAY_ROTATION._90)

# Gesture IDs:
# 0: press
# 1: swipe from left to USB port
# 2: swipe from USB port to left
# 3: top to bottom
# 4: bottom to top
# 5: release
# 12: long press

start_y = None # Variable to store the starting Y-coordinate of a touch
def handle_gesture(pin):
    global start_y  # Access the global start_y variable
    indev._read_reg(0x01)
    gesture_id = indev._rx_buf[0]
    indev._read_reg(0x02)
    finger_num = indev._rx_buf[0]
    indev._read_reg(0x03)
    x_h = indev._rx_buf[0]
    indev._read_reg(0x04)
    x_l = indev._rx_buf[0]
    x = ((x_h & 0x0F) << 8) | x_l
    indev._read_reg(0x05)
    y_h = indev._rx_buf[0]
    indev._read_reg(0x06)
    y_l = indev._rx_buf[0]
    y = ((y_h & 0x0F) << 8) | y_l
    #print(f"GestureID={gesture_id},FingerNum={finger_num},X={x},Y={y}")
    temp = y
    y = TFT_VER_RES - x
    #x = TFT_HOR_RES - temp
    x = temp
    #print(f"Corrected GestureID={gesture_id},FingerNum={finger_num},X={x},Y={y}")
    if gesture_id == 0x00 and start_y is None:  # Press (touch start)
        # Store the starting Y-coordinate
        start_y = y
        #print(f"Touch started at Y={start_y}")
    elif gesture_id == 0x04 and drawer_open:  # Swipe up
        # print("Swipe Up Detected")
        close_drawer()
        start_y = None  # Clear start_y after gesture
    elif gesture_id == 0x03:  # Swipe down
        if start_y is not None and start_y <= NOTIFICATION_BAR_HEIGHT:
            # print("Swipe Down Detected from Notification Bar")
            open_drawer()
        start_y = None  # Clear start_y after gesture
    elif gesture_id == 0x05:  # Release
        start_y = None  # Clear start_y on release

indev._write_reg(0xEC,0x06)
indev._write_reg(0xFA,0x50)
irq_pin=machine.Pin(46,machine.Pin.IN,machine.Pin.PULL_UP)
irq_pin.irq(trigger=machine.Pin.IRQ_FALLING, handler=handle_gesture)

print("boot.py finished")
