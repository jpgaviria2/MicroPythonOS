# Constants
CURRENT_VERSION = "0.0.1"
TFT_HOR_RES=320
TFT_VER_RES=240
NOTIFICATION_BAR_HEIGHT=24
BUTTON_WIDTH=100
BUTTON_HEIGHT=40
PADDING_TINY=5
PADDING_SMALL=10
PADDING_MEDIUM=20
PADDING_LARGE=40
DRAWER_ANIM_DURATION=300
SLIDER_MIN_VALUE=1
SLIDER_MAX_VALUE=100
SLIDER_DEFAULT_VALUE=100

CLOCK_UPDATE_INTERVAL = 100 # 10 or even 1 ms doesn't seem to change the framerate but 100ms is enough
WIFI_ICON_UPDATE_INTERVAL = 1500
TEMPERATURE_UPDATE_INTERVAL = 2000
MEMFREE_UPDATE_INTERVAL = 5000 # not too frequent because there's a forced gc.collect() to give it a reliable value

# Color palette
DARKPINK = lv.color_hex(0xEC048C)
MEDIUMPINK = lv.color_hex(0xF480C5)
LIGHTPINK = lv.color_hex(0xF9E9F2)
DARKYELLOW = lv.color_hex(0xFBDC05)
LIGHTYELLOW = lv.color_hex(0xFBE499)
PUREBLACK = lv.color_hex(0x000000)

COLOR_DRAWER_BG=MEDIUMPINK
COLOR_TEXT_WHITE=LIGHTPINK
COLOR_NOTIF_BAR_BG = DARKPINK
COLOR_DRAWER_BUTTON_BG=DARKYELLOW
COLOR_DRAWER_BUTTONTEXT=PUREBLACK
COLOR_SLIDER_BG=LIGHTPINK
COLOR_SLIDER_KNOB=DARKYELLOW
COLOR_SLIDER_INDICATOR=LIGHTPINK



drawer=None
wifi_screen=None
drawer_open=False


rootscreen = lv.screen_active()
rootscreen.set_style_bg_color(lv.color_hex(0x444444), 0)
rootlabel = lv.label(rootscreen)
rootlabel.set_text("Welcome to PiggyOS!")
rootlabel.align(lv.ALIGN.CENTER, 0, 0)

def open_drawer():
    global drawer_open
    if not drawer_open:
        drawer_open=True
        drawer.set_y(0)

def close_drawer():
    global drawer_open
    if drawer_open:
        drawer_open=False
        drawer.set_y(-TFT_VER_RES)

def toggle_drawer(event):
	global drawer_open
	if drawer_open:
		close_drawer()
	else:
		open_drawer()

