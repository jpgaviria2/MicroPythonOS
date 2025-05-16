# Example results for ESP32-S3 with 8MB SPIRAM:
#
#=== Memory Allocation Test Summary ===
#Buffer Size (bytes) | Max Buffers Allocated
#----------------------------------------
#                 2 |                25762
#                 4 |                25760
#                 8 |                25771
#                16 |                25759
#                32 |                35541
#                64 |                11276
#               128 |                 6517
#               256 |                 3521
#               512 |                 1832
#              1024 |                  932
#              2048 |                  466
#              4096 |                  232
#              8192 |                  115
#             16384 |                   56
#             32768 |                   26
#             65536 |                   12
#            131072 |                    9
#            262144 |                    4
#            524288 |                    2
#           1048576 |                    1
#           2097152 |                    0
#=====================================
#
# On desktop, this hangs while outputting, for some reason...

import gc
import time
import _thread

# Configuration
ALLOCATION_TIMEOUT_MS = 100  # Timeout for a single allocation (in milliseconds)
keep_running = True

def test_allocation(buffer_size, n):
    """Test how many buffers of a given size can be allocated with a timeout."""
    print(f"\nTesting buffer size: {buffer_size} bytes (2^{n})")
    buffers = []
    count = 0
    
    try:
        while keep_running:
            # Measure time for allocation
            start_time = time.ticks_ms()
            # Allocate a new buffer
            buffer = bytearray(buffer_size)
            allocation_time = time.ticks_diff(time.ticks_ms(), start_time)
            
            # Check if allocation took too long
            if allocation_time > ALLOCATION_TIMEOUT_MS:
                print(f"\nStopped after allocating {count} buffers of {buffer_size} bytes: Allocation timeout ({allocation_time}ms > {ALLOCATION_TIMEOUT_MS}ms)")
                break
            
            buffers.append(buffer)
            count += 1
            # Print progress every 100 allocations to avoid flooding serial
            if count % 100 == 0:
                print(f"Allocated {count} buffers of {buffer_size} bytes", end="\r")
    except MemoryError as e:
        buffers.clear()
        print(f"\nStopped after allocating {count} buffers of {buffer_size} bytes: MemoryError")
    except Exception as e:
        buffers.clear()
        print(f"\nStopped after allocating {count} buffers of {buffer_size} bytes: {e}")
    
    # Free allocated buffers
    buffers.clear()
    gc.collect()
    return count

def stress_test_thread():
    summary = "Running RAM memory tests...\n\n"
    summary += "Buffer Size (bytes) | Max Allocated\n"
    summary += "-----------------------------------\n"
    lv.async_call(lambda l: status.set_text(summary), None)
    # Test buffer sizes of 2^n, starting from n=1 (2 bytes)
    n = 1        
    while keep_running:
        buffer_size = 2 ** n
        summary += f"{buffer_size:>12} | "
        #lv.async_call(lambda l: status.set_text(summary), None)
        # Run allocation test
        gc.collect()
        max_buffers = test_allocation(buffer_size, n)
        # Check if we allocated 0 buffers (indicates we can't allocate this size)
        if max_buffers == 0:
            print(f"Cannot allocate buffers of size {buffer_size} bytes. Stopping test.")
            summary += f"{max_buffers:>14}\n"
            #lv.async_call(lambda l: status.set_text(summary), None)
            break
        # Clean up memory before next test
        gc.collect()
        n += 1
        summary += f"{max_buffers:>14}\n"
        lv.async_call(lambda l: status.set_text(summary), None)
        time.sleep_ms(200)  # Brief delay to stabilize system
    # Print summary report
    summary += "\n"
    summary += "===================================\n"
    summary += "Test completed.\n"
    lv.async_call(lambda l: status.set_text(summary), None)



def janitor_cb(timer):
    global keep_running
    if lv.screen_active() != appscreen:
        print("memtest.py backgrounded, cleaning up...")
        janitor.delete()
        keep_running = False

appscreen = lv.screen_active()
status = lv.label(appscreen)
status.align(lv.ALIGN.TOP_LEFT, 5, 10)
status.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
status.set_style_text_font(lv.font_unscii_8, 0)

_thread.stack_size(12*1024)
_thread.start_new_thread(stress_test_thread, ())

janitor = lv.timer_create(janitor_cb, 400, None)
