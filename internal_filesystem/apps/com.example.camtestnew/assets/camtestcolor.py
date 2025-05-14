# This works with copy-paste
# It also works like this:
# import mpos
# mpos.apps.execute_script("apps/com.example.camtestnew/assets/camtestnew.py", True, False, True)
# import mpos
# mpos.apps.execute_script_new_thread("apps/com.example.camtestnew/assets/camtestnew.py", True, False, True)


width=240
height=240

import time

#th.disable()


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
    #pixel_format=PixelFormat.RAW, # fails
    #pixel_format=PixelFormat.RGB888, fails
    pixel_format=PixelFormat.RGB565,
    #pixel_format=PixelFormat.GRAYSCALE,
    #pixel_format=PixelFormat.YUV420,
    #pixel_format=PixelFormat.YUV422, # works
    frame_size=FrameSize.R240X240,
    grab_mode=GrabMode.LATEST 
)



image = lv.image(lv.screen_active())
image.align(lv.ALIGN.LEFT_MID, 0, 0)
#image.set_rotation(900)

# Create image descriptor once
image_dsc = lv.image_dsc_t({
    "header": {
        "magic": lv.IMAGE_HEADER_MAGIC,
        "w": width,
        "h": height,
        "stride": width *2,
        #"cf": lv.COLOR_FORMAT.L8 # works
        "cf": lv.COLOR_FORMAT.RGB565 # works
        #"cf": lv.COLOR_FORMAT.I422 #doesnt show anything
        #"cf": lv.COLOR_FORMAT.I420 #doesnt show anything
        #"cf": lv.COLOR_FORMAT.I420
        #"cf": lv.COLOR_FORMAT.YUY2
        #"cf": lv.COLOR_FORMAT.UYVY
        #"cf": lv.COLOR_FORMAT.NV12
    },
    'data_size': width * height * 2 ,
    #'data_size': 86400,
    'data': None # Will be updated per frame
})
image.set_src(image_dsc)



for i in range(100):
    print(f"iteration {i}")
    image_dsc.data = cam.capture()  # Returns memoryview
    image.set_src(image_dsc)
    #image.invalidate()
    #lv.task_handler()
    time.sleep_ms(5) # seems to need more than 0 or 1 ms, otherwise there's almost never a new image...
    #lv.tick_inc(5)


print("cleanup")
cam.deinit()


#th.enable()
