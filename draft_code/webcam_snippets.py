try:
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
        #pixel_format=PixelFormat.RGB565,
        pixel_format=PixelFormat.GRAYSCALE,
        frame_size=FrameSize.R240X240,
        grab_mode=GrabMode.LATEST 
    )
    print("it worked!")
except Exception as e:
    print(f"Exception: {e}")



images=300

import webcam
import time


class Webcam:
    def __init__(self):
        # webcam.init() returns (obj, capture_grayscale, deinit)
        self.obj, self._capture_grayscale, self._deinit = webcam.init()
    def capture_grayscale(self):
        return self._capture_grayscale(self.obj)
    def deinit(self):
        return self._deinit(self.obj)

starttime = time.ticks_ms()

# Usage
cam = Webcam()
for _ in range(images):
    buf = cam.capture_grayscale()
    print(len(buf))  # Should print 57600 (240 * 240)

endtime = time.ticks_ms()

print(f"duration: {endtime-starttime}ms")


cam.deinit()














#from webcam import Webcam, init, capture_frame, deinit
import webcam

cam = webcam.init("/dev/video0")  # Initialize webcam with device path
for i in range(1000):
    buf = webcam.capture_frame(cam)  # Captures frame, returns 240x240 grayscale buffer
    print(f"buffer {i} has length {len(buf)}")  # Prints 57600
webcam.deinit(cam)  # Deinitializes webcam


