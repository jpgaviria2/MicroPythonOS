import lcd_bus
import lvgl as lv
import sdl_display
import sdl_pointer
import mpos.ui

TFT_HOR_RES=320
TFT_VER_RES=240

bus = lcd_bus.SDLBus(flags=0)

buf1 = bus.allocate_framebuffer(TFT_HOR_RES * TFT_VER_RES * 2, 0)

display = sdl_display.SDLDisplay(data_bus=bus,display_width=TFT_HOR_RES,display_height=TFT_VER_RES,frame_buffer1=buf1,color_space=lv.COLOR_FORMAT.RGB565)
display.init()

mouse = sdl_pointer.SDLPointer()

# Swipe detection state
start_y = None  # Store the starting Y-coordinate of the mouse press
def swipe_read_cb(indev_drv, data):
    global start_y

    pressed = mouse.get_state()
    #print(f"mouse_state: {pressed}")
    point = lv.point_t()
    mouse.get_point(point)
    #print(f"X={point.x}, Y={point.y}")
    x, y = point.x, point.y

    if pressed and start_y is None:
        start_y = y
        # Mouse button pressed (start of potential swipe)
        if y <= mpos.ui.NOTIFICATION_BAR_HEIGHT:
            # Store starting Y if press is in the notification bar area
            print(f"Mouse press at Y={start_y}")
    elif pressed and start_y is not None:
        # Mouse dragged while pressed (potential swipe in progress)
        # Check for downward swipe (y increased significantly)
        if y > start_y + 50:  # Threshold for swipe detection (adjust as needed)
            print("long swipe down")
            if start_y <= mpos.ui.NOTIFICATION_BAR_HEIGHT:
                print("Swipe Down Detected from Notification Bar")
                mpos.ui.open_drawer()
            start_y = None  # Reset after swipe
    else:
        # Mouse button released
        if start_y is not None and y < start_y - 50:  # Threshold for swipe-up
            print("Swipe Up Detected")
            mpos.ui.close_drawer()
        start_y = None  # Reset on release

# Register the custom read callback with the input device
indev = lv.indev_create()
indev.set_type(lv.INDEV_TYPE.POINTER)
indev.set_read_cb(swipe_read_cb)

print("boot_unix.py finished")

