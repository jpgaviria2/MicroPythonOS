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



#subwindow.clean()
#canary = lv.obj(subwindow)
#canary.add_flag(lv.obj.FLAG.HIDDEN)

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


# Initialize LVGL image widget
image = lv.image(cont)
image.align(lv.ALIGN.LEFT_MID, 0, 0)
image.set_rotation(900)

# Create image descriptor once
image_dsc = lv.image_dsc_t({
    "header": {
        "magic": lv.IMAGE_HEADER_MAGIC,
        "w": width,
        "h": height,
        "stride": width * 2,
        "cf": lv.COLOR_FORMAT.RGB565
    },
    'data_size': width * height * 2,
    'data': None  # Will be updated per frame
})

# Set initial image source (optional, can be set in try_capture)
image.set_src(image_dsc)

# Variable to hold the current memoryview to prevent garbage collection
current_cam_buffer = None

def try_capture():
    global current_cam_buffer
    if cam.frame_available():
        # Get new memoryview from camera
        new_cam_buffer = cam.capture()  # Returns memoryview
        # Verify buffer size
        #if len(new_cam_buffer) != width * height * 2:
        #    print("Invalid buffer size:", len(new_cam_buffer))
        #    cam.free_buffer()
        #    return
        # Update image descriptor with new memoryview
        image_dsc.data = new_cam_buffer
        # Set image source to update LVGL (implicitly invalidates widget)
        image.set_src(image_dsc)
        #image.invalidate() #does not work
        # Free the previous buffer (if any) after setting new data
        if current_cam_buffer is not None:
            cam.free_buffer()  # Free the old buffer
        current_cam_buffer = new_cam_buffer  # Store new buffer reference

# Initial capture
try_capture()


import time
while appscreen == lv.screen_active():
    try_capture()
    time.sleep_ms(100) # Allow for the MicroPython REPL to still work

print("App backgrounded, deinitializing camera...")
cam.deinit()
