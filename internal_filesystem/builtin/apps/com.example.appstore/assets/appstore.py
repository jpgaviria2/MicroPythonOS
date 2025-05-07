import lvgl as lv
import json
import urequests
import gc
import os
import time
import _thread

mainscreen = lv.screen_active()

apps = []
app_detail_screen = None
install_button = None
please_wait_label = None
app_detail_screen = None
progress_bar = None
action_label_install = "Install Latest Version"
action_label_uninstall = "Uninstall"


class App:
    def __init__(self, name, publisher, short_description, long_description, icon_url, download_url, fullname, version, entrypoint, category):
        self.name = name
        self.publisher = publisher
        self.short_description = short_description
        self.long_description = long_description
        self.icon_url = icon_url
        self.download_url = download_url
        self.fullname = fullname
        self.version = version
        self.entrypoint = entrypoint
        self.category = category
        self.image = None
        self.image_dsc = None


def is_installed_by_path(dir_path):
    try:
        if os.stat(dir_path)[0] & 0x4000:
            manifest = f"{dir_path}/META-INF/MANIFEST.MF"
            if os.stat(manifest)[0] & 0x8000:
                return True
    except OSError:
        pass # Skip if directory or manifest doesn't exist
    return False

def is_installed_by_name(app_fullname):
    print(f"Checking if app {app_fullname} is installed...")
    return is_installed_by_path(f"/apps/{app_fullname}") or is_installed_by_path(f"/builtin/apps/{app_fullname}")

def download_icon(url):
    print(f"Downloading icon from {url}")
    try:
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
    except Exception as e:
        print(f"Exception during download of icon: {e}")
    return None

try:
    import zipfile
except ImportError:
    zipfile = None


def uninstall_app(app_folder, label):
    global install_button, progress_bar
    install_button.remove_flag(lv.obj.FLAG.CLICKABLE) # TODO: change color so it's clear the button is not clickable
    label.set_text("Please wait...") # TODO: Put "Cancel" if cancellation is possible
    progress_bar.remove_flag(lv.obj.FLAG.HIDDEN)
    progress_bar.set_value(33, lv.ANIM.ON)
    time.sleep_ms(500)
    try:
        import shutil
        shutil.rmtree(app_folder)
        progress_bar.set_value(66, lv.ANIM.ON)
        time.sleep_ms(500)
    except Exception as e:
        print(f"Removing app_folder {app_folder} got error: {e}")
    progress_bar.set_value(100, lv.ANIM.OFF)
    time.sleep(1)
    progress_bar.add_flag(lv.obj.FLAG.HIDDEN)
    progress_bar.set_value(0, lv.ANIM.OFF)
    label.set_text(action_label_install)
    install_button.add_flag(lv.obj.FLAG.CLICKABLE)

def download_and_unzip(zip_url, dest_folder, label):
    global install_button, progress_bar
    install_button.remove_flag(lv.obj.FLAG.CLICKABLE) # TODO: change color so it's clear the button is not clickable
    label.set_text("Please wait...") # TODO: Put "Cancel" if cancellation is possible
    progress_bar.remove_flag(lv.obj.FLAG.HIDDEN)
    progress_bar.set_value(20, lv.ANIM.ON)
    time.sleep_ms(500)
    try:
        # Step 1: Download the .mpk file
        print(f"Downloading .mpk file from: {zip_url}")
        response = urequests.get(zip_url, timeout=10)
        if response.status_code != 200:
            print("Download failed: Status code", response.status_code)
            response.close()
            label.set_text(action_label_install)
        progress_bar.set_value(40, lv.ANIM.ON)
        time.sleep_ms(500)
        # Save the .mpk file to a temporary location
        try:
            os.remove(temp_zip_path)
        except Exception:
            pass
        try:
            os.mkdir("/tmp")
        except Exception:
            pass
        temp_zip_path = "/tmp/temp.mpk"
        print(f"Writing to temporary mpk path: {temp_zip_path}")
        # TODO: check free available space first!
        with open(temp_zip_path, "wb") as f:
            f.write(response.content)
        progress_bar.set_value(60, lv.ANIM.ON)
        time.sleep_ms(500)
        response.close()
        print("Downloaded .mpk file, size:", os.stat(temp_zip_path)[6], "bytes")
        # Step 2: Unzip the file
        if zipfile is None:
            print("WARNING: zipfile module not available in this MicroPython build, unzip will fail!")
        print("Unzipping it to:", dest_folder)
        with zipfile.ZipFile(temp_zip_path, "r") as zip_ref:
            zip_ref.extractall(dest_folder)
        progress_bar.set_value(80, lv.ANIM.ON)
        time.sleep_ms(500)
        print("Unzipped successfully")
        # Step 3: Clean up
        os.remove(temp_zip_path)
        print("Removed temporary .mpk file")
    except Exception as e:
        print("Operation failed:", str(e))
    finally:
        if 'response' in locals():
            response.close()
            progress_bar.set_value(80, lv.ANIM.OFF)
    progress_bar.set_value(100, lv.ANIM.OFF)
    time.sleep(1)
    progress_bar.add_flag(lv.obj.FLAG.HIDDEN)
    progress_bar.set_value(0, lv.ANIM.OFF)
    label.set_text(action_label_uninstall)
    install_button.add_flag(lv.obj.FLAG.CLICKABLE)


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


