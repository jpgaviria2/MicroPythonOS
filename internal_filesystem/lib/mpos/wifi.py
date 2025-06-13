# Automatically connect to the WiFi, based on the saved networks
# Manage concurrent accesses to the wifi (scan while connect, connect while scan etc)
# Manage saved networks
# This gets started in a new thread, does an autoconnect, and exits.

import ujson
import os
import time

import mpos.config
import mpos.time

have_network = False
try:
    import network
    have_network = True
except Exception as e:
    print("Could not import network, have_network=False")

class WifiService():

    wifi_busy = False # crude lock on wifi

    @staticmethod
    def connect():
        networks = wlan.scan()
        for n in networks:
            ssid = n[0].decode()
            print(f"auto_connect: checking ssid '{ssid}'")
            if ssid in access_points:
                password = access_points.get(ssid).get("password")
                print(f"auto_connect: attempting to connect to saved network {ssid} with password {password}")
                if attempt_connecting(ssid,password):
                    print(f"auto_connect: Connected to {ssid}")
                    return True
                else:
                    print(f"auto_connect: failed to connect to {ssid}")
            else:
                print(f"auto_connect: not trying {ssid} because it hasn't been configured")
        print("auto_connect: no known networks connected")
        return False

    @staticmethod
    def attempt_connecting(ssid,password):
        print(f"auto_connect.py attempt_connecting: Attempting to connect to SSID: {ssid}")
        try:
            wlan.connect(ssid,password)
            for i in range(10):
                if wlan.isconnected():
                    print(f"auto_connect.py attempt_connecting: Connected to {ssid} after {i+1} seconds")
                    mpos.time.sync_time()
                    return True
                elif not wlan.active(): # wificonf app or others might stop the wifi, no point in continuing then
                    print("auto_connect.py attempt_connecting: Someone disabled wifi, bailing out...")
                    return False
                print(f"auto_connect.py attempt_connecting: Waiting for connection, attempt {i+1}/10")
                time.sleep(1)
            print(f"auto_connect.py attempt_connecting: Failed to connect to {ssid}")
            return False
        except Exception as e:
            print(f"auto_connect.py attempt_connecting: Connection error: {e}")
            return False

    @staticmethod
    def auto_connect():
        print("auto_connect thread running")

        # load config:
        access_points = mpos.config.SharedPreferences("com.micropythonos.system.wifiservice").get_dict("access_points")
        if not len(access_points):
            print("WifiService.py: not access points configured, exiting...")
            return

        if not WifiService.wifi_busy:
            WifiService.wifi_busy = True
            if not have_network:
                print("auto_connect: no network module found, waiting to simulate connection...")
                time.sleep(10)
                print("auto_connect: wifi connect simulation done")
            else:
                wlan=network.WLAN(network.STA_IF)
                wlan.active(False) # restart WiFi hardware in case it's in a bad state
                wlan.active(True)
                if connect():
                    print("WifiService.py managed to connect.")
                else:
                    print("WifiService.py did not manage to connect.")
                    wlan.active(False) # disable to conserve power
            WifiService.wifi_busy = False

    @staticmethod
    def is_connected():
        if WifiService.wifi_busy:
            return False
        elif not have_network:
            return True
        else:
            return network.WLAN(network.STA_IF).isconnected()
