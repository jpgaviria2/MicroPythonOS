import lvgl as lv
import json
import urequests
import gc

apps = []
app_detail_screen = None
install_button = None
please_wait_label = None
app_detail_screen = None

class App:
    def __init__(self, name, publisher, short_description, long_description, icon_url, download_url):
        self.name = name
        self.publisher = publisher
        self.short_description = short_description
        self.long_description = long_description
        self.icon_url = icon_url
        self.image_dsc = None
        self.download_url = download_url

def load_icon(url):
    print(f"downloading icon from {url}")
    response = urequests.get(url, timeout=5)
    if response.status_code == 200:
        image_data = response.content
        print("Downloaded image, size:", len(image_data), "bytes")
        image_dsc = lv.image_dsc_t({
            'data_size': len(image_data),
            'data': image_data
        })
        return image_dsc
    else:
        print("Failed to download image: Status code", response.status_code)
        return None

import os
try:
    import zipfile
except ImportError:
    zipfile = None

def download_and_unzip(zip_url, dest_folder):
    try:
        # Step 1: Download the .zip file
        print("Downloading .zip file from:", zip_url)
        response = urequests.get(zip_url, timeout=10)
        if response.status_code != 200:
            print("Download failed: Status code", response.status_code)
            response.close()
            return False
        # Save the .zip file to a temporary location
        os.mkdir("/tmp")
        temp_zip_path = "/tmp/temp.zip"
        print(f"Writing to temporary zip path: {temp_zip_path}")
        # TODO: check free available space first!
        with open(temp_zip_path, "wb") as f:
            f.write(response.content)
        response.close()
        print("Downloaded .zip file, size:", os.stat(temp_zip_path)[6], "bytes")
        # Step 2: Unzip the file
        if zipfile is None:
            print("Error: zipfile module not available in this MicroPython build")
            return False
        print("Unzipping it to:", dest_folder)
        with zipfile.ZipFile(temp_zip_path, "r") as zip_ref:
            zip_ref.extractall(dest_folder)
        print("Unzipped successfully")
        # Step 3: Clean up
        os.remove(temp_zip_path)
        print("Removed temporary .zip file")
        return True
    except Exception as e:
        print("Operation failed:", str(e))
        return False
    finally:
        if 'response' in locals():
            response.close()


def download_apps(json_url):
    global apps
    try:
        response = urequests.get(json_url, timeout=10)
        print("download_apps")
        if response.status_code == 200:
            print(f"Got response text: {response.text}")
            apps = [App(**app) for app in json.loads(response.text)]
            response.close()
            please_wait_label.add_flag(lv.obj.FLAG.HIDDEN)
            create_apps_list()
    except Exception as e:
        print("Download failed:", e)
        please_wait_label.set_text(f"Error downloading app index: {e}")


def create_apps_list():
    global apps
    print("create_apps_list")
    apps_list = lv.list(subwindow)
    apps_list.set_style_pad_all(0, 0)
    apps_list.set_size(lv.pct(100), lv.pct(100))
    print("create_apps_list iterating")
    for app in apps:
        item = apps_list.add_button(None, "Test")
        item.set_style_pad_all(0, 0)
        item.add_flag(lv.obj.FLAG.CLICKABLE)
        item.set_size(lv.pct(100), lv.SIZE_CONTENT)
        item.add_event_cb(lambda e, a=app: show_app_detail(a), lv.EVENT.CLICKED, None)
        cont = lv.obj(item)
        cont.set_style_pad_all(0, 0)
        cont.set_flex_flow(lv.FLEX_FLOW.ROW)
        cont.set_size(lv.pct(100), lv.SIZE_CONTENT)
        cont.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        cont.add_event_cb(lambda e, a=app: show_app_detail(a), lv.EVENT.CLICKED, None)
        image_dsc = load_icon(app.icon_url)
        app.image_dsc = image_dsc
        icon_spacer = lv.image(cont)
        icon_spacer.set_src(image_dsc)
        icon_spacer.set_size(64, 64)
        icon_spacer.add_event_cb(lambda e, a=app: show_app_detail(a), lv.EVENT.CLICKED, None)
        label_cont = lv.obj(cont)
        label_cont.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        label_cont.set_size(lv.pct(75), lv.SIZE_CONTENT)
        label_cont.add_event_cb(lambda e, a=app: show_app_detail(a), lv.EVENT.CLICKED, None)
        name_label = lv.label(label_cont)
        name_label.set_text(app.name)
        name_label.set_style_text_font(lv.font_montserrat_16, 0)
        name_label.add_event_cb(lambda e, a=app: show_app_detail(a), lv.EVENT.CLICKED, None)
        desc_label = lv.label(label_cont)
        desc_label.set_text(app.short_description)
        desc_label.set_style_text_font(lv.font_montserrat_12, 0)
        desc_label.add_event_cb(lambda e, a=app: show_app_detail(a), lv.EVENT.CLICKED, None)
        print("create_apps_list app one done")
    print("create_apps_list app done")


