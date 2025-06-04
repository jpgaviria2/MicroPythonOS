import lvgl as lv
import mpos.apps

th = None

NOTIFICATION_BAR_HEIGHT=24

CLOCK_UPDATE_INTERVAL = 1000 # 10 or even 1 ms doesn't seem to change the framerate but 100ms is enough
WIFI_ICON_UPDATE_INTERVAL = 1500
TEMPERATURE_UPDATE_INTERVAL = 2000
MEMFREE_UPDATE_INTERVAL = 5000 # not too frequent because there's a forced gc.collect() to give it a reliable value

DRAWER_ANIM_DURATION=300

drawer=None
rootscreen = None

drawer_open=False
bar_open=False

hide_bar_animation = None
show_bar_animation = None
show_bar_animation_start_value = -NOTIFICATION_BAR_HEIGHT
show_bar_animation_end_value = 0
hide_bar_animation_start_value = show_bar_animation_end_value
hide_bar_animation_end_value = show_bar_animation_start_value

notification_bar = None

foreground_app_name=None


def get_pointer_xy():
    indev = lv.indev_active()
    if indev:
        point = lv.point_t()
        indev.get_point(point)
        return point.x, point.y
    else:
        return indev_error_x,indev_error_y # make it visible that this occurred


drawer_swipe_start_y = 0
def drawer_swipe_cb(event):
    global drawer_swipe_start_y
    event_code = event.get_code()
    #name = mpos.ui.get_event_name(event_code)
    #print(f"drawer_swipe_cb {event_code} and {name}")
    if event_code == lv.EVENT.PRESSED:
        x, drawer_swipe_start_y = get_pointer_xy()
    elif event_code == lv.EVENT.RELEASED:
        x, end_y = get_pointer_xy()
        if end_y < drawer_swipe_start_y - NOTIFICATION_BAR_HEIGHT:
            mpos.ui.close_drawer()
        drawer_swipe_start_y = 0


# Shutdown function to run in main thread
def shutdown():
    print("Shutting down...")
    lv.deinit()  # Deinitialize LVGL (if supported)
    # Add driver cleanup here
    import sys
    sys.exit(0)


def set_foreground_app(appname):
    global foreground_app_name
    foreground_app_name = appname
    print(f"foreground app is: {foreground_app_name}")

def open_drawer():
    global drawer_open, drawer
    if not drawer_open:
        open_bar()
        drawer_open=True
        drawer.remove_flag(lv.obj.FLAG.HIDDEN)

def close_drawer(to_launcher=False):
    global drawer_open, drawer
    if drawer_open:
        drawer_open=False
        drawer.add_flag(lv.obj.FLAG.HIDDEN)
        if not to_launcher and not mpos.apps.is_launcher(foreground_app_name):
            print("close_drawer: also closing bar")
            close_bar()

def open_bar():
    print("opening bar...")
    global bar_open, show_bar_animation, hide_bar_animation, notification_bar
    if not bar_open:
        #print("not open so opening...")
        bar_open=True
        hide_bar_animation.current_value = hide_bar_animation_end_value
        #show_bar_animation.current_value = hide_bar_animation_start_value
        show_bar_animation.start()
    else:
        print("bar already open")

def close_bar():
    global bar_open, show_bar_animation, hide_bar_animation
    if bar_open:
        bar_open=False
        show_bar_animation.current_value = show_bar_animation_end_value
        #hide_bar_animation.current_value = hide_bar_animation_start_value
        hide_bar_animation.start()

def show_launcher():
    mpos.apps.restart_launcher()
    #global rootscreen
    #set_foreground_app("com.example.launcher")
    #open_bar()
    #prevscreen = screen_stack[0] # load previous screen
    #lv.screen_load(prevscreen)
    #lv.screen_load(rootscreen)

