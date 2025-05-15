appscreen = lv.screen_active()

import time
import random

# Configuration
SPINNER_SIZE = 40   # Size of each spinner in pixels

# Global variables
spinner_count = 0
metrics_label = None

def add_spinner_and_update(timer):
    global spinner_count, metrics_label
    try:
        x = random.randint(0, appscreen.get_width() - SPINNER_SIZE)
        y = random.randint(0, appscreen.get_height() - SPINNER_SIZE)
        spinner_count += 1
        print(f"Placing spinner {spinner_count} with size {SPINNER_SIZE} at {x},{y}")
        spinner = lv.spinner(appscreen)
        spinner.set_size(SPINNER_SIZE, SPINNER_SIZE)
        spinner.set_pos(x, y)
    except Exception as e:
        print(f"Failed to create spinner {spinner_count}: {e}")
        return
    
    metrics_label.set_text(f"Spinners: {spinner_count}")
    print(f"Finished adding spinner {spinner_count}")

def run_benchmark():
    global spinner_count, metrics_label
    print("Starting LVGL spinner benchmark...")
    metrics_label = lv.label(appscreen)
    metrics_label.set_style_text_color(lv.color_white(), 0)
    metrics_label.set_style_bg_color(lv.color_black(), 0)
    metrics_label.set_style_bg_opa(lv.OPA.COVER, 0)
    metrics_label.set_pos(10, 10)
    metrics_label.set_text("Spinners: 0")
    timer = lv.timer_create(add_spinner_and_update, 2000, None)
    th.disable() # taskhandler control is necessary, otherwise there are concurrency issues
    while appscreen == lv.screen_active():
        lv.task_handler()
        time.sleep_ms(10)
        lv.tick_inc(10)
    th.enable()
    timer.delete()

try:
    run_benchmark()
except Exception as e:
    print(f"Error in benchmark: {e}")

print("lvgltest.py exiting")
