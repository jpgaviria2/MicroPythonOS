import lvgl as lv
import ota.update
from esp32 import Partition
import urequests

subwindow.clean()
canary = lv.obj(subwindow)
canary.add_flag(lv.obj.FLAG.HIDDEN)

import ota.status
ota.status.status()
current = Partition(Partition.RUNNING)
current
next_partition = current.get_next_update()
next_partition

label = lv.label(subwindow)
label.set_text("OS Update: 0.00%")
label.align(lv.ALIGN.CENTER, 0, -30)

progress_bar = lv.bar(subwindow)
progress_bar.set_size(200, 20)
progress_bar.align(lv.ALIGN.BOTTOM_MID, 0, -50)
progress_bar.set_range(0, 100)
progress_bar.set_value(0, lv.ANIM.OFF)

# Custom OTA update with LVGL progress
def update_with_lvgl(url):
    def progress_callback(percent):
        print(f"OTA Update: {percent:.1f}%")
        label.set_text(f"OTA Update: {percent:.2f}%")
        progress_bar.set_value(int(percent), lv.ANIM.ON)
    current = Partition(Partition.RUNNING)
    next_partition = current.get_next_update()
    response = urequests.get(url, stream=True)
    total_size = int(response.headers.get('Content-Length', 0))
    bytes_written = 0
    chunk_size = 4096
    i = 0
    print(f"Starting OTA update of size: {total_size}")
    while canary.is_valid():
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
    next_partition.set_boot()
    import machine
    machine.reset()

# Start OTA update
update_with_lvgl("http://demo.lnpiggy.com:2121/latest.bin")
