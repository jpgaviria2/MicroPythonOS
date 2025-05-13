appscreen = lv.screen_active()

keepgoing = True
keepliveqrdecoding = False
width = 240
height = 240

# Variable to hold the current memoryview to prevent garbage collection
current_cam_buffer = None


cont = lv.obj(appscreen)
cont.set_style_pad_all(0, 0)
cont.set_style_border_width(0, 0)
cont.set_size(lv.pct(100), lv.pct(100))
cont.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

snap_button = lv.button(cont)
snap_button.set_size(60, 60)
snap_button.align(lv.ALIGN.RIGHT_MID, 0, 0)
snap_label = lv.label(snap_button)
snap_label.set_text(lv.SYMBOL.OK)
snap_label.center()

def snap_button_click(e):
    print("Picture taken!")
    try:
        import os
        os.mkdir("data")
        os.mkdir("data/com.example.camtest")
    except OSError:
        pass
    if current_cam_buffer is not None:
        filename="data/com.example.camtest/capture.raw"
        try:
            with open(filename, 'wb') as f:
                f.write(current_cam_buffer)
            print(f"Successfully wrote current_cam_buffer to {filename}")
        except OSError as e:
            print(f"Error writing to file: {e}")

snap_button.add_event_cb(snap_button_click,lv.EVENT.CLICKED,None)


qr_button = lv.button(cont)
qr_button.set_size(60, 60)
qr_button.align(lv.ALIGN.BOTTOM_RIGHT, 0, 0)
qr_label = lv.label(qr_button)
qr_label.set_text(lv.SYMBOL.EYE_OPEN)
qr_label.center()

def process_qr_buffer(buffer):
    try:
        # Try to decode buffer as a UTF-8 string
        result = buffer.decode('utf-8')
        # Check if the string is printable (ASCII printable characters)
        if all(32 <= ord(c) <= 126 for c in result):
            return result
    except UnicodeDecodeError:
        pass
    # If not a valid string or not printable, convert to hex
    hex_str = ' '.join([f'{b:02x}' for b in buffer])
    return hex_str.lower()

def qrdecode_live():
    # Image dimensions
    buffer_size = width * height  # 240 * 240 = 57600 bytes
    while keepgoing and keepliveqrdecoding:
        try:
            import qrdecode
            result = qrdecode.qrdecode(current_cam_buffer, width, height)
            if result.startswith('\ufeff'): # Remove BOM (\ufeff) from the start of the decoded string, if present
                result = result[1:]
            result = process_qr_buffer(result)
            print(f"QR decoding found: {result}")
        except Exception as e:
            print("QR decode error: ", e)
        time.sleep_ms(500)

def qr_button_click(e):
    global keepliveqrdecoding, qr_label
    if not keepliveqrdecoding:
        print("Activating live QR decoding...")
        keepliveqrdecoding = True
        qr_label.set_text(lv.SYMBOL.EYE_CLOSE)
        try:
            import _thread
            _thread.stack_size(12*1024) # 16KB is too much
            _thread.start_new_thread(qrdecode_live, ())
        except Exception as e:
            print("Could not start live QR decoding thread: ", e)
    else:
        print("Deactivating live QR decoding...")
        keepliveqrdecoding = False
        qr_label.set_text(lv.SYMBOL.EYE_OPEN)

qr_button.add_event_cb(qr_button_click,lv.EVENT.CLICKED,None)


close_button = lv.button(cont)
close_button.set_size(60,60)
close_button.align(lv.ALIGN.TOP_RIGHT, 0, 0)
close_label = lv.label(close_button)
close_label.set_text(lv.SYMBOL.CLOSE)
close_label.center()
def close_button_click(e):
    global keepgoing
    print("Closing camera!")
    keepgoing = False

close_button.add_event_cb(close_button_click,lv.EVENT.CLICKED,None)


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
        "stride": width ,
        #"cf": lv.COLOR_FORMAT.RGB565
        "cf": lv.COLOR_FORMAT.L8
    },
    'data_size': width * height,
    'data': None  # Will be updated per frame
})

# Set initial image source (optional, can be set in try_capture)
image.set_src(image_dsc)


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
while appscreen == lv.screen_active() and keepgoing:
    try_capture()
    time.sleep_ms(100) # Allow for the MicroPython REPL to still work. Reducing it doesn't seem to affect the on-display FPS.

print("App backgrounded, deinitializing camera...")
cam.deinit()

show_launcher()