def add_notification_bar(screen):
    # Create notification bar object
    notification_bar = lv.obj(screen)
    notification_bar.set_style_bg_color(COLOR_NOTIF_BAR_BG, 0)
    notification_bar.set_size(320, NOTIFICATION_BAR_HEIGHT)
    notification_bar.set_pos(0, 0)
    notification_bar.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
    notification_bar.set_scroll_dir(lv.DIR.VER)
    notification_bar.set_style_border_width(0, 0)
    notification_bar.set_style_radius(0, 0)
    # Time label
    time_label = lv.label(notification_bar)
    time_label.set_text("00:00:00.000")
    time_label.align(lv.ALIGN.LEFT_MID, 0, 0)
    time_label.set_style_text_color(COLOR_TEXT_WHITE, 0)
    temp_label = lv.label(notification_bar)
    temp_label.set_text("00°C")
    temp_label.align_to(time_label, lv.ALIGN.OUT_RIGHT_MID, PADDING_TINY, 0)
    temp_label.set_style_text_color(COLOR_TEXT_WHITE, 0)
    memfree_label = lv.label(notification_bar)
    memfree_label.set_text("")
    memfree_label.align_to(temp_label, lv.ALIGN.OUT_RIGHT_MID, PADDING_TINY, 0)
    memfree_label.set_style_text_color(COLOR_TEXT_WHITE, 0)
    #style = lv.style_t()
    #style.init()
    #style.set_text_font(lv.font_montserrat_8)  # tiny font
    #memfree_label.add_style(style, 0)
    # Notification icon (bell)
    #notif_icon = lv.label(notification_bar)
    #notif_icon.set_text(lv.SYMBOL.BELL)
    #notif_icon.align_to(time_label, lv.ALIGN.OUT_RIGHT_MID, PADDING_TINY, 0)
    #notif_icon.set_style_text_color(COLOR_TEXT_WHITE, 0)
    # Battery icon
    battery_icon = lv.label(notification_bar)
    battery_icon.set_text(lv.SYMBOL.BATTERY_FULL)
    battery_icon.align(lv.ALIGN.RIGHT_MID, -PADDING_TINY, 0)
    battery_icon.set_style_text_color(COLOR_TEXT_WHITE, 0)
    # WiFi icon
    wifi_icon = lv.label(notification_bar)
    wifi_icon.set_text(lv.SYMBOL.WIFI)
    wifi_icon.align_to(battery_icon, lv.ALIGN.OUT_LEFT_MID, -PADDING_TINY, 0)
    wifi_icon.set_style_text_color(COLOR_TEXT_WHITE, 0)
    wifi_icon.add_flag(lv.obj.FLAG.HIDDEN)
    # Battery percentage - not shown to conserve space
    #battery_label = lv.label(notification_bar)
    #battery_label.set_text("100%")
    #battery_label.align(lv.ALIGN.RIGHT_MID, 0, 0)
    #battery_label.set_style_text_color(COLOR_TEXT_WHITE, 0)
    # Update time
    import time
    def update_time(timer):
        ticks = time.ticks_ms()
        hours = (ticks // 3600000) % 24
        minutes = (ticks // 60000) % 60
        seconds = (ticks // 1000) % 60
        milliseconds = ticks % 1000
        time_label.set_text(f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}")
    import network
    def update_wifi_icon(timer):
        try:
            if network.WLAN(network.STA_IF).isconnected():
                wifi_icon.remove_flag(lv.obj.FLAG.HIDDEN)
            else:
                wifi_icon.add_flag(lv.obj.FLAG.HIDDEN)
        except lv.LvReferenceError:
            print("update_wifi_icon caught LvReferenceError")
    import esp32
    def update_temperature(timer):
        temp_label.set_text(f"{esp32.mcu_temperature()}°C")
    import gc
    def update_memfree(timer):
        gc.collect()
        memfree_label.set_text(f"{gc.mem_free()}")
    timer1 = lv.timer_create(update_time, CLOCK_UPDATE_INTERVAL, None)
    timer2 = lv.timer_create(update_temperature, TEMPERATURE_UPDATE_INTERVAL, None)
    timer3 = lv.timer_create(update_memfree, MEMFREE_UPDATE_INTERVAL, None)
    timer4 = lv.timer_create(update_wifi_icon, WIFI_ICON_UPDATE_INTERVAL, None)
    notification_bar.add_event_cb(toggle_drawer, lv.EVENT.CLICKED, None)
    return timer1, timer2, timer3, timer4


drawer=lv.obj(lv.layer_top())
drawer.set_size(lv.pct(100),lv.pct(100))
drawer.set_pos(0,-TFT_VER_RES) # off screen initially
drawer.set_style_bg_color(COLOR_DRAWER_BG,0)
drawer.set_scroll_dir(lv.DIR.NONE)
drawer.set_style_pad_all(0, 0)
add_notification_bar(drawer)
slider_label=lv.label(drawer)
slider_label.set_text(f"{SLIDER_DEFAULT_VALUE}%")
slider_label.set_style_text_color(COLOR_TEXT_WHITE,0)
slider_label.align(lv.ALIGN.TOP_MID,0,NOTIFICATION_BAR_HEIGHT+PADDING_SMALL)
slider=lv.slider(drawer)
slider.set_range(SLIDER_MIN_VALUE,SLIDER_MAX_VALUE)
slider.set_value(SLIDER_DEFAULT_VALUE,False)
slider.set_width(TFT_HOR_RES-PADDING_LARGE)
slider.align_to(slider_label,lv.ALIGN.OUT_BOTTOM_MID,0,PADDING_SMALL)
slider.set_style_bg_color(COLOR_SLIDER_BG,lv.PART.MAIN)
slider.set_style_bg_color(COLOR_SLIDER_INDICATOR,lv.PART.INDICATOR)
slider.set_style_bg_color(COLOR_SLIDER_KNOB,lv.PART.KNOB)
def slider_event(e):
    value=slider.get_value()
    slider_label.set_text(f"{value}%")
    display.set_backlight(value)

slider.add_event_cb(slider_event,lv.EVENT.VALUE_CHANGED,None)
wifi_btn=lv.button(drawer)
wifi_btn.set_size(BUTTON_WIDTH,BUTTON_HEIGHT)
wifi_btn.align(lv.ALIGN.LEFT_MID,PADDING_MEDIUM,0)
wifi_btn.set_style_bg_color(COLOR_DRAWER_BUTTON_BG,0)
wifi_label=lv.label(wifi_btn)
wifi_label.set_text(lv.SYMBOL.WIFI+" WiFi")
wifi_label.center()
wifi_label.set_style_text_color(COLOR_DRAWER_BUTTONTEXT,0)
def wifi_event(e):
    global drawer_open
    #wifi_screen.set_y(0) # TODO: make this
    close_drawer()

wifi_btn.add_event_cb(wifi_event,lv.EVENT.CLICKED,None)
#
settings_btn=lv.button(drawer)
settings_btn.set_size(BUTTON_WIDTH,BUTTON_HEIGHT)
settings_btn.align(lv.ALIGN.RIGHT_MID,-PADDING_MEDIUM,0)
settings_btn.set_style_bg_color(COLOR_DRAWER_BUTTON_BG,0)
settings_label=lv.label(settings_btn)
settings_label.set_text(lv.SYMBOL.SETTINGS+" Settings")
settings_label.center()
settings_label.set_style_text_color(COLOR_DRAWER_BUTTONTEXT,0)
def settings_event(e):
    global drawer_open
    close_drawer()

settings_btn.add_event_cb(settings_event,lv.EVENT.CLICKED,None)
#
launcher_btn=lv.button(drawer)
launcher_btn.set_size(BUTTON_WIDTH,BUTTON_HEIGHT)
launcher_btn.align(lv.ALIGN.BOTTOM_LEFT,PADDING_MEDIUM,-PADDING_MEDIUM)
launcher_btn.set_style_bg_color(COLOR_DRAWER_BUTTON_BG,0)
launcher_label=lv.label(launcher_btn)
launcher_label.set_text(lv.SYMBOL.HOME+" Launcher")
launcher_label.center()
launcher_label.set_style_text_color(COLOR_DRAWER_BUTTONTEXT,0)
def launcher_event(e):
    print("Launcher button pressed!")
    global drawer_open
    close_drawer()
    lv.screen_load(rootscreen)

launcher_btn.add_event_cb(launcher_event,lv.EVENT.CLICKED,None)
#
restart_btn=lv.button(drawer)
restart_btn.set_size(BUTTON_WIDTH,BUTTON_HEIGHT)
restart_btn.align(lv.ALIGN.BOTTOM_RIGHT,-PADDING_MEDIUM,-PADDING_MEDIUM)
restart_btn.set_style_bg_color(COLOR_DRAWER_BUTTON_BG,0)
restart_label=lv.label(restart_btn)
restart_label.set_text(lv.SYMBOL.POWER+" Reset")
restart_label.center()
restart_label.set_style_text_color(COLOR_DRAWER_BUTTONTEXT,0)
restart_btn.add_event_cb(lambda event: machine.reset(),lv.EVENT.CLICKED,None)










import _thread
import traceback
import uio
import time

def parse_manifest(manifest_path):
    name = "Unknown"
    start_script = "assets/start.py"
    try:
        with uio.open(manifest_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith("Name:"):
                    name = line.split(":", 1)[1].strip()
                elif line.startswith("Start-Script:"):
                    start_script = line.split(":", 1)[1].strip()
    except OSError:
        print(f"Error reading {manifest_path}")
    return name, start_script

def long_path_to_filename(path):
    try:
        if not path or not isinstance(path, str):
            return None
        # Extract filename using rsplit and take the last part
        filename = path.rsplit('/', 1)[-1]
        # Limit to the first 7 characters
        return filename[:7]
    except Exception as e:
        print(f"Error extracting filename: {str(e)}")
        return None

# Run the script in the current thread:
def execute_script(script_source, is_file, is_launcher, is_graphical):
    thread_id = _thread.get_ident()
    print(f"Thread {thread_id}: executing script")
    try:
        if is_file:
            print(f"Thread {thread_id}: reading script from file {script_source}")
            with open(script_source, 'r') as f: # TODO: check if file exists first?
                script_source = f.read()
        if not is_graphical:
            script_globals = {
                '__name__': "__main__"
            }
        else: # is_graphical
            if is_launcher:
                prevscreen = None
                newscreen = rootscreen
            else:
                prevscreen = lv.screen_active()
                newscreen=lv.obj()
                newscreen.set_size(lv.pct(100),lv.pct(100))
            timer1, timer2, timer3, timer4 = add_notification_bar(newscreen)
            subwindow = lv.obj(newscreen)
            subwindow.set_size(TFT_HOR_RES, TFT_VER_RES - NOTIFICATION_BAR_HEIGHT)
            subwindow.set_pos(0, NOTIFICATION_BAR_HEIGHT)
            subwindow.set_style_border_width(0, 0)
            subwindow.set_style_pad_all(0, 0)
            lv.screen_load(newscreen)
            script_globals = {
                'lv': lv,
                'appscreen': newscreen,
                'subwindow': subwindow,
                'start_app': start_app, # for launcher apps
                'parse_manifest': parse_manifest, # for launcher apps
                '__name__': "__main__"
            }
        print(f"Thread {thread_id}: starting script")
        try:
            compile_name = 'script' if not is_file else long_path_to_filename(script_source) # Only filename, to avoid 'name too long' error
            compiled_script = compile(script_source, compile_name, 'exec')
            exec(compiled_script, script_globals)
        except Exception as e:
            print(f"Thread {thread_id}: exception during execution:")
            # Print stack trace with exception type, value, and traceback
            tb = getattr(e, '__traceback__', None)
            traceback.print_exception(type(e), e, tb)
        print(f"Thread {thread_id}: script {compile_name} finished")
        if is_graphical and not is_launcher:
            print("/main.py: execute_script(): cleaning subwindow...")
            timer1.delete()
            timer2.delete()
            timer3.delete()
            timer4.delete()
            newscreen.delete() #still runs into timer errors, even though these timers have been deleted...
            print(f"Thread {thread_id}: finished, prevscreen is set and it's not a launcher so returning to previous screen...")
            lv.screen_load(prevscreen)
    except Exception as e:
        print(f"Thread {thread_id}: error:")
        tb = getattr(e, '__traceback__', None)
        traceback.print_exception(type(e), e, tb)

# Run the script in a new thread:
def execute_script_new_thread(scriptname, is_file, is_launcher, is_graphical):
    print(f"/main.py: execute_script_new_thread({scriptname},{is_file},{is_launcher})")
    try:
        # 168KB maximum at startup but 136KB after loading display, drivers, LVGL gui etc so let's go for 128KB for now, still a lot...
        # But then no additional threads can be created. A stacksize of 32KB allows for 4 threads, so 3 in the app itself, which might be tight.
        _thread.stack_size(16384) # A stack size of 16KB allows for around 10 threads in the app, which should be plenty.
        _thread.start_new_thread(execute_script, (scriptname, is_file, is_launcher, is_graphical))
    except Exception as e:
        print("/main.py: execute_script_new_thread(): error starting new thread thread: ", e)

def start_app(app_dir, is_launcher=False):
    print(f"/main.py start_app({app_dir},{is_launcher}")
    manifest_path = f"{app_dir}/META-INF/MANIFEST.MF"
    app_name, start_script = parse_manifest(manifest_path)
    start_script_fullpath = f"{app_dir}/{start_script}"
    execute_script_new_thread(start_script_fullpath, True, is_launcher, True)

def run_launcher():
    start_app("/apps/com.example.launcher", True)

execute_script_new_thread("/autorun.py", True, False, False)
run_launcher()

# If we got this far without crashing, then no need to rollback the update
import ota.rollback
ota.rollback.cancel()
