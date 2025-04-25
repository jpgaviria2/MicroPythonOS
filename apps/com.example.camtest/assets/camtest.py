#define PWDN_GPIO_NUM 17  //power down is not used
#define RESET_GPIO_NUM -1 //software reset will be performed
#define XCLK_GPIO_NUM 8
#define SIOD_GPIO_NUM 21
#define SIOC_GPIO_NUM 16

#define Y9_GPIO_NUM 2
#define Y8_GPIO_NUM 7
#define Y7_GPIO_NUM 10
#define Y6_GPIO_NUM 14
#define Y5_GPIO_NUM 11
#define Y4_GPIO_NUM 15
#define Y3_GPIO_NUM 13
#define Y2_GPIO_NUM 12
#define VSYNC_GPIO_NUM 6
#define HREF_GPIO_NUM 4
#define PCLK_GPIO_NUM 9

#define CAM_LEDC_TIMER      LEDC_TIMER_1
#define CAM_LEDC_CHANNEL    LEDC_CHANNEL_0


# OV5640 I2C address
#sensor_addr = 0x3C
#reg_addr = 0x4300
#reg_value = 0x6F  # RGB565 (bit[6]=1) + sequence 0xF (bits[3:0]=0xF)
#from machine import I2C, Pin
#i2c = I2C(scl=Pin(16), sda=Pin(21))
#i2c.readfrom_mem(0x3C, 0x4300, 1)
#i2c.writeto_mem(sensor_addr, reg_addr, bytes([reg_value]))


subwindow.clean()
canary = lv.obj(subwindow)
canary.add_flag(lv.obj.FLAG.HIDDEN)

#width = 480
#height = 320
#width = 320
#height = 240
#width = 120
#height = 160

width = 240
height = 240

cont = lv.obj(subwindow)
cont.set_style_pad_all(0, 0)
cont.set_style_border_width(0, 0)
cont.set_size(lv.pct(100), lv.pct(100))
cont.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

image = lv.image(cont)
image.align(lv.ALIGN.LEFT_MID, 0, 0)
#image.set_size(width, height)
#image.set_size(height, width)
image.set_rotation(900)


from camera import Camera, GrabMode, PixelFormat, FrameSize, GainCeiling

cam = Camera(
    data_pins=[12,13,15,11,14,10,7,2],
    vsync_pin=6,
    href_pin=4,
    sda_pin=21,
    scl_pin=16,
    pclk_pin=9,
    xclk_pin=8,
    xclk_freq=20000000,
    powerdown_pin=-1,
    reset_pin=-1,
    pixel_format=PixelFormat.RGB565,
    frame_size=FrameSize.R240X240,
    grab_mode=GrabMode.LATEST 
)
#cam.init() automatically done when creating the Camera()

#cam.reconfigure(frame_size=FrameSize.HVGA)
#frame_size=FrameSize.HVGA, # 480x320
#frame_size=FrameSize.QVGA, # 320x240
#frame_size=FrameSize.QQVGA # 160x120

cam.set_vflip(True)

def try_capture():
    if cam.frame_available():
        img = bytes(cam.capture())
        cam.free_buffer()
        # Swap bytes for each 16-bit pixel
        # This is no longer needed because the esp-camera driver does {FORMAT_CTRL00, 0x6F}, // RGB565 (RGB) instead of {FORMAT_CTRL00, 0x61}, // RGB565 (BGR) now
        #img_swapped = bytearray(len(img))
        #for i in range(0, len(img), 2):
        #    img_swapped[i] = img[i+1]    # Swap high and low bytes
        #    img_swapped[i+1] = img[i]
        image_dsc = lv.image_dsc_t({
            "header": { "magic": lv.IMAGE_HEADER_MAGIC, "w": width, "h": height, "stride": width * 2, "cf": lv.COLOR_FORMAT.RGB565 },
            'data_size': len(img),
            'data': img
        })
        image.set_src(image_dsc)

try_capture()

import time

try:
    while canary.is_valid():
        try_capture()
        time.sleep_ms(100) # Allow for the MicroPython REPL to still work
except lv.LvReferenceError: # triggers when the canary dies
    print("Canary died, deinitializing camera...")
    cam.deinit()

