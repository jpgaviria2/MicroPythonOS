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
    try:
        os.stat('/data')
    except OSError:
        os.mkdir('/data')
    try:
        os.stat('/data/com.example.wificonf')
    except OSError:
        os.mkdir('/data/com.example.wificonf')
    try:
        with open('/data/com.example.wificonf/conf.json','r') as f:
            global access_points
            access_points=ujson.load(f)
    except OSError:
        access_points={}

def save_config():
    with open('/data/com.example.wificonf/conf.json','w') as f:
        ujson.dump(access_points,f)

def scan_networks():
    networks=wlan.scan()
    return [n[0].decode() for n in networks]

def attempt_connecting(ssid,password):
    wlan.connect(ssid,password)
    for _ in range(10):
        if wlan.isconnected():
            return True
        time.sleep(1)
    return False

def refresh_list():
    list.clean()
    for ssid in scan_networks():
        button=list.add_button(None,ssid)
        button.add_event_cb(lambda e, s=ssid: select_ssid_cb(e,s),lv.EVENT.CLICKED,None)
        status="connected" if wlan.isconnected() and wlan.config('essid')==ssid else "failed" if ssid in access_points else ""
        if status:
            label=lv.label(button)
            label.set_text(status)
            label.align(lv.ALIGN.RIGHT_MID,-10,0)

def scan_cb(event):
    refresh_list()

def select_ssid_cb(event,ssid):
    global selected_ssid
    selected_ssid=ssid
    show_password_popup()

def show_password_popup():
    global popup,password_ta
    popup=lv.obj(subwindow)
    popup.set_size(260,200)
    popup.center()
    popup.add_flag(lv.obj.FLAG.CLICKABLE)
    label=lv.label(popup)
    label.set_text(f"Enter password for {selected_ssid}")
    label.align(lv.ALIGN.TOP_MID,0,10)
    password_ta=lv.textarea(popup)
    password_ta.set_size(220,40)
    password_ta.align(lv.ALIGN.CENTER,0,-20)
    password_ta.set_placeholder_text("Password")
    keyboard=lv.keyboard(popup)
    keyboard.set_size(260,100)
    keyboard.align(lv.ALIGN.BOTTOM_MID,0,0)
    keyboard.set_textarea(password_ta)
    connect_button=lv.button(popup)
    connect_button.set_size(100,40)
    connect_button.align(lv.ALIGN.BOTTOM_LEFT,10,-50)
    label=lv.label(connect_button)
    label.set_text("Connect")
    connect_button.add_event_cb(connect_cb,lv.EVENT.CLICKED,None)
    cancel_button=lv.button(popup)
    cancel_button.set_size(100,40)
    cancel_button.align(lv.ALIGN.BOTTOM_RIGHT,-10,-50)
    label=lv.label(cancel_button)
    label.set_text("Cancel")
    cancel_button.add_event_cb(cancel_cb,lv.EVENT.CLICKED,None)

def connect_cb(event):
    global access_points
    password=password_ta.get_text()
    access_points[selected_ssid]=password
    save_config()
    popup.delete()
    success=attempt_connecting(selected_ssid,password)
    refresh_list()

def cancel_cb(event):
    popup.delete()

def create_ui(subwindow):
    global list
    list=lv.list(subwindow)
    list.set_size(280,300)
    list.center()
    refresh_list()
    scan_button=lv.button(subwindow)
    scan_button.set_size(100,40)
    scan_button.align(lv.ALIGN.TOP_MID,0,10)
    label=lv.label(scan_button)
    label.set_text("Scan")
    scan_button.add_event_cb(scan_cb,lv.EVENT.CLICKED,None)
    load_config()

subwindow.clean()
create_ui(subwindow)
