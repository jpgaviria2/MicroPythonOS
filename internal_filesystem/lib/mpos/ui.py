import lvgl as lv
import mpos.apps

th = None

NOTIFICATION_BAR_HEIGHT=24

CLOCK_UPDATE_INTERVAL = 1000 # 10 or even 1 ms doesn't seem to change the framerate but 100ms is enough
WIFI_ICON_UPDATE_INTERVAL = 1500
TEMPERATURE_UPDATE_INTERVAL = 2000
#MEMFREE_UPDATE_INTERVAL = 5000 # not too frequent because there's a forced gc.collect() to give it a reliable value

DRAWER_ANIM_DURATION=300

drawer=None
rootscreen = None

drawer_open=False
bar_open=True

hide_bar_animation = None
show_bar_animation = None
show_bar_animation_start_value = -NOTIFICATION_BAR_HEIGHT
show_bar_animation_end_value = 0
hide_bar_animation_start_value = show_bar_animation_end_value
hide_bar_animation_end_value = show_bar_animation_start_value

notification_bar = None

foreground_app_name=None

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
        print("not open so opening...")
        bar_open=True
        hide_bar_animation.current_value = hide_bar_animation_end_value # stop the hide animation
        show_bar_animation.current_value = hide_bar_animation_start_value
        #show_bar_animation.start() # coming from the camera, this doesn't work?!
        notification_bar.set_y(show_bar_animation_end_value) # workaround is fine
    else:
        print("bar already open")

def close_bar():
    global bar_open, show_bar_animation, hide_bar_animation
    if bar_open:
        bar_open=False
        show_bar_animation.current_value = show_bar_animation_end_value # stop the show animation
        hide_bar_animation.current_value = hide_bar_animation_start_value
        hide_bar_animation.start()

def show_launcher():
    global rootscreen
    set_foreground_app("com.example.launcher")
    open_bar()
    lv.screen_load(rootscreen)

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


def create_notification_bar():
    global notification_bar
    # Create notification bar
    notification_bar = lv.obj(lv.layer_top())
    notification_bar.set_size(lv.pct(100), NOTIFICATION_BAR_HEIGHT)
    notification_bar.set_pos(0, 0)
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
    #memfree_label = lv.label(notification_bar)
    #memfree_label.set_text("")
    #memfree_label.align_to(temp_label, lv.ALIGN.OUT_RIGHT_MID, NOTIFICATION_BAR_HEIGHT, 0)
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
        ticks = time.ticks_ms()
        hours = (ticks // 3600000) % 24
        minutes = (ticks // 60000) % 60
        seconds = (ticks // 1000) % 60
        #milliseconds = ticks % 1000
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
    
    
    #import gc
    #def update_memfree(timer):
    #    gc.collect()
    #    memfree_label.set_text(f"{gc.mem_free()}")
    
    timer1 = lv.timer_create(update_time, CLOCK_UPDATE_INTERVAL, None)
    timer2 = lv.timer_create(update_temperature, TEMPERATURE_UPDATE_INTERVAL, None)
    #timer3 = lv.timer_create(update_memfree, MEMFREE_UPDATE_INTERVAL, None)
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
    

def create_drawer(display):
    global drawer
    drawer=lv.obj(lv.layer_top())
    drawer.set_size(lv.pct(100),lv.pct(90))
    drawer.set_pos(0,NOTIFICATION_BAR_HEIGHT)
    drawer.set_scroll_dir(lv.DIR.NONE)
    drawer.set_style_pad_all(0, 0)
    drawer.add_flag(lv.obj.FLAG.HIDDEN)
    
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
        start_app_by_name("com.example.wificonf")
    
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
    restart_btn.add_event_cb(lambda event: machine.reset(),lv.EVENT.CLICKED,None)
    
