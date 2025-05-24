# This code grabs images from the camera in RGB565 format (2 bytes per pixel)
# and sends that to the QR decoder if QR decoding is enabled.
# The QR decoder then converts the RGB565 to grayscale, as that's what quirc operates on.
# It would be slightly more efficient to capture the images from the camera in L8/grayscale format,
# or in YUV format and discarding the U and V planes, but then the image will be gray (not great UX)
# and the performance impact of converting RGB565 to grayscale is probably minimal anyway.

import time

import mpos.apps
import mpos.ui

# screens:
main_screen = None

keepliveqrdecoding = False
width = 240
height = 240

# Variable to hold the current memoryview to prevent garbage collection
current_cam_buffer = None
image_dsc = None
image = None
qr_label = None

use_webcam = False
qr_button = None
snap_button = None

status_label = None
status_label_cont = None
status_label_text = "No camera found."
status_label_text_searching = "Searching QR codes..."
status_label_text_found = "Decoding QR..."

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

def qrdecode_one():
    global status_label, status_label_text
    try:
        import qrdecode
        result = qrdecode.qrdecode_rgb565(current_cam_buffer, width, height)
        if not result:
            status_label.set_text(status_label_text_searching)
        else:
            result = remove_bom(result)
            result = print_qr_buffer(result)
            print(f"QR decoding found: {result}")
            status_label.set_text(result)
            stop_qr_decoding()
    except ValueError as e:
        print("QR ValueError: ", e)
        status_label.set_text(status_label_text_searching)
    except TypeError as e:
        print("QR TypeError: ", e)
        status_label.set_text(status_label_text_found)
    except Exception as e:
        print("QR got other error: ", e)


def close_button_click(e):
    print("Close button clicked")
    mpos.ui.back_screen()


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


def start_qr_decoding():
    global qr_label, keepliveqrdecoding, status_label_cont, status_label
    print("Activating live QR decoding...")
    keepliveqrdecoding = True
    qr_label.set_text(lv.SYMBOL.EYE_CLOSE)
    status_label_cont.remove_flag(lv.obj.FLAG.HIDDEN)
    status_label.set_text(status_label_text_searching)

def stop_qr_decoding():
    global qr_label, keepliveqrdecoding
    print("Deactivating live QR decoding...")
    keepliveqrdecoding = False
    qr_label.set_text(lv.SYMBOL.EYE_OPEN)
    status_label_text = status_label.get_text()
    if status_label_text == status_label_text_searching or status_label_text == status_label_text_found: # if it found a QR code, then leave it
        status_label_cont.add_flag(lv.obj.FLAG.HIDDEN)


def qr_button_click(e):
    global keepliveqrdecoding
    if not keepliveqrdecoding:
        start_qr_decoding()
    else:
        stop_qr_decoding()

def try_capture(event):
    #print("capturing camera frame")
    global current_cam_buffer, image_dsc, image, use_webcam
    try:
        if use_webcam:
            current_cam_buffer = webcam.capture_frame(cam, "rgb565")
        elif cam.frame_available():
            current_cam_buffer = cam.capture()
        if current_cam_buffer and len(current_cam_buffer):
            image_dsc.data = current_cam_buffer
            #image.invalidate() # does not work so do this:
            image.set_src(image_dsc)
            if not use_webcam:
                cam.free_buffer()  # Free the old buffer
            if keepliveqrdecoding:
                qrdecode_one()
    except Exception as e:
        print(f"Camera capture exception: {e}")


def build_ui():
    global image, image_dsc,qr_label, status_label, cam, use_webcam, qr_button, snap_button, status_label_cont, main_screen
    main_screen = lv.obj()
    main_screen.set_style_pad_all(0, 0)
    main_screen.set_style_border_width(0, 0)
    main_screen.set_size(lv.pct(100), lv.pct(100))
    main_screen.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
    close_button = lv.button(main_screen)
    close_button.set_size(60,60)
    close_button.align(lv.ALIGN.TOP_RIGHT, 0, 0)
    close_label = lv.label(close_button)
    close_label.set_text(lv.SYMBOL.CLOSE)
    close_label.center()
    close_button.add_event_cb(close_button_click,lv.EVENT.CLICKED,None)
    snap_button = lv.button(main_screen)
    snap_button.set_size(60, 60)
    snap_button.align(lv.ALIGN.RIGHT_MID, 0, 0)
    snap_button.add_flag(lv.obj.FLAG.HIDDEN)
    snap_label = lv.label(snap_button)
    snap_label.set_text(lv.SYMBOL.OK)
    snap_label.center()
    snap_button.add_event_cb(snap_button_click,lv.EVENT.CLICKED,None)
    qr_button = lv.button(main_screen)
    qr_button.set_size(60, 60)
    qr_button.add_flag(lv.obj.FLAG.HIDDEN)
    qr_button.align(lv.ALIGN.BOTTOM_RIGHT, 0, 0)
    qr_label = lv.label(qr_button)
    qr_label.set_text(lv.SYMBOL.EYE_OPEN)
    qr_label.center()
    qr_button.add_event_cb(qr_button_click,lv.EVENT.CLICKED,None)
    # Initialize LVGL image widget
    image = lv.image(main_screen)
    image.align(lv.ALIGN.LEFT_MID, 0, 0)
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
    status_label_cont = lv.obj(main_screen)
    status_label_cont.set_size(lv.pct(66),lv.pct(60))
    status_label_cont.align(lv.ALIGN.LEFT_MID, lv.pct(5), 0)
    status_label_cont.set_style_bg_color(lv.color_white(), 0)
    status_label_cont.set_style_bg_opa(66, 0)
    status_label_cont.set_style_border_width(0, 0)
    status_label = lv.label(status_label_cont)
    status_label.set_text("No camera found.")
    status_label.set_long_mode(lv.label.LONG.WRAP)
    status_label.set_style_text_color(lv.color_white(), 0)
    status_label.set_width(lv.pct(100))
    status_label.center()
    mpos.ui.load_screen(main_screen)


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



def check_running(timer):
    if lv.screen_active() != main_screen:
        print("camtest.py backgrounded, cleaning up...")
        check_running_timer.delete()
        if capture_timer:
            capture_timer.delete()
        if use_webcam:
            webcam.deinit(cam)
        elif cam:
            cam.deinit()
        print("camtest.py cleanup done.")



build_ui()

cam = init_cam()
if cam:
    image.set_rotation(900) # internal camera is rotated 90 degrees
else:
    print("camtest.py: no internal camera found, trying webcam on /dev/video0")
    try:
        import webcam
        cam = webcam.init("/dev/video0")
        use_webcam = True
    except Exception as e:
        print(f"camtest.py: webcam exception: {e}")

if cam:
    print("Camera initialized, continuing...")
    check_running_timer = lv.timer_create(check_running, 500, None)
    qr_button.remove_flag(lv.obj.FLAG.HIDDEN)
    snap_button.remove_flag(lv.obj.FLAG.HIDDEN)
    status_label_cont.add_flag(lv.obj.FLAG.HIDDEN)
    capture_timer = lv.timer_create(try_capture, 100, None)
else:
   print("No camera found, stopping camtest.py")
