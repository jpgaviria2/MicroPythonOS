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
start_y = None  # Store the starting Y-coordinate of the mouse press
start_x = None  # Store the starting X-coordinate for left-edge swipe

# the problem is, this whole thing is called after the click/release has been processed by the screen...
def swipe_read_cb(indev_drv, data):
    global start_y, start_x
    global indev
    global mouse
    
    mouseindev = mouse._indevs[0]
    #print(indev) # none...
    #print(mouse.get_event_count())
    #print(mouseindev.get_event_count()) # 0
    #mouseindev.stop_processing()
    #mouseindev.enable(False) # well this works...
    #mouseindev.__x = -1 # works
    #mouseindev.__y = -1 # works
    #print(mouse._indevs[0])

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
                #mouseindev.enable(False) # well this works...
                mouseindev.wait_release()
                mpos.ui.back_screen()  # Call custom method for left menu
            start_y = None  # Reset Y after swipe
            start_x = None  # Reset X after swipe
        
        # Reset both coordinates on release
        start_y = None
        start_x = None

def get_xy():
    indev = lv.indev_active()
    if indev:
        point = lv.point_t()
        indev.get_point(point)
        return point.x, point.y
    else:
        return indev_error_x,indev_error_y # make it visible that this occurred

def test_indev_cb(event):
    print("test_indev_cb")

def test_cb(event):
    print("test_cb")
    event_code=event.get_code()
    name = mpos.ui.get_event_name(event_code)
    print(f"lv_event_t: code={event_code}, name={name}") # target={event.get_target()}, user_data={event.get_user_data()}, param={event.get_param()}
    x, y = get_xy()
    print(f"x,y = {x},{y}")
    # try to disable the event
    event.stop_processing()
    event.stop_bubbling()
    #global mouse    
    #mouseindev = mouse._indevs[0]
    #mouseindev.__x = -1 # works
    #mouseindev.__y = -1 # works
    #mouseindev.wait_release() # results in only PRESSED and then it stops...
    #if event_code == lv.EVENT.RELEASED or event_code == lv.EVENT.CLICKED:
    #    mouseindev.wait_release() # results in only PRESSED and then it stops...
        #mouseindev.enable(False) # well this works...

gesture_start_x = None
gesture_start_y = None
def detect_gesture(event, pressed, x, y):
    global mouse
    global gesture_start_x, gesture_start_y
    
    mouseindev = mouse._indevs[0]
    event.stop_processing()
    event.stop_bubbling()
    #event.remove_all()

    if pressed and gesture_start_x is None :
        # Mouse/touch pressed (start of potential swipe)
        gesture_start_y = y  # Store Y for vertical swipe detection
        gesture_start_x = x  # Store X for horizontal swipe detection
        #print(f"Mouse press at X={start_x}, Y={start_y}")
        
        # Check if press is in notification bar (for swipe down)
        if y <= mpos.ui.NOTIFICATION_BAR_HEIGHT:
            print(f"Press in notification bar at Y={start_y}")
        # Check if press is near left edge (for swipe right)
        if x <= 20:  # Adjust threshold for left edge (e.g., 20 pixels)
            print(f"Press near left edge at X={start_x}")
    elif pressed and gesture_start_x is not None:
        # Mouse/touch dragged while pressed (potential swipe in progress)
        print("tracking pressed")
        if gesture_start_x <= 20:  # Confirm swipe started near left edge
            print("tracking pressed with swipe started left")
            #mpos.ui.back_screen()  # Call custom method for left menu
            mouse.wait_release() # causes only presses to be detected anymore
            #mouseindev.wait_release() # causes only presses to be detected anymore
            #event.stop_processing()
            #event.stop_bubbling()
            #mouseindev.__x = -1
            #mouseindev.__y = -1
            #mouseindev.enable(False) # causes no pressed to be detected anymore because no events
            # Idea: show a full-screen widget that captures the presses?
    else:
        # Check for rightward swipe from left edge (x increased significantly)
        if gesture_start_x is not None and x > gesture_start_x + 50:  # Threshold for swipe right
            print("Long swipe right")
            if gesture_start_x <= 20:  # Confirm swipe started near left edge
                print("!!! Swipe Right Detected from Left Edge")
                mpos.ui.back_screen()  # Call custom method for left menu
                #mouse.wait_release()
                #mouseindev.wait_release()
                #event.stop_processing()
                #event.stop_bubbling()
                #mouseindev.__x = -1
                #mouseindev.__y = -1
                #mouseindev.enable(False)
        
        # Reset both coordinates on release
        gesture_start_y = None
        gesture_start_x = None
        #mouseindev.enable(True) # well this works...


def detect_swipe(event):
    global mouse
    pressed = mouse.get_state()  # Get mouse/touch pressed state
    point = lv.point_t()
    mouse.get_point(point)  # Get current coordinates
    x, y = point.x, point.y
    code = event.get_code()
    name = mpos.ui.get_event_name(code)
    print(f"detect_swipe got {pressed},{x},{y} with {code},{name}")
    event.stop_processing()
    # crashes: target_obj = event.get_target_obj()  # Get the widget that triggered the event
    target = event.get_target()  # Get the widget that triggered the event
    print("Event triggered by target:", target)
    ctarget = event.get_current_target()  # Get the widget that triggered the event
    print("Event triggered by ctarget:", ctarget)
    #target_obj = lv.obj.cast(target)
    target_obj = lv.obj(target)  # Wrap the Blob as an lv.obj
    print("Event triggered by object:", target_obj)
    # Example: Check if the object is a button
    if isinstance(target_obj, lv.button):
        print("This is a button!")
    elif isinstance(target_obj, lv.obj):
        print("This is a generic LVGL object")
    #event.remove()
    #event.removeall()
    # this also works:
    #mouseindev = mouse._indevs[0]
    #mouseindev.get_point(point) # Always returns 0,0
    #x, y = point.x, point.y
    #print(f"detect_swipe got {x},{y} from mouseindev")
    
    detect_gesture(event, pressed, x, y)


# this seems to work for capturing mouse events:
#mouse.add_event_cb(detect_swipe, lv.EVENT.ALL, None)

def re_enable_upon_release(indev_drv, data):
    #print("re_enable_upon_release")
    global mouse
    #pressed = mouse.get_state()  # doesn't change if mouseindev has been disabled
    #print(f"re_enable_upon_release {pressed}")
    #if not pressed:
    mouseindev = mouse._indevs[0]
    mouseindev.enable(True) # causes no pressed to be detected anymore because no events

# Register the custom read callback with the input device
#indev = lv.indev_create()
#indev.set_type(lv.INDEV_TYPE.POINTER)
#indev.set_read_cb(re_enable_upon_release)

#indev = lv.indev_active()
#if not indev:
#    print("ERROR: could not get active indev?!")
#else:
#    indev.set_read_cb(test_indev_cb)



print("boot_unix.py finished")

