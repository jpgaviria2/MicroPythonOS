import ujson
import os
import time
import lvgl as lv
import _thread

from mpos.apps import Activity, Intent
import mpos.ui
import mpos.config

# Global variables because they're used by multiple Activities:
access_points={}
last_tried_ssid = ""
last_tried_result = ""

# This is basically the wifi settings app
class WiFi(Activity):

    scan_button_scan_text = "Rescan"
    scan_button_scanning_text = "Scanning..."

    ssids=[]
    havenetwork = True
    keep_running = True
    busy_scanning = False
    busy_connecting = False

    # Widgets:
    aplist = None
    error_label = None
    scan_button = None
    scan_button_label = None

    def onCreate(self):
        main_screen = lv.obj()
        main_screen.set_style_pad_all(15, 0)
        print("create_ui: Creating list widget")
        self.aplist=lv.list(main_screen)
        self.aplist.set_size(lv.pct(100),lv.pct(80))
        self.aplist.align(lv.ALIGN.TOP_MID,0,0)
        print("create_ui: Creating error label")
        self.error_label=lv.label(main_screen)
        self.error_label.set_text("")
        self.error_label.align(lv.ALIGN.BOTTOM_MID,0,-40)
        self.error_label.add_flag(lv.obj.FLAG.HIDDEN)
        print("create_ui: Creating Scan button")
        self.scan_button=lv.button(main_screen)
        self.scan_button.set_size(lv.SIZE_CONTENT,lv.pct(15))
        self.scan_button.align(lv.ALIGN.BOTTOM_MID,0,0)
        self.scan_button_label=lv.label(self.scan_button)
        self.scan_button_label.set_text(self.scan_button_scan_text)
        self.scan_button_label.center()
        self.scan_button.add_event_cb(self.scan_cb,lv.EVENT.CLICKED,None)
        self.setContentView(main_screen)

    def onStart(self, screen):
        self.havenetwork = True
        try:
            import network
            wlan=network.WLAN(network.STA_IF)
            wlan.active(True)
        except Exception as e:
            self.havenetwork = False

    def onResume(self, screen):
        global access_points
        access_points = mpos.config.SharedPreferences("com.micropythonos.system.wifiservice").get_dict("access_points")
        self.keep_running = True
        if len(self.ssids) == 0:
            self.start_scan_networks()

    def onStop(self, screen):
        self.keep_running = False

    def show_error(self, message):
        if self.keep_running: # called from slow threads so might already have stopped
            # Schedule UI updates because different thread
            print(f"show_error: Displaying error: {message}")
            lv.async_call(lambda l: self.error_label.set_text(message), None)
            lv.async_call(lambda l: self.error_label.remove_flag(lv.obj.FLAG.HIDDEN), None)
            timer=lv.timer_create(lambda t: self.error_label.add_flag(lv.obj.FLAG.HIDDEN),3000,None)
            timer.set_repeat_count(1)

    def scan_networks_thread(self):
        print("scan_networks: Scanning for Wi-Fi networks")
        global ssids, busy_scanning, scan_button_label, scan_button
        if self.havenetwork and not wlan.isconnected(): # restart WiFi hardware in case it's in a bad state
            wlan.active(False)
            wlan.active(True)
        try:
            if self.havenetwork:
                networks = wlan.scan()
                self.ssids = list(set(n[0].decode() for n in networks))
            else:
                time.sleep(2)
                self.ssids = ["Home WiFi", "I believe Wi can Fi", "Winternet is coming", "The Promised LAN"]
            print(f"scan_networks: Found networks: {self.ssids}")
        except Exception as e:
            print(f"scan_networks: Scan failed: {e}")
            self.show_error("Wi-Fi scan failed")
        # scan done:
        self.busy_scanning = False
        if self.keep_running:
            # Schedule UI updates because different thread
            lv.async_call(lambda l: self.scan_button_label.set_text(self.scan_button_scan_text), None)
            lv.async_call(lambda l: self.scan_button.add_flag(lv.obj.FLAG.CLICKABLE), None)
            lv.async_call(lambda l: self.refresh_list(), None)

    def start_scan_networks(self):
        print("scan_networks: Showing scanning label")
        if self.busy_scanning:
            print("Not scanning for networks because already busy_scanning.")
        elif not self.keep_running:
            return
        else:
            self.busy_scanning = True
            self.scan_button.remove_flag(lv.obj.FLAG.CLICKABLE)
            self.scan_button_label.set_text(self.scan_button_scanning_text)
            _thread.stack_size(mpos.apps.good_stack_size())
            _thread.start_new_thread(self.scan_networks_thread, ())

    def refresh_list(self):
        print("refresh_list: Clearing current list")
        self.aplist.clean() # this causes an issue with lost taps if an ssid is clicked that has been removed
        print("refresh_list: Populating list with scanned networks")
        for ssid in self.ssids:
            if len(ssid) < 1 or len(ssid) > 32:
                print(f"Skipping too short or long SSID: {ssid}")
                continue
            print(f"refresh_list: Adding SSID: {ssid}")
            button=self.aplist.add_button(None,ssid)
            button.add_event_cb(lambda e, s=ssid: self.select_ssid_cb(s),lv.EVENT.CLICKED,None)
            if self.havenetwork and wlan.isconnected() and wlan.config('essid')==ssid:
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
    
    def scan_cb(self, event):
        print("scan_cb: Scan button clicked, refreshing list")
        self.start_scan_networks()
    
    def select_ssid_cb(self,ssid):
        print(f"select_ssid_cb: SSID selected: {ssid}")
        intent = Intent(activity_class=PasswordPage)
        intent.putExtra("selected_ssid", ssid)
        self.startActivityForResult(intent, self.password_page_result_cb)
        
    def password_page_result_cb(self, result):
        print(f"PasswordPage finished, result: {result}")
        if result.get("result_code"):
            data = result.get("data")
            if data:
                self.start_attempt_connecting(data.get("ssid"), data.get("password"))

    def start_attempt_connecting(self, ssid, password):
        print(f"start_attempt_connecting: Attempting to connect to SSID '{ssid}' with password '{password}'")
        self.scan_button.remove_flag(lv.obj.FLAG.CLICKABLE)
        self.scan_button_label.set_text(f"Connecting to {ssid}...")
        if self.busy_connecting:
            print("Not attempting connect because busy_connecting.")
        else:
            self.busy_connecting = True
            _thread.stack_size(mpos.apps.good_stack_size())
            _thread.start_new_thread(self.attempt_connecting_thread, (ssid,password))

    def attempt_connecting_thread(self, ssid, password):
        global last_tried_ssid, last_tried_result
        print(f"attempt_connecting_thread: Attempting to connect to SSID '{ssid}' with password '{password}'")
        result="connected"
        try:
            if self.havenetwork:
                wlan.disconnect()
                wlan.connect(ssid,password)
                for i in range(10):
                    if wlan.isconnected() or not self.keep_running:
                        print(f"attempt_connecting: Connected to {ssid} after {i+1} seconds")
                        break
                    print(f"attempt_connecting: Waiting for connection, attempt {i+1}/10")
                    time.sleep(1)
                if not wlan.isconnected():
                    result="timeout"
            else:
                print("Warning: not trying to connect because not havenetwork, just waiting a bit...")
                time.sleep(5)
        except Exception as e:
            print(f"attempt_connecting: Connection error: {e}")
            result=f"{e}"
            self.show_error("Connecting to {ssid} failed!")
        print(f"Connecting to {ssid} got result: {result}")
        last_tried_ssid = ssid
        last_tried_result = result
        self.busy_connecting=False
        if self.keep_running:
            # Schedule UI updates because different thread
            lv.async_call(lambda l: self.scan_button_label.set_text(self.scan_button_scan_text), None)
            lv.async_call(lambda l: self.scan_button.add_flag(lv.obj.FLAG.CLICKABLE), None)
            lv.async_call(lambda l: self.refresh_list(), None)