def download_icons():
    global apps
    for app in apps:
        image_dsc = download_icon(app.icon_url)
        app.image_dsc = image_dsc
        app.image.set_src(image_dsc)
        print(f"Changed image_dsc for {app.icon_url}")
    print("finished downloading all icons")

def load_icon(icon_path):
    with open(icon_path, 'rb') as f:
        image_data = f.read()
        image_dsc = lv.image_dsc_t({
            'data_size': len(image_data),
            'data': image_data
        })
    return image_dsc

def create_apps_list():
    global apps
    default_icon_dsc = load_icon("/builtin/res/mipmap-mdpi/default_icon_64x64.png")
    print("create_apps_list")
    apps_list = lv.list(mainscreen)
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
        icon_spacer = lv.image(cont)
        #image_dsc = default_icon_dsc
        #app.image_dsc = image_dsc
        #icon_spacer.set_src(image_dsc)
        icon_spacer.set_size(64, 64)
        app.image = icon_spacer
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
    try:
        _thread.stack_size(16384)
        _thread.start_new_thread(download_icons,())
    except Exception as e:
        print("Could not start thread to download icons: ", e)


def show_app_detail(app):
    global app_detail_screen, install_button, progress_bar, action_label_install, action_label_uninstall
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
    progress_bar = lv.bar(cont)
    progress_bar.set_width(lv.pct(100))
    progress_bar.set_range(0, 100)
    progress_bar.add_flag(lv.obj.FLAG.HIDDEN)
    install_button = lv.button(cont)
    install_button.align_to(detail_cont, lv.ALIGN.OUT_BOTTOM_MID, 0, lv.pct(5))
    install_button.set_size(lv.pct(100), 40)
    install_button.add_flag(lv.obj.FLAG.CLICKABLE)
    print(f"Adding install button for url: {app.download_url}")
    install_button.add_event_cb(lambda e, d=app.download_url, f=app.fullname: toggle_install(d,f), lv.EVENT.CLICKED, None)
    install_label = lv.label(install_button)
    if is_installed_by_name(app.fullname):
        action_label = action_label_uninstall # Maybe show "restore builtin version" for builtin apps...
    else:
        action_label = action_label_install
    install_label.set_text(action_label)
    install_label.center()
    version_label = lv.label(cont)
    version_label.set_width(lv.pct(100))
    version_label.set_text(f"Version: {app.version}")
    version_label.set_style_text_font(lv.font_montserrat_12, 0)
    version_label.align_to(install_button, lv.ALIGN.OUT_BOTTOM_MID, 0, lv.pct(5))
    long_desc_label = lv.label(cont)
    long_desc_label.align_to(version_label, lv.ALIGN.OUT_BOTTOM_MID, 0, lv.pct(5))
    long_desc_label.set_text(app.long_description)
    long_desc_label.set_style_text_font(lv.font_montserrat_12, 0)
    long_desc_label.set_width(lv.pct(100))
    lv.screen_load(app_detail_screen)


def toggle_install(download_url, fullname):
    global install_button, action_label_install, action_label_uninstall
    print(f"Install button clicked for {download_url} and fullname {fullname}")
    label = install_button.get_child(0)
    if label.get_text() == action_label_install:
        try:
            _thread.stack_size(16384)
            _thread.start_new_thread(download_and_unzip, (download_url, f"/apps/{fullname}", label))
        except Exception as e:
            print("Could not start download_and_unzip thread: ", e)
    elif label.get_text() == action_label_uninstall:
        print("Uninstalling app....")
        try:
            _thread.stack_size(16384)
            _thread.start_new_thread(uninstall_app, (f"/apps/{fullname}", label))
        except Exception as e:
            print("Could not start download_and_unzip thread: ", e)


def back_to_main(event):
    global app_detail_screen
    if app_detail_screen:
        app_detail_screen.delete()
        app_detail_screen = None
    lv.screen_load(mainscreen)


print("appstore.py starting")

please_wait_label = lv.label(mainscreen)
please_wait_label.set_text("Downloading app index...")
please_wait_label.center()

import network
import time
if not network.WLAN(network.STA_IF).isconnected():
    please_wait_label.set_text("Error: WiFi is not connected.")
    time.sleep(10)
else:
    download_apps("http://demo.lnpiggy.com:2121/apps.json")
    # Wait until the user stops the app
    import time
    while mainscreen == lv.screen_active() or app_detail_screen == lv.screen_active():
        time.sleep_ms(100)
    print("User navigated away from the appstore, restarting launcher to refresh...")
    restart_launcher() # refresh the launcher

print("appstore.py ending")
