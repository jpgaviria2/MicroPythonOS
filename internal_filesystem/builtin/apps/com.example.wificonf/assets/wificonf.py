import ujson
import os
import time
import lvgl as lv
import _thread

# Screens:
appscreen = lv.screen_active()
password_page=None

ssids=[]
busy_scanning=False
busy_connecting=False
access_points={}
selected_ssid=None
aplist=None
password_ta=None
keyboard=None
error_label=None
connect_button=None
cancel_button=None

last_tried_ssid = ""
last_tried_result = ""

scan_button=None
scan_button_label=None
scan_button_scan_text = "Rescan"
scan_button_scanning_text = "Scanning..."

def load_config():
    print("load_config: Checking for /data directory")
    try:
        os.stat('data')
        print("load_config: /data exists")
    except OSError:
        print("load_config: Creating /data directory")
        os.mkdir('data')
    print("load_config: Checking for /data/com.example.wificonf directory")
    try:
        os.stat('data/com.example.wificonf')
        print("load_config: /data/com.example.wificonf exists")
    except OSError:
        print("load_config: Creating /data/com.example.wificonf directory")
        os.mkdir('data/com.example.wificonf')
    print("load_config: Loading config from conf.json")
    try:
        with open('data/com.example.wificonf/conf.json','r') as f:
            global access_points
            access_points=ujson.load(f)
            print(f"load_config: Loaded access_points: {access_points}")
    except OSError:
        access_points={}
        print("load_config: No config file found, using empty access_points")

def save_config():
    print("save_config: Saving access_points to conf.json")
    try:
        with open('data/com.example.wificonf/conf.json','w') as f:
            ujson.dump(access_points,f)
        print(f"save_config: Saved access_points: {access_points}")
    except OSError:
        show_error("Failed to save config")
        print("save_config: Failed to save config")


def scan_networks_thread():
    print("scan_networks: Scanning for Wi-Fi networks")
    global ssids, busy_scanning, scan_button_label, scan_button
    if havenetwork and not wlan.isconnected(): # restart WiFi hardware in case it's in a bad state
        wlan.active(False)
        wlan.active(True)
    try:
        if havenetwork:
            networks = wlan.scan()
            ssids = list(set(n[0].decode() for n in networks))
        else:
            time.sleep(2)
            ssids = ["Dummy", "Test", "SSIDs"]
        print(f"scan_networks: Found networks: {ssids}")
    except Exception as e:
        print(f"scan_networks: Scan failed: {e}")
        show_error("Wi-Fi scan failed")
    # scan done:
    busy_scanning = False
    lv.async_call(lambda l: scan_button_label.set_text(scan_button_scan_text), None)
    lv.async_call(lambda l: scan_button.add_flag(lv.obj.FLAG.CLICKABLE), None)
    lv.async_call(lambda l: refresh_list(), None)


def start_scan_networks():
    print("scan_networks: Showing scanning label")
    global scan_button_label, busy_scanning, scan_button
    if busy_scanning:
        print("Not scanning for networks because already busy_scanning.")
    else:
        busy_scanning = True
        scan_button.remove_flag(lv.obj.FLAG.CLICKABLE)
        scan_button_label.set_text(scan_button_scanning_text)
        _thread.stack_size(12*1024)
        _thread.start_new_thread(scan_networks_thread, ())


def attempt_connecting_thread(ssid,password):
    global busy_connecting, scan_button_label, scan_button, last_tried_ssid, last_tried_result
    print(f"attempt_connecting: Attempting to connect to SSID: {ssid}")
    result="connected"
    try:
        if havenetwork:
            wlan.disconnect()
            wlan.connect(ssid,password)
            for i in range(10):
                if wlan.isconnected():
                    print(f"attempt_connecting: Connected to {ssid} after {i+1} seconds")
                    break
                print(f"attempt_connecting: Waiting for connection, attempt {i+1}/10")
                time.sleep(1)
            if not wlan.isconnected():
                result="timeout"
        else:
            print("Warning: not trying to connect because not havenetwork")
    except Exception as e:
        print(f"attempt_connecting: Connection error: {e}")
        result=f"{e}"
        show_error("Connecting to {ssid} failed!")
    print(f"Connecting to {ssid} got result: {result}")
    last_tried_ssid = ssid
    last_tried_result = result
    busy_connecting=False
    # Schedule UI updates because different thread
    lv.async_call(lambda l: scan_button_label.set_text(scan_button_scan_text), None)
    lv.async_call(lambda l: scan_button.add_flag(lv.obj.FLAG.CLICKABLE), None)
    lv.async_call(lambda l: refresh_list(), None)