def show_app_detail(app):
    global app_detail_screen, install_button
    app_detail_screen = lv.obj()
    app_detail_screen.set_size(lv.pct(100), lv.pct(100))
    back_button = lv.button(app_detail_screen)
    back_button.set_width(lv.pct(15))
    back_button.add_flag(lv.obj.FLAG.CLICKABLE)
    back_button.add_event_cb(back_to_main, lv.EVENT.CLICKED, None)
    back_label = lv.label(back_button)
    back_label.set_text(lv.SYMBOL.LEFT)
    back_label.center()
    cont = lv.obj(app_detail_screen)
    cont.set_size(lv.pct(100), lv.pct(100))
    cont.set_pos(0, 40)
    cont.set_flex_flow(lv.FLEX_FLOW.COLUMN)
    #
    headercont = lv.obj(cont)
    headercont.set_style_pad_all(0, 0)
    headercont.set_flex_flow(lv.FLEX_FLOW.ROW)
    headercont.set_size(lv.pct(100), lv.SIZE_CONTENT)
    headercont.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
    icon_spacer = lv.image(headercont)
    if app.image_dsc:
        icon_spacer.set_src(app.image_dsc)
    icon_spacer.set_size(64, 64)
    #
    detail_cont = lv.obj(headercont)
    detail_cont.set_style_pad_all(0, 0)
    detail_cont.set_flex_flow(lv.FLEX_FLOW.COLUMN)
    detail_cont.set_size(lv.pct(75), lv.SIZE_CONTENT)
    name_label = lv.label(detail_cont)
    name_label.set_text(app.name)
    name_label.set_style_text_font(lv.font_montserrat_24, 0)
    publisher_label = lv.label(detail_cont)
    publisher_label.set_text(app.publisher)
    publisher_label.set_style_text_font(lv.font_montserrat_16, 0)
    #
    #progress_bar = lv.bar(cont)
    #progress_bar.set_width(lv.pct(100))
    #progress_bar.set_range(0, 100)
    #progress_bar.set_value(50, lv.ANIM.OFF)
    install_button = lv.button(cont)
    install_button.align_to(detail_cont, lv.ALIGN.OUT_BOTTOM_MID, 0, lv.pct(5))
    install_button.set_size(lv.pct(100), 40)
    install_button.add_flag(lv.obj.FLAG.CLICKABLE)
    install_button.add_event_cb(lambda e, d=app.download_url: toggle_install(d), lv.EVENT.CLICKED, None)
    install_label = lv.label(install_button)
    install_label.set_text("(Re)Install") # TODO: check if already installed and if yes, change to "Uninstall" and "Open"
    install_label.center()
    long_desc_label = lv.label(cont)
    long_desc_label.align_to(install_button, lv.ALIGN.OUT_BOTTOM_MID, 0, lv.pct(5))
    long_desc_label.set_text(app.long_description)
    long_desc_label.set_style_text_font(lv.font_montserrat_12, 0)
    long_desc_label.set_width(lv.pct(100))
    lv.screen_load(app_detail_screen)


def toggle_install(download_url):
    global install_button
    label = install_button.get_child(0)
    if label.get_text() == "(Re)Install":
        install_button.remove_flag(lv.obj.FLAG.CLICKABLE) # TODO: change color so it's clear the button is not clickable
        label.set_text("Please wait...") # TODO: Put "Cancel" if cancellation is possible
        # TODO: do the download and install in a new thread with a few sleeps so it can be cancelled...
        download_and_unzip(download_url, "/apps")
        label.set_text("Open")
        install_button.add_flag(lv.obj.FLAG.CLICKABLE)
    else: # if the button text was "Please wait..." or "Uninstall" or "Installed!"
        label.set_text("Install")


def back_to_main(event):
    global app_detail_screen
    if app_detail_screen:
        app_detail_screen.delete()
        app_detail_screen = None
    lv.screen_load(appscreen)


print("appstore.py starting")

please_wait_label = lv.label(subwindow)
please_wait_label.set_text("Downloading app index...")
please_wait_label.center()

import network
if not network.WLAN(network.STA_IF).isconnected():
    please_wait_label.set_text("Error: WiFi is not connected.")
else:
    download_apps("http://demo.lnpiggy.com:2121/apps.json")
    # Wait until the user stops the app
    import time
    while appscreen == lv.screen_active() or app_detail_screen == lv.screen_active():
        time.sleep_ms(100)
    
print("appstore.py ending")
