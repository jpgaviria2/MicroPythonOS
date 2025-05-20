# Example results for ESP32-S3 with 8MB SPIRAM:
#
# Test Summary:
# Busy loop: 153018.20 iterations/second
# Busy loop with yield: 40303.37 iterations/second
# SHA-256 (1KB): 7357.60 iterations/second
#
# Adding the appscreen == lv.screen_active() test reduces the results to:
# Busy loop: 22289 iterations/second
# Busy loop with yield: 15923 iterations/second
# SHA-256 (1KB): 5269 iterations/second
#
# New way, with the tests in a thread, replacing appscreen == lv.screen_active() with keeprunning:
# Busy loop: 127801 iterations/second
# Busy loop with yield: 38394 iterations/second
# SHA-256 (1KB): 5012 iterations/second
#
# New way, but now with 10 in a loop and 10 second tests for more stability:
# Busy loop: 127000 iterations/second
# Busy loop with yield: 46000 iterations/second => this went up 25%
# SHA-256 (1KB): 5100 iterations/second
#
# When the nostr thing is hanging:
# Busy loop: 102000 iterations/second
# Busy loop with yield: 12000 iterations/second => this went down 70%!
# SHA-256 (1KB): 5100 iterations/second
#
# Results on desktop:
# Busy loop: 15 997 000 => 125x faster
# Busy loop with yield: 10 575 000 => 229x faster
# SHA-256 (1KB): 291 000 => 57x faster


import time
import hashlib
import os
import _thread

keeprunning = True
summary = "Running 3 CPU tests...\n\n"

# Configuration
START_SPACING = 2000 # Wait for system to settle
TEST_DURATION = 10000  # Duration of each test (ms)
TEST_SPACING = 1000 # Wait between tests (ms)

def stress_test_thread():
    DATA_SIZE = 1024   # 1KB of data for SHA-256 test
    DATA = os.urandom(DATA_SIZE)  # Generate 1KB of random data for SHA-256
    print("stress_test_thread running")
    global summary, keeprunning
    summary += "Waiting for system to settle...\n\n"
    time.sleep_ms(START_SPACING)
    summary += "Busy loop without yield: "
    iterations = 0
    start_time = time.ticks_ms()
    end_time = start_time + TEST_DURATION
    while time.ticks_ms() < end_time and keeprunning:
        iterations += 1
    duration_ms = time.ticks_diff(time.ticks_ms(), start_time)
    iterations_per_second = (iterations / duration_ms) * 1000
    print(f"Busy loop test ran duration: {duration_ms}, average: {iterations_per_second:.2f} iterations/second")
    summary += f"{iterations_per_second:.2f}/s\n"
    #
    time.sleep_ms(TEST_SPACING)
    print("\nStarting busy loop with yield (sleep_ms(0)) stress test...")
    summary += "Busy loop with yield: "
    iterations = 0
    start_time = time.ticks_ms()
    end_time = start_time + TEST_DURATION
    while time.ticks_ms() < end_time and keeprunning:
        for _ in range(10):
            time.sleep_ms(0)  # Yield to other tasks
        iterations += 10
    duration_ms = time.ticks_diff(time.ticks_ms(), start_time)
    iterations_per_second = (iterations / duration_ms) * 1000
    print(f"Busy loop with yield test completed: {iterations_per_second:.2f} iterations/second")
    summary += f"{iterations_per_second:.2f}/s\n"
    #
    time.sleep_ms(TEST_SPACING)
    print("\nStarting SHA-256 stress test (1KB data)...")
    summary += "Busy loop with SHA-256 (1KB): "
    iterations = 0
    start_time = time.ticks_ms()
    end_time = start_time + TEST_DURATION
    while time.ticks_ms() < end_time and keeprunning:
        for _ in range(10):
            hashlib.sha256(DATA).digest()  # Compute SHA-256 on 1KB data
        iterations += 10
    duration_ms = time.ticks_diff(time.ticks_ms(), start_time)
    iterations_per_second = (iterations / duration_ms) * 1000
    print(f"SHA-256 test completed: {iterations_per_second:.2f} iterations/second")
    summary += f" {iterations_per_second:.2f}/s\n"
    summary += "\nAll tests completed."


def janitor_cb(timer):
    global keeprunning
    if lv.screen_active() != appscreen:
        print("cputest.py backgrounded, cleaning up...")
        janitor.delete()
        keeprunning = False
        update_status_timer.delete()

appscreen = lv.screen_active()
janitor = lv.timer_create(janitor_cb, 1000, None)
update_status_timer = lv.timer_create(lambda timer: status.set_text(summary), 750, None)

status = lv.label(appscreen)
status.align(lv.ALIGN.TOP_LEFT, 5, 10)
status.set_text(summary)

_thread.stack_size(12*1024)
_thread.start_new_thread(stress_test_thread, ())