def start_attempt_connecting(ssid,password):
    print(f"start_attempt_connecting: Attempting to connect to SSID: {ssid}")
    global busy_connecting, scan_button_label, scan_button
    scan_button.remove_flag(lv.obj.FLAG.CLICKABLE)
    scan_button_label.set_text(f"Connecting to {ssid}...")
    if busy_connecting:
        print("Not attempting connect because busy_connecting.")
    else:
        busy_connecting = True
        _thread.stack_size(12*1024)
        _thread.start_new_thread(attempt_connecting_thread, (ssid,password))

def show_error(message):
    print(f"show_error: Displaying error: {message}")
    global error_label
    lv.async_call(lambda l: error_label.set_text(message), None)
    lv.async_call(lambda l: error_label.remove_flag(lv.obj.FLAG.HIDDEN), None)
    timer=lv.timer_create(lambda t: error_label.add_flag(lv.obj.FLAG.HIDDEN),3000,None)
    timer.set_repeat_count(1)

def refresh_list():
    global ssids
    print("refresh_list: Clearing current list")
    aplist.clean() # this causes an issue with lost taps if an ssid is clicked that has been removed
    print("refresh_list: Populating list with scanned networks")
    for ssid in ssids:
        if len(ssid) < 1 or len(ssid) > 32:
            print(f"Skipping too short or long SSID: {ssid}")
            continue
        print(f"refresh_list: Adding SSID: {ssid}")
        button=aplist.add_button(None,ssid)
        button.add_event_cb(lambda e, s=ssid: select_ssid_cb(e,s),lv.EVENT.CLICKED,None)
        if havenetwork and wlan.isconnected() and wlan.config('essid')==ssid:
            status="connected"
        elif last_tried_ssid==ssid: # implies not connected because not wlan.isconnected()
            status=last_tried_result
        elif ssid in access_points:
            status="saved"
        else:
            status=""
        if status:
            print(f"refresh_list: Setting status '{status}' for SSID: {ssid}")
            label=lv.label(button)
            label.set_text(status)
            label.align(lv.ALIGN.RIGHT_MID,-10,0)

def scan_cb(event):
    print("scan_cb: Scan button clicked, refreshing list")
    start_scan_networks()

def select_ssid_cb(event,ssid):
    global selected_ssid
    print(f"select_ssid_cb: SSID selected: {ssid}")
    selected_ssid=ssid
    show_password_page(ssid)

def hide_keyboard():
    global keyboard,connect_button,cancel_button
    print("keyboard_cb: READY or CANCEL or RETURN clicked, hiding keyboard")
    keyboard.set_height(0)
    #keyboard.remove_flag(lv.obj.FLAG.CLICKABLE)
    print("keyboard_cb: Showing Connect and Cancel buttons")
    connect_button.remove_flag(lv.obj.FLAG.HIDDEN)
    cancel_button.remove_flag(lv.obj.FLAG.HIDDEN)

def keyboard_cb(event):
    #print("keyboard_cb: Keyboard event triggered")
    code=event.get_code()
    if code==lv.EVENT.READY or code==lv.EVENT.CANCEL:
        hide_keyboard()

def keyboard_value_changed_cb(event):
    global keyboard
    #print("keyboard value changed!")
    #print(f"event: code={event.get_code()}, target={event.get_target()}, user_data={event.get_user_data()}, param={event.get_param()}") # event: code=32, target=<Blob>, user_data=<Blob>, param=<Blob>
    button = keyboard.get_selected_button()
    text = keyboard.get_button_text(button)
    #print(f"button {button} and text {text}")
    if text == lv.SYMBOL.NEW_LINE:
        print("Newline key pressed, hiding keyboard...")
        hide_keyboard()

def password_ta_cb(event):
    print("password_ta_cb: Password textarea clicked")
    global keyboard,connect_button,cancel_button
    print("password_ta_cb: Hiding Connect and Cancel buttons")
    connect_button.add_flag(lv.obj.FLAG.HIDDEN)
    cancel_button.add_flag(lv.obj.FLAG.HIDDEN)
    print("password_ta_cb: Showing keyboard")
    keyboard.set_height(160)
    #keyboard.add_flag(lv.obj.FLAG.CLICKABLE)

