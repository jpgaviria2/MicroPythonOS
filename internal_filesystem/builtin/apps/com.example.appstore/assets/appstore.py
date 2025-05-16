import lvgl as lv
import json
import urequests
import gc
import os
import time
import _thread

import mpos.apps

# Screens:
app_detail_screen = None
appscreen = lv.screen_active()

apps = []
update_button = None
install_button = None
install_label = None
please_wait_label = None

progress_bar = None

refresh_icons_period = 300

action_label_install = "Install"
action_label_uninstall = "Uninstall"
action_label_restore = "Restore Built-in"
action_label_nothing = "Disable" # This doesn't do anything at the moment, but it could mark builtin apps as "Disabled" somehow and also allow for "Enable" then

def compare_versions(ver1: str, ver2: str) -> bool:
    """Compare two version numbers (e.g., '1.2.3' vs '4.5.6').
    Returns True if ver1 is greater than ver2, False otherwise."""
    print(f"Comparing versions: {ver1} vs {ver2}")
    v1_parts = [int(x) for x in ver1.split('.')]
    v2_parts = [int(x) for x in ver2.split('.')]
    print(f"Version 1 parts: {v1_parts}")
    print(f"Version 2 parts: {v2_parts}")
    for i in range(max(len(v1_parts), len(v2_parts))):
        v1 = v1_parts[i] if i < len(v1_parts) else 0
        v2 = v2_parts[i] if i < len(v2_parts) else 0
        print(f"Comparing part {i}: {v1} vs {v2}")
        if v1 > v2:
            print(f"{ver1} is greater than {ver2}")
            return True
        if v1 < v2:
            print(f"{ver1} is less than {ver2}")
            return False
    print(f"Versions are equal or {ver1} is not greater than {ver2}")
    return False

def is_builtin_app(app_fullname):
    return is_installed_by_path(f"builtin/apps/{app_fullname}")

def is_overridden_builtin_app(app_fullname):
    return is_installed_by_path(f"apps/{app_fullname}") and is_installed_by_path(f"builtin/apps/{app_fullname}")

def is_update_available(app_fullname, new_version):
    appdir = f"apps/{app_fullname}"
    builtinappdir = f"builtin/apps/{app_fullname}"
    installed_app=None
    if is_installed_by_path(appdir):
        print(f"{appdir} found, getting version...")
        installed_app = parse_manifest(f"{appdir}/META-INF/MANIFEST.JSON")
    elif is_installed_by_path(builtinappdir):
        print(f"{builtinappdir} found, getting version...")
        installed_app = parse_manifest(f"{builtinappdir}/META-INF/MANIFEST.JSON")
    if not installed_app or installed_app.version == "0.0.0": # special case, if the installed app doesn't have a version number then there's no update
        return False
    return compare_versions(new_version, installed_app.version)


def is_installed_by_path(dir_path):
    try:
        if os.stat(dir_path)[0] & 0x4000:
            manifest = f"{dir_path}/META-INF/MANIFEST.JSON"
            if os.stat(manifest)[0] & 0x8000:
                return True
    except OSError:
        pass # Skip if directory or manifest doesn't exist
    return False

def is_installed_by_name(app_fullname):
    print(f"Checking if app {app_fullname} is installed...")
    return is_installed_by_path(f"apps/{app_fullname}") or is_installed_by_path(f"builtin/apps/{app_fullname}")

def set_install_label(app_fullname):
    global install_label
    # Figure out whether to show:
    # - "install" option if not installed
    # - "update" option if already installed and new version
    # - "uninstall" option if already installed and not builtin
    # - "restore builtin" option if it's an overridden builtin app
    # So:
    # - install, uninstall and restore builtin can be same button, always shown
    # - update is separate button, only shown if already installed and new version
    is_installed = True
    update_available = False
    builtin_app = is_builtin_app(app_fullname)
    overridden_builtin_app = is_overridden_builtin_app(app_fullname)
    if not overridden_builtin_app:
        is_installed = is_installed_by_name(app_fullname)
    if is_installed:
        if builtin_app:
            if overridden_builtin_app:
                action_label = action_label_restore
            else:
                action_label = action_label_nothing
        else:
            action_label = action_label_uninstall
    else:
        action_label = action_label_install
    install_label.set_text(action_label)


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


