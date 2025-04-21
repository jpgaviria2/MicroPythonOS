from machine import Pin, SPI
import st7789 
import lcd_bus
import machine
import cst816s
import i2c
import urequests

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

#lv.init() # not needed
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

task_handler.TaskHandler()
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

print("boot.py finished")
