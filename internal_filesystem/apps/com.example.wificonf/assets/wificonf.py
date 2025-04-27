import network
import ujson
import os
import time
import lvgl as lv

wlan=network.WLAN(network.STA_IF)
wlan.active(True)
access_points={}
selected_ssid=None
list=None
password_ta=None
password_page=None
main_subwindow=None
keyboard=None
error_label=None
scanning_label=None
connect_button=None
cancel_button=None
back_button=None

def load_config():
    print("load_config: Checking for /data directory")
    try:
        os.stat('/data')
        print("load_config: /data exists")
    except OSError:
        print("load_config: Creating /data directory")
        os.mkdir('/data')
    print("load_config: Checking for /data/com.example.wificonf directory")
    try:
        os.stat('/data/com.example.wificonf')
        print("load_config: /data/com.example.wificonf exists")
    except OSError:
        print("load_config: Creating /data/com.example.wificonf directory")
        os.mkdir('/data/com.example.wificonf')
    print("load_config: Loading config from conf.json")
    try:
        with open('/data/com.example.wificonf/conf.json','r') as f:
            global access_points
            access_points=ujson.load(f)
            print(f"load_config: Loaded access_points: {access_points}")
    except OSError:
        access_points={}
        print("load_config: No config file found, using empty access_points")

def save_config():
    print("save_config: Saving access_points to conf.json")
    try:
        with open('/data/com.example.wificonf/conf.json','w') as f:
            ujson.dump(access_points,f)
        print(f"save_config: Saved access_points: {access_points}")
    except OSError:
        show_error("Failed to save config")
        print("save_config: Failed to save config")

def scan_networks():
    print("scan_networks: Showing scanning label")
    scanning_label.set_text("Scanning...")
    scanning_label.set_hidden(False)
    lv.task_handler()
    print("scan_networks: Scanning for Wi-Fi networks")
    try:
        networks=wlan.scan()
        ssids=[n[0].decode() for n in networks]
        print(f"scan_networks: Found networks: {ssids}")
        scanning_label.set_hidden(True)
        return ssids
    except Exception as e:
        print(f"scan_networks: Scan failed: {e}")
        show_error("Wi-Fi scan failed")
        scanning_label.set_hidden(True)
        return []

def attempt_connecting(ssid,password):
    print(f"attempt_connecting: Attempting to connect to SSID: {ssid}")
    try:
        wlan.connect(ssid,password)
        for i in range(10):
            if wlan.isconnected():
                print(f"attempt_connecting: Connected to {ssid} after {i+1} seconds")
                return True
            print(f"attempt_connecting: Waiting for connection, attempt {i+1}/10")
            time.sleep(1)
        print(f"attempt_connecting: Failed to connect to {ssid}")
        return False
    except Exception as e:
        print(f"attempt_connecting: Connection error: {e}")
        show_error("Connection failed")
        return False

def auto_connect():
    print("auto_connect: Attempting to connect to known networks")
    for ssid,password in access_points.items():
        print(f"auto_connect: Trying SSID: {ssid}")
        if attempt_connecting(ssid,password):
            print(f"auto_connect: Connected to {ssid}")
            return True
    print("auto_connect: No known networks connected")
    return False

def show_error(message):
    print(f"show_error: Displaying error: {message}")
    global error_label
    error_label.set_text(message)
    error_label.set_hidden(False)
    timer=lv.timer_create(lambda t: error_label.set_hidden(True),3000,None)
    timer.set_repeat_count(1)

def refresh_list():
    print("refresh_list: Clearing current list")
    list.clean()
    print("refresh_list: Populating list with scanned networks")
    for ssid in scan_networks():
        print(f"refresh_list: Adding SSID: {ssid}")
        button=list.add_button(None,ssid)
        button.add_event_cb(lambda e, s=ssid: select_ssid_cb(e,s),lv.EVENT.CLICKED,None)
        status="connected" if wlan.isconnected() and wlan.config('essid')==ssid else "failed" if ssid in access_points else ""
        if status:
            print(f"refresh_list: Setting status '{status}' for SSID: {ssid}")
            label=lv.label(button)
            label.set_text(status)
            label.align(lv.ALIGN.RIGHT_MID,-10,0)

def scan_cb(event):
    print("scan_cb: Scan button clicked, refreshing list")
    refresh_list()

def select_ssid_cb(event,ssid):
    global selected_ssid
    print(f"select_ssid_cb: SSID selected: {ssid}")
    selected_ssid=ssid
    show_password_page()

def keyboard_cb(event):
    print("keyboard_cb: Keyboard event triggered")
    global keyboard,connect_button,cancel_button,back_button
    code=event.get_code()
    if code==lv.EVENT.READY:
        print("keyboard_cb: OK/Checkmark clicked, hiding keyboard")
        keyboard.set_height(0)
        keyboard.clear_flag(lv.obj.FLAG_CLICKABLE)
        print("keyboard_cb: Showing Connect, Cancel, and Back buttons")
        connect_button.set_hidden(False)
        cancel_button.set_hidden(False)
        back_button.set_hidden(False)

