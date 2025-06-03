import lvgl as lv
import requests
import ujson
import time
import _thread

import mpos.apps
import mpos.info
import mpos.ui

main_screen = None

status_label=None
install_button=None

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


# Custom OTA update with LVGL progress
def update_with_lvgl(url):
    global install_button, status_label, main_screen
    install_button.add_flag(lv.obj.FLAG.HIDDEN) # or change to cancel button?
    status_label.set_text("Update in progress.\nNavigate away to cancel.")
    import ota.update
    import ota.status
    ota.status.status()
    from esp32 import Partition
    current_partition = Partition(Partition.RUNNING)
    print(f"Current partition: {current_partition}")
    next_partition = current_partition.get_next_update()
    print(f"Next partition: {next_partition}")
    label = lv.label(main_screen)
    label.set_text("OS Update: 0.00%")
    label.align(lv.ALIGN.CENTER, 0, -30)
    progress_bar = lv.bar(main_screen)
    progress_bar.set_size(200, 20)
    progress_bar.align(lv.ALIGN.BOTTOM_MID, 0, -50)
    progress_bar.set_range(0, 100)
    progress_bar.set_value(0, lv.ANIM.OFF)
    def progress_callback(percent):
        print(f"OTA Update: {percent:.1f}%")
        label.set_text(f"OTA Update: {percent:.2f}%")
        progress_bar.set_value(int(percent), lv.ANIM.ON)
    current = Partition(Partition.RUNNING)
    next_partition = current.get_next_update()
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('Content-Length', 0))
    bytes_written = 0
    chunk_size = 4096
    i = 0
    print(f"Starting OTA update of size: {total_size}")
    while main_screen == lv.screen_active(): # stop if the user navigates away
        time.sleep_ms(100) # don't hog the CPU
        chunk = response.raw.read(chunk_size)
        if not chunk:
            print("No chunk, breaking...")
            break
        if len(chunk) < chunk_size:
            print(f"Padding chunk {i} from {len(chunk)} to {chunk_size} bytes")
            chunk = chunk + b'\xFF' * (chunk_size - len(chunk))
        print(f"Writing chunk {i}")
        next_partition.writeblocks(i, chunk)
        bytes_written += len(chunk)
        i += 1
        if total_size:
            progress_callback(bytes_written / total_size * 100)
    response.close()
    if bytes_written >= total_size: # if the update was completely installed
        next_partition.set_boot()
        import machine
        machine.reset()

def install_button_click(download_url):
    print(f"install_button_click for url {download_url}")
    try:
        _thread.stack_size(mpos.apps.good_stack_size())
        _thread.start_new_thread(update_with_lvgl, (download_url,))
    except Exception as e:
        print("Could not start update_with_lvgl thread: ", e)

def handle_update_info(version, download_url, changelog):
    global install_button, status_label
    label = f"Installed OS version: {mpos.info.CURRENT_OS_VERSION}\n"
    if compare_versions(version, mpos.info.CURRENT_OS_VERSION):
        label += "Available new"
        install_button.remove_flag(lv.obj.FLAG.HIDDEN)
        install_button.add_event_cb(lambda e, u=download_url: install_button_click(u), lv.EVENT.CLICKED, None)
    else:
        label += "matches latest"
    label += f" version: {version}\n\nDetails:\n\n{changelog}"
    status_label.set_text(label)

def show_update_info():
    global status_label
    status_label.set_text("Checking for OS updates...")
    # URL of the JSON file
    url = "http://demo.lnpiggy.com:2121/osupdate.json"  # Adjust if the actual JSON URL differs
    print(f"osudpate.py: fetching {url}")
    try:
        print("doing requests.get()")
        # Download the JSON
        response = requests.get(url)
        # Check if request was successful
        if response.status_code == 200:
            # Parse JSON
            osupdate = ujson.loads(response.text)
            # Access attributes
            version = osupdate["version"]
            download_url = osupdate["download_url"]
            changelog = osupdate["changelog"]
            # Print the values
            print("Version:", version)
            print("Download URL:", download_url)
            print("Changelog:", changelog)
            handle_update_info(version, download_url, changelog)
        else:
            print("Failed to download JSON. Status code:", response.status_code)
        # Close response
        response.close()
    except Exception as e:
        print("Error:", str(e))
    

main_screen = lv.obj()
install_button = lv.button(main_screen)
install_button.align(lv.ALIGN.TOP_RIGHT, 0, mpos.ui.NOTIFICATION_BAR_HEIGHT)
install_button.add_flag(lv.obj.FLAG.HIDDEN) # button will be shown if there is an update available
install_button.set_size(lv.SIZE_CONTENT, lv.pct(20))
install_label = lv.label(install_button)
install_label.set_text("Update OS")
install_label.center()
status_label = lv.label(main_screen)
status_label.align(lv.ALIGN.TOP_LEFT,0,mpos.ui.NOTIFICATION_BAR_HEIGHT)
mpos.ui.load_screen(main_screen)

network_connected = True
try:
    import network
    network_connected = network.WLAN(network.STA_IF).isconnected()
except Exception as e:
    print("Warning: could not check WLAN status:", str(e))

if not network_connected:
    status_label.set_text("Error: WiFi is not connected.")
    time.sleep(10)
else:
    print("Showing update info...")
    show_update_info()

print("osupdate.py finished")