def show_password_page(ssid):
    global password_page,password_ta,keyboard,connect_button,cancel_button
    print("show_password_page: Creating new password page")
    password_page=lv.obj()
    password_page.set_size(lv.pct(100),lv.pct(100))
    print(f"show_password_page: Creating label for SSID: {selected_ssid}")
    label=lv.label(password_page)
    label.set_text(f"Enter password for {selected_ssid}")
    label.align(lv.ALIGN.TOP_MID,0,5)
    print("show_password_page: Creating password textarea")
    password_ta=lv.textarea(password_page)
    password_ta.set_size(200,30)
    password_ta.set_one_line(True)
    password_ta.align_to(label, lv.ALIGN.OUT_BOTTOM_MID, 5, 0)
    # try to find saved password:
    for apssid,password in access_points.items():
        if ssid == apssid:
            password_ta.set_text(password)
            break
    password_ta.set_placeholder_text("Password")
    password_ta.add_event_cb(password_ta_cb,lv.EVENT.CLICKED,None)
    print("show_password_page: Creating keyboard (hidden by default)")
    keyboard=lv.keyboard(password_page)
    keyboard.set_size(lv.pct(100),0)
    keyboard.align(lv.ALIGN.BOTTOM_LEFT,0,0)
    keyboard.set_textarea(password_ta)
    keyboard.add_event_cb(keyboard_cb,lv.EVENT.READY,None)
    keyboard.add_event_cb(keyboard_cb,lv.EVENT.CANCEL,None)
    keyboard.add_event_cb(keyboard_value_changed_cb,lv.EVENT.VALUE_CHANGED,None)
    print("show_password_page: Creating Connect button")
    connect_button=lv.button(password_page)
    connect_button.set_size(100,40)
    connect_button.align(lv.ALIGN.BOTTOM_LEFT,10,-40)
    label=lv.label(connect_button)
    label.set_text("Connect")
    label.center()
    connect_button.add_event_cb(connect_cb,lv.EVENT.CLICKED,None)
    print("show_password_page: Creating Cancel button")
    cancel_button=lv.button(password_page)
    cancel_button.set_size(100,40)
    cancel_button.align(lv.ALIGN.BOTTOM_RIGHT,-10,-40)
    label=lv.label(cancel_button)
    label.set_text("Close")
    label.center()
    cancel_button.add_event_cb(cancel_cb,lv.EVENT.CLICKED,None)
    print("show_password_page: Loading password page")
    lv.screen_load(password_page)

def connect_cb(event):
    global access_points
    print("connect_cb: Connect button clicked")
    password=password_ta.get_text()
    print(f"connect_cb: Got password: {password}")
    access_points[selected_ssid]=password
    print(f"connect_cb: Updated access_points: {access_points}")
    save_config()
    print("connect_cb: Deleting password page")
    password_page.delete()
    print("connect_cb: Restoring main appscreen")
    lv.screen_load(appscreen)
    print(f"connect_cb: Attempting connection to {selected_ssid}")
    start_attempt_connecting(selected_ssid,password)

def cancel_cb(event):
    print("cancel_cb: Cancel button clicked")
    print("Deleting password screen...")
    password_page.delete()
    print("cancel_cb: Restoring main appscreen")
    lv.screen_load(appscreen)

def create_ui():
    global aplist,appscreen,error_label,scan_button_label,scan_button
    print("create_ui: Creating list widget")
    aplist=lv.list(appscreen)
    aplist.set_size(lv.pct(100),lv.pct(80))
    aplist.align(lv.ALIGN.TOP_MID,0,0)
    print("create_ui: Creating error label")
    error_label=lv.label(appscreen)
    error_label.set_text("")
    error_label.align(lv.ALIGN.BOTTOM_MID,0,-40)
    error_label.add_flag(lv.obj.FLAG.HIDDEN)
    print("create_ui: Creating Scan button")
    scan_button=lv.button(appscreen)
    scan_button.set_size(lv.SIZE_CONTENT,lv.pct(15))
    scan_button.align(lv.ALIGN.BOTTOM_MID,0,-5)
    scan_button_label=lv.label(scan_button)
    scan_button_label.set_text(scan_button_scan_text)
    scan_button_label.center()
    scan_button.add_event_cb(scan_cb,lv.EVENT.CLICKED,None)



havenetwork = True
try:
    import network
    wlan=network.WLAN(network.STA_IF)
    wlan.active(True)
except Exception as e:
    havenetwork = False

load_config()
create_ui()
start_scan_networks()

