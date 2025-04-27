import network
import ujson
import os
import time
import lvgl as lv

class WiFiConf:
    def __init__(self,subwindow):
        self.subwindow=subwindow
        self.wlan=network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.access_points={}
        self.load_config()
        self.selected_ssid=None
        self.create_ui()
    def load_config(self):
        try:
            os.stat('/data/com.example.wificonf')
        except OSError:
            os.makedirs('/data/com.example.wificonf')
        try:
            with open('/data/com.example.wificonf/conf.json','r') as f:
                self.access_points=ujson.load(f)
        except OSError:
            self.access_points={}
    def save_config(self):
        with open('/data/com.example.wificonf/conf.json','w') as f:
            ujson.dump(self.access_points,f)
    def scan_networks(self):
        networks=self.wlan.scan()
        return [n[0].decode() for n in networks]
    def attempt_connecting(self,ssid,password):
        self.wlan.connect(ssid,password)
        for _ in range(10):
            if self.wlan.isconnected():
                return True
            time.sleep(1)
        return False
    def create_ui(self):
        self.list=lv.list(self.subwindow)
        self.list.set_size(280,300)
        self.list.center()
        self.refresh_list()
        scan_button=lv.button(self.subwindow)
        scan_button.set_size(100,40)
        scan_button.align(lv.ALIGN.TOP_MID,0,10)
        label=lv.label(scan_button)
        label.set_text("Scan")
        scan_button.add_event_cb(self.scan_cb,lv.EVENT.CLICKED,None)
    def refresh_list(self):
        self.list.clean()
        for ssid in self.scan_networks():
            button=self.list.add_button(None,ssid)
            button.add_event_cb(self.select_ssid_cb,lv.EVENT.CLICKED,ssid)
            status="connected" if self.wlan.isconnected() and self.wlan.config('essid')==ssid else \
                  "failed" if ssid in self.access_points else ""
            if status:
                label=lv.label(button)
                label.set_text(status)
                label.align(lv.ALIGN.RIGHT_MID,-10,0)
    def scan_cb(self,event):
        self.refresh_list()
    def select_ssid_cb(self,event,ssid):
        self.selected_ssid=ssid
        self.show_password_popup()
    def show_password_popup(self):
        self.popup=lv.obj(self.subwindow)
        self.popup.set_size(260,200)
        self.popup.center()
        self.popup.add_flag(lv.OBJ_FLAG.CLICKABLE)
        label=lv.label(self.popup)
        label.set_text(f"Enter password for {self.selected_ssid}")
        label.align(lv.ALIGN.TOP_MID,0,10)
        self.password_ta=lv.textarea(self.popup)
        self.password_ta.set_size(220,40)
        self.password_ta.align(lv.ALIGN.CENTER,0,-20)
        self.password_ta.set_placeholder_text("Password")
        keyboard=lv.keyboard(self.popup)
        keyboard.set_size(260,100)
        keyboard.align(lv.ALIGN.BOTTOM_MID,0,0)
        keyboard.set_textarea(self.password_ta)
        connect_button=lv.button(self.popup)
        connect_button.set_size(100,40)
        connect_button.align(lv.ALIGN.BOTTOM_LEFT,10,-50)
        label=lv.label(connect_button)
        label.set_text("Connect")
        connect_button.add_event_cb(self.connect_cb,lv.EVENT.CLICKED,None)
        cancel_button=lv.button(self.popup)
        cancel_button.set_size(100,40)
        cancel_button.align(lv.ALIGN.BOTTOM_RIGHT,-10,-50)
        label=lv.label(cancel_button)
        label.set_text("Cancel")
        cancel_button.add_event_cb(self.cancel_cb,lv.EVENT.CLICKED,None)
    def connect_cb(self,event):
        password=self.password_ta.get_text()
        self.access_points[self.selected_ssid]=password
        self.save_config()
        self.popup.delete()
        success=self.attempt_connecting(self.selected_ssid,password)
        self.refresh_list()
    def cancel_cb(self,event):
        self.popup.delete()


app=WiFiConf(subwindow)
