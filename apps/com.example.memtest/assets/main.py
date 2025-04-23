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

import gc
import time

# Configuration
ALLOCATION_TIMEOUT_MS = 100  # Timeout for a single allocation (in milliseconds)


def test_allocation(buffer_size, n):
    """Test how many buffers of a given size can be allocated with a timeout."""
    print(f"\nTesting buffer size: {buffer_size} bytes (2^{n})")
    buffers = []
    count = 0
    
    try:
        while canary.is_valid():
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
    except MemoryError:
        print(f"\nStopped after allocating {count} buffers of {buffer_size} bytes: MemoryError")
    except Exception as e:
        print(f"\nStopped after allocating {count} buffers of {buffer_size} bytes: {e}")
    
    # Free allocated buffers
    buffers.clear()
    gc.collect()
    return count


# Test buffer sizes of 2^n, starting from n=1 (2 bytes)
n = 1

subwindow.clean()
canary = lv.obj(subwindow)
canary.add_flag(lv.obj.FLAG.HIDDEN)

status = lv.label(subwindow)
status.align(lv.ALIGN.TOP_LEFT, 5, 10)
status.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
status.set_style_text_font(lv.font_unscii_8, 0)

summary = "Running RAM memory tests...\n\n"
summary += "=== Memory Allocation Test Summary ===\n"
summary += "Buffer Size (bytes) | Max Allocated\n"
summary += "-" * 30 + "\n"
status.set_text(summary)

while canary.is_valid():
   buffer_size = 2 ** n
   summary += f"{buffer_size:>12} | "
   status.set_text(summary)
   # Run allocation test
   gc.collect()
   max_buffers = test_allocation(buffer_size, n)
   # Check if we allocated 0 buffers (indicates we can't allocate this size)
   if max_buffers == 0:
       print(f"Cannot allocate buffers of size {buffer_size} bytes. Stopping test.")
       summary += f"{max_buffers:>14}\n"
       status.set_text(summary)
       break
   # Clean up memory before next test
   gc.collect()
   time.sleep_ms(100)  # Brief delay to stabilize system
   n += 1
   summary += f"{max_buffers:>14}\n"
   status.set_text(summary)

# Print summary report
summary += "\n=====================================\n\n"
summary += "Test completed.\n"
status.set_text(summary)
