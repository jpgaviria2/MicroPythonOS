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

import time
import hashlib
import os
import _thread

# Configuration
START_SPACING = 2000 # Wait for task bar to go up
TEST_DURATION = 5000  # Duration of each test (ms)
TEST_SPACING = 1000 # Wait between tests (ms)
DATA_SIZE = 1024   # 1KB of data for SHA-256 test
DATA = os.urandom(DATA_SIZE)  # Generate 1KB of random data for SHA-256

def stress_test_busy_loop():
    print("\nStarting busy loop stress test...")
    global summary
    summary += "Busy loop without yield: "
    iterations = 0
    start_time = time.ticks_ms()
    end_time = start_time + TEST_DURATION
    while time.ticks_ms() < end_time and appscreen == lv.screen_active():
        iterations += 1
    duration_ms = time.ticks_diff(time.ticks_ms(), start_time)
    iterations_per_second = (iterations / duration_ms) * 1000
    print(f"Busy loop test ran duration: {duration_ms}, average: {iterations_per_second:.2f} iterations/second")
    summary += f"{iterations_per_second:.2f}/s\n"
    return iterations_per_second


def stress_test_busy_loop_with_yield():
    print("\nStarting busy loop with yield (sleep_ms(0)) stress test...")
    global summary
    summary += "Busy loop with yield: "
    iterations = 0
    start_time = time.ticks_ms()
    end_time = start_time + TEST_DURATION
    while time.ticks_ms() < end_time and appscreen == lv.screen_active():
        iterations += 1
        time.sleep_ms(0)  # Yield to other tasks
    duration_ms = time.ticks_diff(time.ticks_ms(), start_time)
    iterations_per_second = (iterations / duration_ms) * 1000
    print(f"Busy loop with yield test completed: {iterations_per_second:.2f} iterations/second")
    summary += f"{iterations_per_second:.2f}/s\n"
    return iterations_per_second

def stress_test_sha256():
    print("\nStarting SHA-256 stress test (1KB data)...")
    global summary
    summary += "Busy loop with SHA-256 (1KB): "
    iterations = 0
    start_time = time.ticks_ms()
    end_time = start_time + TEST_DURATION
    while time.ticks_ms() < end_time and appscreen == lv.screen_active():
        hashlib.sha256(DATA).digest()  # Compute SHA-256 on 1KB data
        iterations += 1
    duration_ms = time.ticks_diff(time.ticks_ms(), start_time)
    iterations_per_second = (iterations / duration_ms) * 1000
    print(f"SHA-256 test completed: {iterations_per_second:.2f} iterations/second")
    summary += f" {iterations_per_second:.2f}/s\n"
    summary += "\nAll tests completed."
    return iterations_per_second


def update_status_cb(timer):
    status.set_text(summary)


def janitor_cb(timer):
    if lv.screen_active() != appscreen:
        print("cputest.py backgrounded, cleaning up...")
        janitor.delete()
        update_status_timer.delete()
        stress_test_busy_loop_with_yield_timer.delete()

appscreen = lv.screen_active()
janitor = lv.timer_create(janitor_cb, 500, None)
update_status_timer = lv.timer_create(update_status_cb, 200, None)

status = lv.label(appscreen)
status.align(lv.ALIGN.TOP_LEFT, 5, 10)
status.set_style_text_color(lv.color_hex(0xFFFFFF), 0)

summary = "Running 3 CPU tests...\n\n"
status.set_text(summary)

_thread.stack_size(12*1024)
_thread.start_new_thread(stress_test_busy_loop, ())

stress_test_busy_loop_with_yield_timer = lv.timer_create(lambda timer: _thread.start_new_thread(stress_test_busy_loop_with_yield, ()), TEST_DURATION * 2, None)
stress_test_busy_loop_with_yield_timer.set_repeat_count(1)
stress_test_busy_loop_with_yield_timer.set_auto_delete(False)

stress_test_busy_loop_with_yield_timer = lv.timer_create(lambda timer: _thread.start_new_thread(stress_test_sha256, ()), TEST_DURATION * 4, None)
stress_test_busy_loop_with_yield_timer.set_repeat_count(1)
stress_test_busy_loop_with_yield_timer.set_auto_delete(False)

