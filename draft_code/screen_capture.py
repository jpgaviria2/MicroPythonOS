import ustruct
import os
#os.mkdir("/flash")

import lvgl as lv
import micropython
import ustruct

# Capture the screen to a buffer
snapshot_buf = lv.snapshot_take(lv.screen_active(), lv.COLOR_FORMAT.NATIVE)
if snapshot_buf is None:
    print("Failed to capture snapshot")
else:
    print("Snapshot captured successfully")

# Assuming snapshot_buf is from lv.snapshot_take(scr, lv.COLOR_FORMAT.NATIVE)
if snapshot_buf:
    # Verify metadata
    print("Width:", snapshot_buf.header.w)  # Should be 320
    print("Height:", snapshot_buf.header.h)  # Should be 240
    print("Data size:", snapshot_buf.data_size)  # Should be 153600
    # Get the raw buffer pointer
    data_ptr = snapshot_buf.data
    data_size = snapshot_buf.data_size
    # Use memoryview to access the full buffer
    try:
        # Create a memoryview of the C buffer
        buffer = memoryview(data_ptr)[:data_size]
        print("Buffer length:", len(buffer))  # Should be 153600
        # Save to flash storage
        with open("/flash/snapshot.bin", "wb") as f:
            f.write(buffer)
        print("Snapshot saved to /flash/snapshot.bin")
    except Exception as e:
        print("Error accessing or saving buffer:", e)
    # Free the snapshot to avoid memory leaks
    lv.snapshot_free(snapshot_buf)
else:
    print("Snapshot capture failed")





# Assuming snapshot_buf is the lv_img_dsc_t from lv.snapshot_take
if snapshot_buf:
    # Get image data and metadata
    img_data = snapshot_buf.data  # Raw buffer (bytearray)
    img_width = snapshot_buf.header.w
    img_height = snapshot_buf.header.h
    img_data_size = snapshot_buf.data_size
    # Save to flash storage
    try:
        with open("/flash/snapshot.bin", "wb") as f:
            f.write(img_data, img_data_size)
        print("Snapshot saved to /flash/snapshot.bin")
    except OSError as e:
        print("Failed to save snapshot:", e)
else:
    print("No snapshot to save")





if False:
    img_data = snapshot_buf.data
    img_width = snapshot_buf.header.w
    img_height = snapshot_buf.header.h
    img_data_size = snapshot_buf.data_size
    color_format = lv.COLOR_FORMAT.NATIVE  # Store format for reference
    try:
        with open("/flash/snapshot.bin", "wb") as f:
            # Write header: width (4 bytes), height (4 bytes), format (4 bytes)
            f.write(ustruct.pack("III", img_width, img_height, color_format))
            # Write image data
            f.write(img_data, img_data_size)
        print("Snapshot with header saved to /flash/snapshot.bin")
    except OSError as e:
        print("Failed to save snapshot:", e)
