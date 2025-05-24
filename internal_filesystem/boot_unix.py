# Hardware initialization for Unix and MacOS systems

import lcd_bus
import lvgl as lv
import sdl_display

import mpos.ui

#TFT_HOR_RES=640
#TFT_VER_RES=480
TFT_HOR_RES=320
TFT_VER_RES=240

bus = lcd_bus.SDLBus(flags=0)

buf1 = bus.allocate_framebuffer(TFT_HOR_RES * TFT_VER_RES * 2, 0)

display = sdl_display.SDLDisplay(data_bus=bus,display_width=TFT_HOR_RES,display_height=TFT_VER_RES,frame_buffer1=buf1,color_space=lv.COLOR_FORMAT.RGB565)
display.init()

import sdl_pointer
mouse = sdl_pointer.SDLPointer()

#import sdl_keyboard
#keyboard = sdl_keyboard.SDLKeyboard()


#def keyboard_cb(event):
 #   global canvas
  #  event_code=event.get_code()
   # print(f"boot_unix: code={event_code}") # target={event.get_target()}, user_data={event.get_user_data()}, param={event.get_param()}

#keyboard.add_event_cb(keyboard_cb, lv.EVENT.ALL, None)


# Swipe detection state
# Swipe detection state
start_y = None  # Store the starting Y-coordinate of the mouse press
start_x = None  # Store the starting X-coordinate for left-edge swipe

def swipe_read_cb(indev_drv, data):
    global start_y, start_x
    global indev
    global mouse

    pressed = mouse.get_state()  # Get mouse/touch pressed state
    point = lv.point_t()
    mouse.get_point(point)  # Get current coordinates
    #indev.get_point(point) # Always returns 0,0
    x, y = point.x, point.y
    
    #indev.stop_processing()
    #data.state = lv.INDEV_STATE.RELEASED  # Ensure release state
    #data.point.x = -1  # Move point off-screen to prevent widget interaction
    #data.point.y = -1
    #indev.stop_processing() # doesn't work on unix
    #return
    #mouse.stop_processing()

    if pressed and start_y is None and start_x is None:
        # Mouse/touch pressed (start of potential swipe)
        start_y = y  # Store Y for vertical swipe detection
        start_x = x  # Store X for horizontal swipe detection
        #print(f"Mouse press at X={start_x}, Y={start_y}")
        
        # Check if press is in notification bar (for swipe down)
        if y <= mpos.ui.NOTIFICATION_BAR_HEIGHT:
            print(f"Press in notification bar at Y={start_y}")
        # Check if press is near left edge (for swipe right)
        if x <= 20:  # Adjust threshold for left edge (e.g., 20 pixels)
            print(f"Press near left edge at X={start_x}")
    elif pressed and (start_y is not None or start_x is not None):
        # Mouse/touch dragged while pressed (potential swipe in progress)
        
        # Check for downward swipe (y increased significantly)
        if start_y is not None and y > start_y + 50:  # Threshold for swipe down
            print("Long swipe down")
            if start_y <= mpos.ui.NOTIFICATION_BAR_HEIGHT:
                print("Swipe Down Detected from Notification Bar")
                mpos.ui.open_drawer()
            start_y = None  # Reset Y after swipe
            start_x = None  # Reset X to avoid conflicts
    else:
        # Mouse/touch released
        if start_y is not None and y < start_y - 50:  # Threshold for swipe-up
            print("Swipe Up Detected")
            mpos.ui.close_drawer()

        # Check for rightward swipe from left edge (x increased significantly)
        if start_x is not None and x > start_x + 50:  # Threshold for swipe right
            print("Long swipe right")
            if start_x <= 20:  # Confirm swipe started near left edge
                print("Swipe Right Detected from Left Edge")
                mpos.ui.back_screen()  # Call custom method for left menu
            start_y = None  # Reset Y after swipe
            start_x = None  # Reset X after swipe
        
        # Reset both coordinates on release
        start_y = None
        start_x = None

# Register the custom read callback with the input device
indev = lv.indev_create()
indev.set_type(lv.INDEV_TYPE.POINTER)
indev.set_read_cb(swipe_read_cb)

print("boot_unix.py finished")