def create_rootscreen():
    global rootscreen
    rootscreen = lv.screen_active()
    # Create a style for the undecorated screen
    style = lv.style_t()
    style.init()
    # Remove background (make it transparent or set no color)
    style.set_bg_opa(lv.OPA.TRANSP)  # Transparent background
    style.set_border_width(0)        # No border
    style.set_outline_width(0)       # No outline
    style.set_shadow_width(0)        # No shadow
    style.set_pad_all(0)             # No padding
    style.set_radius(0)              # No corner radius (sharp edges)
    # Apply the style to the screen
    rootscreen.add_style(style, 0)
    rootscreen.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
    #rootscreen.set_scroll_mode(lv.SCROLL_MODE.OFF)
    rootlabel = lv.label(rootscreen)
    rootlabel.set_text("Welcome!")
    rootlabel.align(lv.ALIGN.CENTER, 0, 0)


timer1 = None
timer2 = None
timer3 = None
timer4 = None

def create_notification_bar():
    global notification_bar
    global timer1, timer2, timer3, timer4
    # Create notification bar
    notification_bar = lv.obj(lv.layer_top())
    notification_bar.set_size(lv.pct(100), NOTIFICATION_BAR_HEIGHT)
    notification_bar.set_pos(0, show_bar_animation_start_value)
    notification_bar.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
    notification_bar.set_scroll_dir(lv.DIR.VER)
    notification_bar.set_style_border_width(0, 0)
    notification_bar.set_style_radius(0, 0)
    # Time label
    time_label = lv.label(notification_bar)
    time_label.set_text("00:00:00")
    time_label.align(lv.ALIGN.LEFT_MID, 0, 0)
    temp_label = lv.label(notification_bar)
    temp_label.set_text("00°C")
    temp_label.align_to(time_label, lv.ALIGN.OUT_RIGHT_MID, NOTIFICATION_BAR_HEIGHT	, 0)
    memfree_label = lv.label(notification_bar)
    memfree_label.set_text("")
    memfree_label.align_to(temp_label, lv.ALIGN.OUT_RIGHT_MID, NOTIFICATION_BAR_HEIGHT, 0)
    #style = lv.style_t()
    #style.init()
    #style.set_text_font(lv.font_montserrat_8)  # tiny font
    #memfree_label.add_style(style, 0)
    # Notification icon (bell)
    #notif_icon = lv.label(notification_bar)
    #notif_icon.set_text(lv.SYMBOL.BELL)
    #notif_icon.align_to(time_label, lv.ALIGN.OUT_RIGHT_MID, PADDING_TINY, 0)
    # Battery icon
    battery_icon = lv.label(notification_bar)
    battery_icon.set_text(lv.SYMBOL.BATTERY_FULL)
    battery_icon.align(lv.ALIGN.RIGHT_MID, 0, 0)
    # WiFi icon
    wifi_icon = lv.label(notification_bar)
    wifi_icon.set_text(lv.SYMBOL.WIFI)
    wifi_icon.align_to(battery_icon, lv.ALIGN.OUT_LEFT_MID, -NOTIFICATION_BAR_HEIGHT, 0)
    wifi_icon.add_flag(lv.obj.FLAG.HIDDEN)
    # Battery percentage - not shown to conserve space
    #battery_label = lv.label(notification_bar)
    #battery_label.set_text("100%")
    #battery_label.align(lv.ALIGN.RIGHT_MID, 0, 0)
    # Update time
    import time
    def update_time(timer):
        hours = time.localtime()[3]
        minutes = time.localtime()[4]
        seconds = time.localtime()[5]
        time_label.set_text(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    
    can_check_network = False
    try:
        import network
        can_check_network = True
    except Exception as e:
        print("Warning: could not check WLAN status:", str(e))
    
    def update_wifi_icon(timer):
        if not can_check_network or network.WLAN(network.STA_IF).isconnected():
            wifi_icon.remove_flag(lv.obj.FLAG.HIDDEN)
        else:
            wifi_icon.add_flag(lv.obj.FLAG.HIDDEN)
    
    can_check_temperature = False
    try:
        import esp32
        can_check_temperature = True
    except Exception as e:
        print("Warning: can't check temperature sensor:", str(e))
    
    def update_temperature(timer):
        if can_check_temperature:
            temp_label.set_text(f"{esp32.mcu_temperature()}°C")
        else:
            temp_label.set_text("42°C")
    
    def update_memfree(timer):
        import gc
        gc.collect() # otherwise it goes down to 10% before shooting back up to 70%
        free = gc.mem_free()
        used = gc.mem_alloc()
        total_memory = gc.mem_free() + gc.mem_alloc()
        percentage = round(free * 100 / (free + used))
        memfree_label.set_text(f"{percentage}%")
    
    timer1 = lv.timer_create(update_time, CLOCK_UPDATE_INTERVAL, None)
    timer2 = lv.timer_create(update_temperature, TEMPERATURE_UPDATE_INTERVAL, None)
    timer3 = lv.timer_create(update_memfree, MEMFREE_UPDATE_INTERVAL, None)
    timer4 = lv.timer_create(update_wifi_icon, WIFI_ICON_UPDATE_INTERVAL, None)
    
    # hide bar animation
    global hide_bar_animation
    hide_bar_animation = lv.anim_t()
    hide_bar_animation.init()
    hide_bar_animation.set_var(notification_bar)
    hide_bar_animation.set_values(0, -NOTIFICATION_BAR_HEIGHT)
    hide_bar_animation.set_time(2000)
    hide_bar_animation.set_custom_exec_cb(lambda not_used, value : notification_bar.set_y(value))
    
    # show bar animation
    global show_bar_animation
    show_bar_animation = lv.anim_t()
    show_bar_animation.init()
    show_bar_animation.set_var(notification_bar)
    show_bar_animation.set_values(show_bar_animation_start_value, show_bar_animation_end_value)
    show_bar_animation.set_time(1000)
    show_bar_animation.set_custom_exec_cb(lambda not_used, value : notification_bar.set_y(value))
    


def create_drawer(display=None):
    global drawer
    drawer=lv.obj(lv.layer_top())
    drawer.set_size(lv.pct(100),lv.pct(90))
    drawer.set_pos(0,NOTIFICATION_BAR_HEIGHT)
    drawer.set_scroll_dir(lv.DIR.NONE)
    drawer.set_style_pad_all(0, 0)
    drawer.set_style_border_width(0, 0)
    drawer.set_style_radius(0, 0)
    drawer.add_flag(lv.obj.FLAG.HIDDEN)
    #drawer.add_flag(lv.obj.FLAG.GESTURE_BUBBLE) # no gestures are received... maybe not supported by SDL Pointer Driver...
    drawer.add_event_cb(drawer_swipe_cb, lv.EVENT.PRESSED, None)
    drawer.add_event_cb(drawer_swipe_cb, lv.EVENT.RELEASED, None)    
    slider_label=lv.label(drawer)
    slider_label.set_text(f"{100}%") # TODO: restore this from configuration
    slider_label.align(lv.ALIGN.TOP_MID,0,lv.pct(4))
    slider=lv.slider(drawer)
    slider.set_range(1,100)
    slider.set_value(100,False)
    slider.set_width(lv.pct(80))
    slider.align_to(slider_label,lv.ALIGN.OUT_BOTTOM_MID,0,lv.pct(4))
    def slider_event(e):
        value=slider.get_value()
        slider_label.set_text(f"{value}%")
        if display:
            display.set_backlight(value)
    
    slider.add_event_cb(slider_event,lv.EVENT.VALUE_CHANGED,None)
    wifi_btn=lv.button(drawer)
    wifi_btn.set_size(lv.pct(40),lv.SIZE_CONTENT)
    wifi_btn.align(lv.ALIGN.LEFT_MID,0,0)
    wifi_label=lv.label(wifi_btn)
    wifi_label.set_text(lv.SYMBOL.WIFI+" WiFi")
    wifi_label.center()
    def wifi_event(e):
        global drawer_open
        close_drawer()
        mpos.apps.start_app_by_name("com.micropythonos.wificonf")
    
    wifi_btn.add_event_cb(wifi_event,lv.EVENT.CLICKED,None)
    #
    #settings_btn=lv.button(drawer)
    #settings_btn.set_size(BUTTON_WIDTH,BUTTON_HEIGHT)
    #settings_btn.align(lv.ALIGN.RIGHT_MID,-PADDING_MEDIUM,0)
    #settings_label=lv.label(settings_btn)
    #settings_label.set_text(lv.SYMBOL.SETTINGS+" Settings")
    #settings_label.center()
    #def settings_event(e):
    #    global drawer_open
    #    close_drawer()
    
    #settings_btn.add_event_cb(settings_event,lv.EVENT.CLICKED,None)
    #
    launcher_btn=lv.button(drawer)
    launcher_btn.set_size(lv.pct(40),lv.SIZE_CONTENT)
    launcher_btn.align(lv.ALIGN.BOTTOM_LEFT,0,0)
    launcher_label=lv.label(launcher_btn)
    launcher_label.set_text(lv.SYMBOL.HOME+" Launcher")
    launcher_label.center()
    def launcher_event(e):
        print("Launcher button pressed!")
        global drawer_open
        close_drawer(True)
        show_launcher()
    
    launcher_btn.add_event_cb(launcher_event,lv.EVENT.CLICKED,None)
    #
    restart_btn=lv.button(drawer)
    restart_btn.set_size(lv.pct(40),lv.SIZE_CONTENT)
    restart_btn.align(lv.ALIGN.RIGHT_MID,0,0)
    restart_label=lv.label(restart_btn)
    restart_label.set_text(lv.SYMBOL.POWER+" Reset")
    restart_label.center()
    def reset_cb(e):
        import machine
        if hasattr(machine, 'reset'):
            machine.reset()
        elif hasattr(machine, 'soft_reset'):
            machine.soft_reset()
        else:
            print("Warning: machine has no reset or soft_reset method available")
    
    try:
        restart_btn.add_event_cb(reset_cb,lv.EVENT.CLICKED,None)
    except Exception as e:
        print("Warning: could not import machine, not adding reset callback")
    
    poweroff_btn=lv.button(drawer)
    poweroff_btn.set_size(lv.pct(40),lv.SIZE_CONTENT)
    poweroff_btn.align(lv.ALIGN.BOTTOM_RIGHT,0,0)
    poweroff_label=lv.label(poweroff_btn)
    poweroff_label.set_text(lv.SYMBOL.POWER+" Power Off")
    poweroff_label.center()
    def poweroff_cb(e):
        lv.deinit()  # Deinitialize LVGL (if supported)
        import sys
        sys.exit(0)
    
    poweroff_btn.add_event_cb(poweroff_cb,lv.EVENT.CLICKED,None)
    



EVENT_MAP = {
    lv.EVENT.ALL: "ALL",
    lv.EVENT.CANCEL: "CANCEL",
    lv.EVENT.CHILD_CHANGED: "CHILD_CHANGED",
    lv.EVENT.CHILD_CREATED: "CHILD_CREATED",
    lv.EVENT.CHILD_DELETED: "CHILD_DELETED",
    lv.EVENT.CLICKED: "CLICKED",
    lv.EVENT.COLOR_FORMAT_CHANGED: "COLOR_FORMAT_CHANGED",
    lv.EVENT.COVER_CHECK: "COVER_CHECK",
    lv.EVENT.CREATE: "CREATE",
    lv.EVENT.DEFOCUSED: "DEFOCUSED",
    lv.EVENT.DELETE: "DELETE",
    lv.EVENT.DRAW_MAIN: "DRAW_MAIN",
    lv.EVENT.DRAW_MAIN_BEGIN: "DRAW_MAIN_BEGIN",
    lv.EVENT.DRAW_MAIN_END: "DRAW_MAIN_END",
    lv.EVENT.DRAW_POST: "DRAW_POST",
    lv.EVENT.DRAW_POST_BEGIN: "DRAW_POST_BEGIN",
    lv.EVENT.DRAW_POST_END: "DRAW_POST_END",
    lv.EVENT.DRAW_TASK_ADDED: "DRAW_TASK_ADDED",
    lv.EVENT.FLUSH_FINISH: "FLUSH_FINISH",
    lv.EVENT.FLUSH_START: "FLUSH_START",
    lv.EVENT.FLUSH_WAIT_FINISH: "FLUSH_WAIT_FINISH",
    lv.EVENT.FLUSH_WAIT_START: "FLUSH_WAIT_START",
    lv.EVENT.FOCUSED: "FOCUSED",
    lv.EVENT.GESTURE: "GESTURE",
    lv.EVENT.GET_SELF_SIZE: "GET_SELF_SIZE",
    lv.EVENT.HIT_TEST: "HIT_TEST",
    lv.EVENT.HOVER_LEAVE: "HOVER_LEAVE",
    lv.EVENT.HOVER_OVER: "HOVER_OVER",
    lv.EVENT.INDEV_RESET: "INDEV_RESET",
    lv.EVENT.INSERT: "INSERT",
    lv.EVENT.INVALIDATE_AREA: "INVALIDATE_AREA",
    lv.EVENT.KEY: "KEY",
    lv.EVENT.LAST: "LAST",
    lv.EVENT.LAYOUT_CHANGED: "LAYOUT_CHANGED",
    lv.EVENT.LEAVE: "LEAVE",
    lv.EVENT.LONG_PRESSED: "LONG_PRESSED",
    lv.EVENT.LONG_PRESSED_REPEAT: "LONG_PRESSED_REPEAT",
    lv.EVENT.PREPROCESS: "PREPROCESS",
    lv.EVENT.PRESSED: "PRESSED",
    lv.EVENT.PRESSING: "PRESSING",
    lv.EVENT.PRESS_LOST: "PRESS_LOST",
    lv.EVENT.READY: "READY",
    lv.EVENT.REFRESH: "REFRESH",
    lv.EVENT.REFR_EXT_DRAW_SIZE: "REFR_EXT_DRAW_SIZE",
    lv.EVENT.REFR_READY: "REFR_READY",
    lv.EVENT.REFR_REQUEST: "REFR_REQUEST",
    lv.EVENT.REFR_START: "REFR_START",
    lv.EVENT.RELEASED: "RELEASED",
    lv.EVENT.RENDER_READY: "RENDER_READY",
    lv.EVENT.RENDER_START: "RENDER_START",
    lv.EVENT.RESOLUTION_CHANGED: "RESOLUTION_CHANGED",
    lv.EVENT.ROTARY: "ROTARY",
    lv.EVENT.SCREEN_LOADED: "SCREEN_LOADED",
    lv.EVENT.SCREEN_LOAD_START: "SCREEN_LOAD_START",
    lv.EVENT.SCREEN_UNLOADED: "SCREEN_UNLOADED",
    lv.EVENT.SCREEN_UNLOAD_START: "SCREEN_UNLOAD_START",
    lv.EVENT.SCROLL: "SCROLL",
    lv.EVENT.SCROLL_BEGIN: "SCROLL_BEGIN",
    lv.EVENT.SCROLL_END: "SCROLL_END",
    lv.EVENT.SCROLL_THROW_BEGIN: "SCROLL_THROW_BEGIN",
    lv.EVENT.SHORT_CLICKED: "SHORT_CLICKED",
    lv.EVENT.SIZE_CHANGED: "SIZE_CHANGED",
    lv.EVENT.STYLE_CHANGED: "STYLE_CHANGED",
    lv.EVENT.VALUE_CHANGED: "VALUE_CHANGED",
    lv.EVENT.VSYNC: "VSYNC"
}

# Function to translate event code to name
def get_event_name(event_code):
    return EVENT_MAP.get(event_code, f"Unknown event {event_code}")


def close_top_layer_msgboxes():
    """
    Iterate through all widgets in lv.layer_top() and close any lv.msgbox instances.
    """
    top_layer = lv.layer_top()
    if not top_layer:
        print("No top layer found")
        return

    # Get number of children
    child_count = top_layer.get_child_count_by_type(lv.msgbox_backdrop_class)
    print(f"Top layer has {child_count} msgbox_backdrops")

    # Iterate through children (use index to avoid modifying list during deletion)
    i = 0
    while i < top_layer.get_child_count_by_type(lv.msgbox_backdrop_class):
        child = top_layer.get_child_by_type(i,lv.msgbox_backdrop_class)
        print("Found msgbox, closing it")
        msgbox = child.get_child_by_type(0,lv.msgbox_class)
        msgbox.close()  # Close the message box
        # Note: lv.msgbox_close() may delete the object, so child count may change

    # Optional: Verify no msgboxes remain
    child_count = top_layer.get_child_count_by_type(lv.msgbox_backdrop_class)
    if child_count == 0:
        print("All msgboxes closed, top layer empty")
    else:
        print(f"Top layer still has {child_count} children")


screen_stack = [] # Stack of (activity, screen) tuples

def empty_screen_stack():
    global screen_stack
    screen_stack.clear()


#def load_screen(screen):
#    setContentView(None, screen) # for compatibility with old apps

# new_activity might be None for compatibility, can be removed if compatibility is no longer needed
def setContentView(new_activity, new_screen):
    global screen_stack

    # Get current activity and screen
    current_activity, current_screen = None, None
    if len(screen_stack) > 0:
        current_activity, current_screen = screen_stack[-1]

    if current_activity and current_screen:
        # Notify current activity that it's being backgrounded:
        current_activity.onPause(current_screen)
        current_activity.onStop(current_screen)
        # don't destroy because the user might go back to it

    # Start the new one:
    print("Appending screen to screen_stack")
    screen_stack.append((new_activity, new_screen))
    close_top_layer_msgboxes() # otherwise they remain
    if new_activity:
        new_activity.onStart(new_screen)  # Initialize UI elements
    lv.screen_load(new_screen)
    if new_activity:
        new_activity.onResume(new_screen)  # Screen is now active


def back_screen():
    global screen_stack
    if len(screen_stack) <= 1:
        print("Warning: can't go back because screen_stack is empty.")
        return False  # No previous screen
    #close_top_layer_msgboxes() # would be nicer to "cancel" all input events
    print("Loading previous screen")
    current_activity, current_screen = screen_stack.pop()  # Remove current screen
    if current_activity:
        current_activity.onPause(current_screen)
        current_activity.onStop(current_screen)
        current_activity.onDestroy(current_screen)
    # System deletes the screen
    if current_screen:
        current_screen.delete()
        current_screen = None
    prev_activity, prev_screen = screen_stack[-1] # load previous screen
    lv.screen_load(prev_screen)
    if prev_activity:
        prev_activity.onResume(prev_screen)
    if len(screen_stack) == 1:
        open_bar()



# Would be better to somehow save other events, like clicks, and pass them down to the layers below if released with x < 60
def back_swipe_cb(event):
    if drawer_open:
        print("ignoring back gesture because drawer is open")
        return

    event_code = event.get_code()
    #name = mpos.ui.get_event_name(event_code)
    #print(f"back_swipe_cb {event_code} and {name}")

    #xa = rect.get_x_aligned()
    #ya = rect.get_y_aligned()
    #print(f"xa, ya: {xa},{ya}")

    #obj = e.get_target()
    #lvobj = lv.obj(obj)
    #pos = lvobj.get_pos()  # Get current position
    #print(f"pos: {lvobj.get_x()}, {lvobj.get_y()}")

    indev = lv.indev_active()
    if indev:
        point = lv.point_t()
        indev.get_point(point)
        x = point.x
        y = point.y
        print(f"pos: {x}, {y}")
        #rect.set_pos(x, 0)
        if event_code == lv.EVENT.RELEASED and x > 60: # TODO: use display_width / 3 here
            mpos.ui.back_screen()
            #rect.set_pos(0,0)
        #rect.set_pos(xa + point.x, ya + point.y)
        #rect.set_pos(point.x, point.y)


def handle_back_swipe():
    rect = lv.obj(lv.layer_top())
    rect.set_size(NOTIFICATION_BAR_HEIGHT, lv.layer_top().get_height()-NOTIFICATION_BAR_HEIGHT)
    rect.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
    rect.set_pos(0, NOTIFICATION_BAR_HEIGHT)
    style = lv.style_t()
    style.init()
    style.set_bg_opa(lv.OPA.TRANSP)
    #style.set_bg_opa(15)
    style.set_border_width(0)
    style.set_radius(0)
    #style.set_border_color(lv.color_hex(0xFF0000))  # White border for visibility
    #style.set_border_opa(lv.OPA._50)  # 50% opacity for the border
    rect.add_style(style, 0)
    #rect.add_flag(lv.obj.FLAG.CLICKABLE)  # Make the object clickable
    #rect.add_flag(lv.obj.FLAG.GESTURE_BUBBLE)  # Allow dragging
    #rect.add_event_cb(drag_event_cb, lv.EVENT.PRESSING, None)
    rect.add_event_cb(back_swipe_cb, lv.EVENT.RELEASED, None)

# Would be better to somehow save other events, like clicks, and pass them down to the layers below if released with x < 60
def top_swipe_cb(event):
    #global rect

    event_code = event.get_code()
    name = mpos.ui.get_event_name(event_code)
    print(f"top_swipe_cb {event_code} and {name}")

    #xa = rect.get_x_aligned()
    #ya = rect.get_y_aligned()
    #print(f"xa, ya: {xa},{ya}")

    #obj = e.get_target()
    #lvobj = lv.obj(obj)
    #pos = lvobj.get_pos()  # Get current position
    #print(f"pos: {lvobj.get_x()}, {lvobj.get_y()}")

    indev = lv.indev_active()
    if indev:
        point = lv.point_t()
        indev.get_point(point)
        x = point.x
        y = point.y
        print(f"pos: {x}, {y}")
        #rect.set_pos(x, 0)
        if event_code == lv.EVENT.RELEASED and y > 60: # TODO: use display_height / 3 here
            mpos.ui.open_drawer()
            #rect.set_pos(0,0)
        #rect.set_pos(xa + point.x, ya + point.y)
        #rect.set_pos(point.x, point.y)


def handle_top_swipe():
    rect = lv.obj(lv.layer_top())
    rect.set_size(lv.pct(100), NOTIFICATION_BAR_HEIGHT)
    rect.set_pos(0, 0)
    rect.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
    style = lv.style_t()
    style.init()
    style.set_bg_opa(lv.OPA.TRANSP)
    #style.set_bg_opa(15)
    style.set_border_width(0)
    style.set_radius(0)
    #style.set_border_color(lv.color_hex(0xFF0000))  # White border for visibility
    #style.set_border_opa(lv.OPA._50)  # 50% opacity for the border
    rect.add_style(style, 0)
    #rect.add_flag(lv.obj.FLAG.CLICKABLE)  # Make the object clickable
    #rect.add_flag(lv.obj.FLAG.GESTURE_BUBBLE)  # Allow dragging
    #rect.add_event_cb(drag_event_cb, lv.EVENT.PRESSING, None)
    rect.add_event_cb(top_swipe_cb, lv.EVENT.RELEASED, None)