class PasswordPage(Activity):

    # Would be good to add some validation here so the password is not too short etc...

    selected_ssid = None

    # Widgets:
    password_ta=None
    keyboard=None
    connect_button=None
    cancel_button=None


    def onCreate(self):
        self.selected_ssid = self.getIntent().extras.get("selected_ssid")
        print("PasswordPage: Creating new password page")
        password_page=lv.obj()
        password_page.set_size(lv.pct(100),lv.pct(100))
        print(f"show_password_page: Creating label for SSID: {self.selected_ssid}")
        label=lv.label(password_page)
        label.set_text(f"Password for {self.selected_ssid}")
        label.align(lv.ALIGN.TOP_MID,0,5)
        print("PasswordPage: Creating password textarea")
        self.password_ta=lv.textarea(password_page)
        self.password_ta.set_size(200,30)
        self.password_ta.set_one_line(True)
        self.password_ta.align_to(label, lv.ALIGN.OUT_BOTTOM_MID, 5, 0)
        self.password_ta.add_event_cb(self.password_ta_cb,lv.EVENT.CLICKED,None)
        pwd = self.findSavedPassword(self.selected_ssid)
        if pwd:
            self.password_ta.set_text(pwd)
        self.password_ta.set_placeholder_text("Password")
        print("PasswordPage: Creating keyboard (hidden by default)")
        self.keyboard=lv.keyboard(password_page)
        self.keyboard.set_size(lv.pct(100),0)
        self.keyboard.align(lv.ALIGN.BOTTOM_LEFT,0,0)
        self.keyboard.set_textarea(self.password_ta)
        self.keyboard.add_event_cb(self.keyboard_cb,lv.EVENT.READY,None)
        self.keyboard.add_event_cb(self.keyboard_cb,lv.EVENT.CANCEL,None)
        self.keyboard.add_event_cb(self.keyboard_value_changed_cb,lv.EVENT.VALUE_CHANGED,None)
        print("PasswordPage: Creating Connect button")
        self.connect_button=lv.button(password_page)
        self.connect_button.set_size(100,40)
        self.connect_button.align(lv.ALIGN.BOTTOM_LEFT,10,-40)
        self.connect_button.add_event_cb(self.connect_cb,lv.EVENT.CLICKED,None)
        label=lv.label(self.connect_button)
        label.set_text("Connect")
        label.center()
        print("PasswordPage: Creating Cancel button")
        self.cancel_button=lv.button(password_page)
        self.cancel_button.set_size(100,40)
        self.cancel_button.align(lv.ALIGN.BOTTOM_RIGHT,-10,-40)
        self.cancel_button.add_event_cb(self.cancel_cb,lv.EVENT.CLICKED,None)
        label=lv.label(self.cancel_button)
        label.set_text("Close")
        label.center()
        print("PasswordPage: Loading password page")
        self.setContentView(password_page)

    def hide_keyboard(self):
        #global keyboard,connect_button,cancel_button
        print("keyboard_cb: READY or CANCEL or RETURN clicked, hiding keyboard")
        self.keyboard.set_height(0)
        self.keyboard.remove_flag(lv.obj.FLAG.CLICKABLE)
        print("keyboard_cb: Showing Connect and Cancel buttons")
        self.connect_button.remove_flag(lv.obj.FLAG.HIDDEN)
        self.cancel_button.remove_flag(lv.obj.FLAG.HIDDEN)
    
    def keyboard_cb(self, event):
        #print("keyboard_cb: Keyboard event triggered")
        code=event.get_code()
        if code==lv.EVENT.READY or code==lv.EVENT.CANCEL:
            self.hide_keyboard()
    
    def keyboard_value_changed_cb(self, event):
        #print("keyboard value changed!")
        #print(f"event: code={event.get_code()}, target={event.get_target()}, user_data={event.get_user_data()}, param={event.get_param()}") # event: code=32, target=<Blob>, user_data=<Blob>, param=<Blob>
        button = self.keyboard.get_selected_button()
        text = self.keyboard.get_button_text(button)
        #print(f"button {button} and text {text}")
        if text == lv.SYMBOL.NEW_LINE:
            print("Newline key pressed, hiding keyboard...")
            hide_keyboard()
    
    def password_ta_cb(self, event):
        print("password_ta_cb: Password textarea clicked")
        print("password_ta_cb: Hiding Connect and Cancel buttons")
        self.connect_button.add_flag(lv.obj.FLAG.HIDDEN)
        self.cancel_button.add_flag(lv.obj.FLAG.HIDDEN)
        print("password_ta_cb: Showing keyboard")
        self.keyboard.set_height(160)
        self.keyboard.add_flag(lv.obj.FLAG.CLICKABLE) # seems needed after showing/hiding the keyboard a few times
    
    
    def connect_cb(self, event):
        global access_points
        print("connect_cb: Connect button clicked")
        password=self.password_ta.get_text()
        print(f"connect_cb: Got password: {password}")
        self.setPassword(self.selected_ssid, password)
        print(f"connect_cb: Updated access_points: {access_points}")
        editor = mpos.config.SharedPreferences("com.micropythonos.system.wifiservice").edit()
        editor.put_dict("access_points", access_points)
        editor.commit()
        self.setResult(True, {"ssid": self.selected_ssid, "password": password})
        print("connect_cb: Restoring main_screen")
        self.finish()
    
    def cancel_cb(self, event):
        print("cancel_cb: Cancel button clicked")
        self.finish()

    @staticmethod
    def setPassword(ssid, password):
        global access_points
        ap = access_points.get(ssid)
        if ap:
            ap["password"] = password
            return
        # if not found, then add it:
        access_points[ssid] = { "password": password }

    @staticmethod
    def findSavedPassword(ssid):
        if not access_points:
            return None
        ap = access_points.get(ssid)
        if ap:
            return ap.get("password")
        return None