def uninstall_app(app_folder, app_fullname):
    global install_button, progress_bar, update_button
    install_button.remove_flag(lv.obj.FLAG.CLICKABLE) # TODO: change color so it's clear the button is not clickable
    install_label.set_text("Please wait...") # TODO: Put "Cancel" if cancellation is possible
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
    set_install_label(app_fullname)
    install_button.add_flag(lv.obj.FLAG.CLICKABLE)
    if is_builtin_app(app_fullname):
        update_button.remove_flag(lv.obj.FLAG.HIDDEN)
        install_button.set_size(lv.pct(47), 40) # if a builtin app was removed, then it was overridden, and a new version is available, so make space for update button


def download_and_unzip(zip_url, dest_folder, app_fullname):
    global install_button, progress_bar
    install_button.remove_flag(lv.obj.FLAG.CLICKABLE) # TODO: change color so it's clear the button is not clickable
    install_label.set_text("Please wait...") # TODO: Put "Cancel" if cancellation is possible
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
            set_install_label(app_fullname)
        progress_bar.set_value(40, lv.ANIM.ON)
        time.sleep_ms(500)
        # Save the .mpk file to a temporary location
        try:
            os.remove(temp_zip_path)
        except Exception:
            pass
        try:
            os.mkdir("tmp")
        except Exception:
            pass
        temp_zip_path = "tmp/temp.mpk"
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
    set_install_label(app_fullname)
    install_button.add_flag(lv.obj.FLAG.CLICKABLE)


def download_apps(json_url):
    global apps, please_wait_label
    try:
        response = urequests.get(json_url, timeout=10)
    except Exception as e:
        print("Download failed:", e)
        please_wait_label.set_text(f"Error downloading app index: {e}")
    if response and response.status_code == 200:
        print(f"Got response text: {response.text}")
        apps = [mpos.apps.App(**app) for app in json.loads(response.text)]
        response.close()
        # Remove duplicates based on app.name
        seen = set()
        apps = [app for app in apps if not (app.name in seen or seen.add(app.name))]
        # Sort apps by app.name
        apps.sort(key=lambda x: x.name.lower())  # Use .lower() for case-insensitive sorting
        please_wait_label.add_flag(lv.obj.FLAG.HIDDEN)
        create_apps_list()

def download_icons():
    for app in apps:
        print("Downloading icon for app ")
        image_dsc = download_icon(app.icon_url)
        app.image_dsc = image_dsc
    print("Finished downloading icons, scheduling stop of refresh timer...")
    # One more fresh is needed, so this needs to be scheduled after the next icon refresh
    refresh_icons_pause = lv.timer_create(lambda l: refresh_icons.pause(), refresh_icons_period, None)
    refresh_icons_pause.set_repeat_count(1)
    refresh_icons_pause.set_auto_delete(False)


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
    default_icon_dsc = load_icon("builtin/res/mipmap-mdpi/default_icon_64x64.png")
    print("create_apps_list")
    apps_list = lv.list(appscreen)
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
    print("create_apps_list app done")
    try:
        _thread.stack_size(32*1024) # seems to need 32KB for urequests
        _thread.start_new_thread(download_icons,())
    except Exception as e:
        print("Could not start thread to download icons: ", e)


