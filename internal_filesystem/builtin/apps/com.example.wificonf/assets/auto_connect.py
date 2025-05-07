# Automatically connect to the WiFi, based on the saved networks

import network
import ujson
import os
import time


access_points={}


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


def auto_connect():
    # TODO: scan for wifi networks first, and only attempt to connect to the ones that are found
    print("auto_connect: Attempting to connect to known networks")
    for ssid,password in access_points.items():
        print(f"auto_connect: Trying SSID: {ssid}")
        if attempt_connecting(ssid,password):
            print(f"auto_connect: Connected to {ssid}")
            return True
    print("auto_connect: No known networks connected")
    return False


def attempt_connecting(ssid,password):
    print(f"auto_connect.py attempt_connecting: Attempting to connect to SSID: {ssid}")
    try:
        wlan.connect(ssid,password)
        for i in range(10):
            if wlan.isconnected():
                print(f"auto_connect.py attempt_connecting: Connected to {ssid} after {i+1} seconds")
                return True
            elif not wlan.active(): # wificonf app or others might stop the wifi, no point in continuing then
                print("auto_connect.py attempt_connecting: Someone disabled wifi, bailing out...")
                return False
            print(f"attempt_connecting: Waiting for connection, attempt {i+1}/10")
            time.sleep(1)
        print(f"auto_connect.py attempt_connecting: Failed to connect to {ssid}")
        return False
    except Exception as e:
        print(f"auto_connect.py attempt_connecting: Connection error: {e}")
        return False

print("auto_connect.py running...")
load_config()

wlan=network.WLAN(network.STA_IF)
wlan.active(True)

if auto_connect():
    print("auto_connect.py managed to connect.")
else:
    print("auto_connect.py did not manage to connect.")
    wlan.active(False) # disable to conserve power
