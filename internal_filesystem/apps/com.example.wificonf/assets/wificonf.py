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
popup=None

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
    with open('/data/com.example.wificonf/conf.json','w') as f:
        ujson.dump(access_points,f)
    print(f"save_config: Saved access_points: {access_points}")

def scan_networks():
    print("scan_networks: Scanning for Wi-Fi networks")
    networks=wlan.scan()
    ssids=[n[0].decode() for n in networks]
    print(f"scan_networks: Found networks: {ssids}")
    return ssids

def attempt_connecting(ssid,password):
    print(f"attempt_connecting: Attempting to connect to SSID: {ssid}")
    wlan.connect(ssid,password)
    for i in range(10):
        if wlan.isconnected():
            print(f"attempt_connecting: Connected to {ssid} after {i+1} seconds")
            return True
        print(f"attempt_connecting: Waiting for connection, attempt {i+1}/10")
        time.sleep(1)
    print(f"attempt_connecting: Failed to connect to {ssid}")
    return False

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
    show_password_popup()

def show_password_popup():
    global popup,password_ta
    print("show_password_popup: Creating password popup")
    popup=lv.obj(subwindow)
    popup.set_size(260,200)
    popup.center()
    popup.add_flag(lv.obj.FLAG.CLICKABLE)
    print(f"show_password_popup: Creating label for SSID: {selected_ssid}")
    label=lv.label(popup)
    label.set_text(f"Enter password for {selected_ssid}")
    label.align(lv.ALIGN.TOP_MID,0,10)
    print("show_password_popup: Creating password textarea")
    password_ta=lv.textarea(popup)
    password_ta.set_size(220,40)
    password_ta.align(lv.ALIGN.CENTER,0,-20)
    password_ta.set_placeholder_text("Password")
    print("show_password_popup: Creating keyboard")
    keyboard=lv.keyboard(popup)
    keyboard.set_size(260,100)
    keyboard.align(lv.ALIGN.BOTTOM_MID,0,0)
    keyboard.set_textarea(password_ta)
    print("show_password_popup: Creating Connect button")
    connect_button=lv.button(popup)
    connect_button.set_size(100,40)
    connect_button.align(lv.ALIGN.BOTTOM_LEFT,10,-50)
    label=lv.label(connect_button)
    label.set_text("Connect")
    connect_button.add_event_cb(connect_cb,lv.EVENT.CLICKED,None)
    print("show_password_popup: Creating Cancel button")
    cancel_button=lv.button(popup)
    cancel_button.set_size(100,40)
    cancel_button.align(lv.ALIGN.BOTTOM_RIGHT,-10,-50)
    label=lv.label(cancel_button)
    label.set_text("Cancel")
    cancel_button.add_event_cb(cancel_cb,lv.EVENT.CLICKED,None)

def connect_cb(event):
    global access_points
    print("connect_cb: Connect button clicked")
    password=password_ta.get_text()
    print(f"connect_cb: Got password: {password}")
    access_points[selected_ssid]=password
    print(f"connect_cb: Updated access_points: {access_points}")
    save_config()
    print("connect_cb: Deleting popup")
    popup.delete()
    print(f"connect_cb: Attempting connection to {selected_ssid}")
    success=attempt_connecting(selected_ssid,password)
    print(f"connect_cb: Connection {'succeeded' if success else 'failed'}")
    refresh_list()

def cancel_cb(event):
    print("cancel_cb: Cancel button clicked, deleting popup")
    popup.delete()

def create_ui(subwindow):
    global list
    print("create_ui: Creating list widget")
    list=lv.list(subwindow)
    list.set_size(280,300)
    list.center()
    print("create_ui: Refreshing list with initial scan")
    refresh_list()
    print("create_ui: Creating Scan button")
    scan_button=lv.button(subwindow)
    scan_button.set_size(100,40)
    scan_button.align(lv.ALIGN.TOP_MID,0,10)
    label=lv.label(scan_button)
    label.set_text("Scan")
    scan_button.add_event_cb(scan_cb,lv.EVENT.CLICKED,None)
    print("create_ui: Loading config")
    load_config()


subwindow.clean()
create_ui(subwindow)
