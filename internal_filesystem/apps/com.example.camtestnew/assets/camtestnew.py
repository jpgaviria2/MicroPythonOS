# This works with copy-paste
# It also works like this:
# import mpos
# mpos.apps.execute_script("apps/com.example.camtestnew/assets/camtestnew.py", True, False, True)
# import mpos
# mpos.apps.execute_script_new_thread("apps/com.example.camtestnew/assets/camtestnew.py", True, False, True)


width=240
height=240

import webcam
import time

th.disable()

cam = webcam.init("/dev/video0")  # Initialize webcam with device path
memview = webcam.capture_frame(cam)  # Returns memoryview
#time.sleep_ms(1000)
#static_bytes_obj = bytes(memview)


image = lv.image(lv.screen_active())
image.align(lv.ALIGN.LEFT_MID, 0, 0)
image.set_rotation(900)
# Create image descriptor once
image_dsc = lv.image_dsc_t({
    "header": {
        "magic": lv.IMAGE_HEADER_MAGIC,
        "w": width,
        "h": height,
        "stride": width ,
        "cf": lv.COLOR_FORMAT.L8
    },
    'data_size': width * height,
    'data': memview # Will be updated per frame
})
image.set_src(image_dsc)

for i in range(600):
    #print(f"iteration {i}")
    webcam.recapture_frame(cam) #refresh memview
    #bytes_obj = bytes(memview)
    #print(f"got bytes: {len(bytes_obj)}")
    #image_dsc.data = static_bytes_obj
    #image_dsc.data = bytes_obj
    #image.set_src(image_dsc)
    image.invalidate()
    lv.task_handler()
    time.sleep_ms(5) # seems to need more than 0 or 1 ms, otherwise there's almost never a new image...
    lv.tick_inc(5)

print("cleanup")
webcam.deinit(cam)  # Deinitializes webcam


th.enable()
