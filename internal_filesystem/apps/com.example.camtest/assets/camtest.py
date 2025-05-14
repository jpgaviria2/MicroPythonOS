import time

appscreen = lv.screen_active()
th.disable()

keepgoing = True
keepliveqrdecoding = False
width = 240
height = 240

# Variable to hold the current memoryview to prevent garbage collection
current_cam_buffer = None
image_dsc = None
image = None
qr_label = None
use_webcam = False

memview = None

def print_qr_buffer(buffer):
    try:
        # Try to decode buffer as a UTF-8 string
        result = buffer.decode('utf-8')
        # Check if the string is printable (ASCII printable characters)
        if all(32 <= ord(c) <= 126 for c in result):
            return result
    except Exception as e:
        pass
    # If not a valid string or not printable, convert to hex
    hex_str = ' '.join([f'{b:02x}' for b in buffer])
    return hex_str.lower()

# Byte-Order-Mark is added sometimes
def remove_bom(buffer):
    bom = b'\xEF\xBB\xBF'
    if buffer.startswith(bom):
        return buffer[3:]
    return buffer

def qrdecode_live():
    # Image dimensions
    buffer_size = width * height  # 240 * 240 = 57600 bytes
    while keepgoing and keepliveqrdecoding:
        try:
            import qrdecode
            result = qrdecode.qrdecode(current_cam_buffer, width, height)
            result = remove_bom(result)
            result = print_qr_buffer(result)
            print(f"QR decoding found: {result}")
        except Exception as e:
            print("QR decode error: ", e)
        time.sleep_ms(500)


def close_button_click(e):
    global keepgoing
    print("Close button clicked")
    keepgoing = False


def snap_button_click(e):
    print("Picture taken!")
    import os
    try:
        os.mkdir("data")
    except OSError:
        pass
    try:
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

def try_capture():
    global current_cam_buffer, image_dsc, image, use_webcam
    if use_webcam:
        current_cam_buffer = webcam.capture_frame(cam, "rgb565")
    elif cam.frame_available():
        current_cam_buffer = cam.capture()  # Returns memoryview
    if current_cam_buffer and len(current_cam_buffer):
        image_dsc.data = current_cam_buffer
        #image.invalidate() # does not work so do this:
        image.set_src(image_dsc)
        if not use_webcam:
            cam.free_buffer()  # Free the old buffer
    else:
        print("No image received from camera, ignoring...")
        return


def build_ui():
    global image, image_dsc,qr_label, cam
    cont = lv.obj(appscreen)
    cont.set_style_pad_all(0, 0)
    cont.set_style_border_width(0, 0)
    cont.set_size(lv.pct(100), lv.pct(100))
    cont.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)    
    close_button = lv.button(cont)
    close_button.set_size(60,60)
    close_button.align(lv.ALIGN.TOP_RIGHT, 0, 0)
    close_label = lv.label(close_button)
    close_label.set_text(lv.SYMBOL.CLOSE)
    close_label.center()
    close_button.add_event_cb(close_button_click,lv.EVENT.CLICKED,None)
    snap_button = lv.button(cont)
    snap_button.set_size(60, 60)
    snap_button.align(lv.ALIGN.RIGHT_MID, 0, 0)
    snap_label = lv.label(snap_button)
    snap_label.set_text(lv.SYMBOL.OK)
    snap_label.center()        
    snap_button.add_event_cb(snap_button_click,lv.EVENT.CLICKED,None)        
    qr_button = lv.button(cont)
    qr_button.set_size(60, 60)
    qr_button.align(lv.ALIGN.BOTTOM_RIGHT, 0, 0)
    qr_label = lv.label(qr_button)
    qr_label.set_text(lv.SYMBOL.EYE_OPEN)
    qr_label.center()
    qr_button.add_event_cb(qr_button_click,lv.EVENT.CLICKED,None)
    # Initialize LVGL image widget
    image = lv.image(cont)
    image.align(lv.ALIGN.LEFT_MID, 0, 0)
    if not use_webcam:
        image.set_rotation(900)
    # Create image descriptor once
    image_dsc = lv.image_dsc_t({
        "header": {
            "magic": lv.IMAGE_HEADER_MAGIC,
            "w": width,
            "h": height,
            "stride": width * 2,
            "cf": lv.COLOR_FORMAT.RGB565
            #"cf": lv.COLOR_FORMAT.L8
        },
        'data_size': width * height * 2,
        'data': None # Will be updated per frame
    })
    image.set_src(image_dsc)


def init_cam():
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
            pixel_format=PixelFormat.RGB565,
            #pixel_format=PixelFormat.GRAYSCALE,
            frame_size=FrameSize.R240X240,
            grab_mode=GrabMode.LATEST 
        )
        #cam.init() automatically done when creating the Camera()
        #cam.reconfigure(frame_size=FrameSize.HVGA)
        #frame_size=FrameSize.HVGA, # 480x320
        #frame_size=FrameSize.QVGA, # 320x240
        #frame_size=FrameSize.QQVGA # 160x120
        cam.set_vflip(True)
        return cam
    except Exception as e:
        print(f"init_cam exception: {e}")
        return None






cam = init_cam()
if not cam:
    print("camtest.py: no internal camera found, trying webcam on /dev/video0")
    try:
        import webcam
        cam = webcam.init("/dev/video0")  # Initialize webcam with device path
        use_webcam = True
    except Exception as e:
        print(f"camtest.py: webcam exception: {e}")

if cam:
    build_ui()
    count=0
    while appscreen == lv.screen_active() and keepgoing is True:
        try_capture()
        # Task handler needs to be updated from the same thread, otherwise it causes concurrency issues:
        lv.task_handler()
        time.sleep_ms(1)
        lv.tick_inc(1)
    print("camtest.py: stopping...")
    if use_webcam:
        webcam.deinit(cam)  # Deinitializes webcam
    else:
        cam.deinit()
else:
   print("No camera found, exiting...")

th.enable()
show_launcher()