def password_ta_cb(event):
    print("password_ta_cb: Password textarea clicked")
    global keyboard,connect_button,cancel_button,back_button
    print("password_ta_cb: Hiding Connect, Cancel, and Back buttons")
    connect_button.set_hidden(True)
    cancel_button.set_hidden(True)
    back_button.set_hidden(True)
    print("password_ta_cb: Showing keyboard")
    keyboard.set_height(80)
    keyboard.add_flag(lv.obj.FLAG_CLICKABLE)

def toggle_password_cb(event):
    print("toggle_password_cb: Password visibility toggle clicked")
    global password_ta
    checkbox=event.get_target()
    password_ta.set_password_mode(not checkbox.get_state())

def show_password_page():
    global password_page,password_ta,keyboard,connect_button,cancel_button,back_button
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
    password_ta.align(lv.ALIGN.CENTER,0,-30)
    password_ta.set_placeholder_text("Password")
    password_ta.set_password_mode(True)
    password_ta.add_event_cb(password_ta_cb,lv.EVENT.CLICKED,None)
    print("show_password_page: Creating show password checkbox")
    checkbox=lv.checkbox(password_page)
    checkbox.set_text("Show password")
    checkbox.align(lv.ALIGN.CENTER,0,0)
    checkbox.add_event_cb(toggle_password_cb,lv.EVENT.VALUE_CHANGED,None)
    print("show_password_page: Creating keyboard (hidden by default)")
    keyboard=lv.keyboard(password_page)
    keyboard.set_size(lv.pct(100),0)
    keyboard.align(lv.ALIGN.BOTTOM_LEFT,0,0)
    keyboard.set_textarea(password_ta)
    keyboard.add_event_cb(keyboard_cb,lv.EVENT.READY,None)
    print("show_password_page: Creating Connect button")
    connect_button=lv.button(password_page)
    connect_button.set_size(80,30)
    connect_button.align(lv.ALIGN.BOTTOM_LEFT,10,-40)
    label=lv.label(connect_button)
    label.set_text("Connect")
    connect_button.add_event_cb(connect_cb,lv.EVENT.CLICKED,None)
    print("show_password_page: Creating Cancel button")
    cancel_button=lv.button(password_page)
    cancel_button.set_size(80,30)
    cancel_button.align(lv.ALIGN.BOTTOM_RIGHT,-10,-40)
    label=lv.label(cancel_button)
    label.set_text("Cancel")
    cancel_button.add_event_cb(cancel_cb,lv.EVENT.CLICKED,None)
    print("show_password_page: Creating Back button")
    back_button=lv.button(password_page)
    back_button.set_size(80,30)
    back_button.align(lv.ALIGN.BOTTOM_MID,0,-40)
    label=lv.label(back_button)
    label.set_text("Back")
    back_button.add_event_cb(cancel_cb,lv.EVENT.CLICKED,None)
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
    print("connect_cb: Restoring main subwindow")
    lv.screen_load(main_subwindow)
    print(f"connect_cb: Attempting connection to {selected_ssid}")
    success=attempt_connecting(selected_ssid,password)
    print(f"connect_cb: Connection {'succeeded' if success else 'failed'}")
    refresh_list()

def cancel_cb(event):
    print("cancel_cb: Cancel/Back button clicked, deleting password page")
    password_page.delete()
    print("cancel_cb: Restoring main subwindow")
    lv.screen_load(main_subwindow)

def create_ui(subwindow):
    global list,main_subwindow,error_label,scanning_label
    main_subwindow=subwindow
    print("create_ui: Creating list widget")
    list=lv.list(subwindow)
    list.set_size(240,180)
    list.align(lv.ALIGN.CENTER,0,-10)
    print("create_ui: Creating error label")
    error_label=lv.label(subwindow)
    error_label.set_text("")
    error_label.align(lv.ALIGN.BOTTOM_MID,0,-40)
    error_label.set_hidden(True)
    print("create_ui: Creating scanning label")
    scanning_label=lv.label(subwindow)
    scanning_label.set_text("Scanning...")
    scanning_label.align(lv.ALIGN.CENTER,0,0)
    scanning_label.set_hidden(True)
    print("create_ui: Creating Scan button")
    scan_button=lv.button(subwindow)
    scan_button.set_size(80,30)
    scan_button.align(lv.ALIGN.BOTTOM_MID,0,-5)
    label=lv.label(scan_button)
    label.set_text("Scan")
    scan_button.add_event_cb(scan_cb,lv.EVENT.CLICKED,None)
    print("create_ui: Attempting auto-connect")
    auto_connect()
    print("create_ui: Refreshing list with initial scan")
    refresh_list()
    print("create_ui: Loading config")
    load_config()


subwindow.clean()
create_ui(subwindow)