def show_app_detail(app):
    global app_detail_screen, install_button, progress_bar, install_label
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
    # Always have this button:
    buttoncont = lv.obj(cont)
    buttoncont.set_style_pad_all(0, 0)
    buttoncont.set_flex_flow(lv.FLEX_FLOW.ROW)
    buttoncont.set_size(lv.pct(100), lv.SIZE_CONTENT)
    buttoncont.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
    print(f"Adding (un)install button for url: {app.download_url}")
    install_button = lv.button(buttoncont)
    install_button.add_flag(lv.obj.FLAG.CLICKABLE)
    install_button.add_event_cb(lambda e, d=app.download_url, f=app.fullname: toggle_install(d,f), lv.EVENT.CLICKED, None)
    install_button.set_size(lv.pct(100), 40)
    install_label = lv.label(install_button)
    install_label.center()
    set_install_label(app.fullname)
    if is_update_available(app.fullname, app.version):
        install_button.set_size(lv.pct(47), 40) # make space for update button
        print("Update available, adding update button.")
        global update_button
        update_button = lv.button(buttoncont)
        update_button.set_size(lv.pct(47), 40)
        update_button.add_event_cb(lambda e, d=app.download_url, f=app.fullname: update_button_click(d,f), lv.EVENT.CLICKED, None)
        update_label = lv.label(update_button)
        update_label.set_text("Update")
        update_label.center()
    # version label:
    version_label = lv.label(cont)
    version_label.set_width(lv.pct(100))
    version_label.set_text(f"Latest version: {app.version}") # make this bold if this is newer than the currently installed one
    version_label.set_style_text_font(lv.font_montserrat_12, 0)
    version_label.align_to(install_button, lv.ALIGN.OUT_BOTTOM_MID, 0, lv.pct(5))
    long_desc_label = lv.label(cont)
    long_desc_label.align_to(version_label, lv.ALIGN.OUT_BOTTOM_MID, 0, lv.pct(5))
    long_desc_label.set_text(app.long_description)
    long_desc_label.set_style_text_font(lv.font_montserrat_12, 0)
    long_desc_label.set_width(lv.pct(100))
    lv.screen_load(app_detail_screen)


def toggle_install(download_url, fullname):
    global install_label
    print(f"Install button clicked for {download_url} and fullname {fullname}")
    label_text = install_label.get_text()
    if label_text == action_label_install:
        try:
            _thread.stack_size(12*1024)
            _thread.start_new_thread(download_and_unzip, (download_url, f"apps/{fullname}", fullname))
        except Exception as e:
            print("Could not start download_and_unzip thread: ", e)
    elif label_text == action_label_uninstall or label_text == action_label_restore:
        print("Uninstalling app....")
        try:
            _thread.stack_size(12*1024)
            _thread.start_new_thread(uninstall_app, (f"apps/{fullname}", fullname))
        except Exception as e:
            print("Could not start download_and_unzip thread: ", e)

def update_button_click(download_url, fullname):
    print(f"Update button clicked for {download_url} and fullname {fullname}")
    global update_button
    update_button.add_flag(lv.obj.FLAG.HIDDEN)
    install_button.set_size(lv.pct(100), 40)
    try:
        _thread.stack_size(12*1024)
        _thread.start_new_thread(download_and_unzip, (download_url, f"apps/{fullname}", fullname))
    except Exception as e:
        print("Could not start download_and_unzip thread: ", e)


def back_to_main(event):
    global app_detail_screen
    if app_detail_screen:
        app_detail_screen.delete()
        app_detail_screen = None
    lv.screen_load(appscreen)


def refresh_icons_cb(timer):
    #print("Refreshing app icons...")
    for app in apps:
        #print("Refreshing icon for {app.name}")
        if app.image_dsc:
            app.image.set_src(app.image_dsc)

def janitor_cb(timer):
    global appscreen, app_detail_screen
    if lv.screen_active() != appscreen and lv.screen_active() != app_detail_screen:
        print("appstore.py backgrounded, cleaning up...")
        janitor.delete()
        refresh_icons.delete()
        restart_launcher() # refresh the launcher
        print("appstore.py ending")

janitor = lv.timer_create(janitor_cb, 400, None)
refresh_icons = lv.timer_create(refresh_icons_cb, refresh_icons_period, None)

please_wait_label = lv.label(appscreen)
please_wait_label.set_text("Downloading app index...")
please_wait_label.center()

can_check_network = True
try:
    import network
except Exception as e:
    can_check_network = False

if can_check_network and not network.WLAN(network.STA_IF).isconnected():
    please_wait_label.set_text("Error: WiFi is not connected.")
else:
    _thread.stack_size(16*1024)
    _thread.start_new_thread(download_apps, ("http://demo.lnpiggy.com:2121/apps.json",))

