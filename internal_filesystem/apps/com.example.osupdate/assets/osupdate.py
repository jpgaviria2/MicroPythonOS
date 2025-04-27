import lvgl as lv
import ota.update
from esp32 import Partition
import urequests

import lvgl as lv
from esp32 import Partition
import urequests
import hashlib
import machine

subwindow.clean()
canary = lv.obj(subwindow)
canary.add_flag(lv.obj.FLAG.HIDDEN)


import ota.status
ota.status.status()
current = Partition(Partition.RUNNING)
current
current.get_next_update()


# Assuming subwindow is defined elsewhere
# subwindow.clean()

# Initialize LVGL display
label = lv.label(subwindow)
label.set_text("OTA Update: 0.00%")
label.align(lv.ALIGN.CENTER, 0, 0)
progress_bar = lv.bar(lv.screen_active())
progress_bar.set_size(200, 20)
progress_bar.align(lv.ALIGN.BOTTOM_MID, 0, -20)
progress_bar.set_range(0, 100)
progress_bar.set_value(0, lv.ANIM.OFF)

# Custom OTA update with LVGL progress
def update_with_lvgl(url, expected_sha256=None):
    def progress_callback(percent):
        print(f"OTA Update: {percent:.1f}%")
        label.set_text(f"OTA Update: {percent:.2f}%")
        progress_bar.set_value(int(percent), lv.ANIM.ON)
        lv.task_handler()  # Ensure LVGL updates the display

    # Free memory before starting
    import gc
    gc.collect()

    # Get partition information
    current = Partition(Partition.RUNNING)
    next_partition = current.get_next_update()
    print("Current partition:", current.info())
    print("Next partition:", next_partition.info())

    # Validate partition size
    partition_size = next_partition.ioctl(4, 0) * 4096  # Total sectors * sector size
    response = urequests.get(url, stream=True)
    total_size = int(response.headers.get('Content-Length', 0))
    if total_size > partition_size:
        print(f"Error: Firmware size {total_size} exceeds partition size {partition_size}")
        response.close()
        return
    print(f"Starting OTA update of size: {total_size}")

    # Initialize SHA256 hash
    sha256 = hashlib.sha256() if expected_sha256 else None

    bytes_written = 0
    chunk_size = 4096
    i = 0
    while True:
        chunk = response.raw.read(chunk_size)
        if not chunk:
            break
        print(f"Writing chunk {i}, size: {len(chunk)} bytes")
        # Pad the chunk if it's smaller than 4096 bytes
        if len(chunk) < chunk_size:
            print(f"Padding chunk {i} from {len(chunk)} to {chunk_size} bytes")
            chunk = chunk + b'\xFF' * (chunk_size - len(chunk))
        # Update hash
        if sha256:
            sha256.update(chunk)
        try:
            next_partition.writeblocks(i, chunk)
        except OSError as e:
            print(f"Error writing chunk {i}: {e}")
            response.close()
            return
        bytes_written += len(chunk)
        i += 1
        if total_size:
            progress_callback(bytes_written / total_size * 100)

    response.close()
    print(f"OTA update complete, wrote {bytes_written} bytes")

    # Verify checksum if provided
    if sha256 and expected_sha256:
        computed_sha256 = sha256.hexdigest()
        if computed_sha256 != expected_sha256:
            print(f"Checksum mismatch: expected {expected_sha256}, got {computed_sha256}")
            return
        print("Checksum verified successfully")

    # Set the boot partition
    try:
        next_partition.set_boot()
        print("Boot partition set to:", next_partition.info())
        print("Current boot partition:", Partition(Partition.BOOT).info())
    except OSError as e:
        print(f"Error setting boot partition: {e}")
        return

    # Mark the new partition as valid to prevent rollback
    try:
        Partition.mark_app_valid_cancel_rollback()
        print("Marked new partition as valid")
    except OSError as e:
        print(f"Error marking partition as valid: {e}")
        return

    # Reboot
    print("Rebooting to new firmware...")
    machine.reset()

# Example usage
# Replace with your firmware URL and SHA256 checksum (if available)
update_with_lvgl("http://demo.lnpiggy.com:2121/ESP32_GENERIC_S3-SPIRAM_OCT_micropython.bin", expected_sha256="c167de508c354724e97857ed4bd5c5608f383302399a506d2a16d6ee0cab08ce")
lvgl_micropy_ESP32_GENERIC_S3-SPIRAM_OCT-16.bin

# Start OTA update
#update_with_lvgl("http://demo.lnpiggy.com:2121/latest.bin")
