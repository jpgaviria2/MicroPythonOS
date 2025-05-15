appscreen == lv.screen_active()

import time
import random

# Configuration
SPINNER_SIZE = 40   # Size of each spinner in pixels

# Global variables
spinner_count = 0
metrics_label = None



def add_spinner_and_update():
    global spinner_count, metrics_label
    try:
        spinner = lv.spinner(appscreen)
        spinner.set_size(SPINNER_SIZE, SPINNER_SIZE)
        spinner.set_pos(
            random.randint(0, appscreen.get_width() - SPINNER_SIZE),
            random.randint(0, appscreen.get_height() - SPINNER_SIZE)
        )
        spinner_count += 1
    except Exception as e:
        print(f"Failed to create spinner {spinner_count + 1}: {e}")
        return
    
    metrics_label.set_text(f"Spinners: {spinner_count}")
    print(f"Added spinner {spinner_count}")

def run_benchmark():
    global spinner_count, metrics_label
    print("Starting LVGL spinner benchmark...")
    
    scr = appscreen
    scr.set_style_bg_color(lv.color_black(), 0)
    
    metrics_label = lv.label(scr)
    metrics_label.set_style_text_color(lv.color_white(), 0)
    metrics_label.set_style_bg_color(lv.color_black(), 0)
    metrics_label.set_style_bg_opa(lv.OPA.COVER, 0)
    metrics_label.set_pos(10, 10)
    metrics_label.set_text("Spinners: 0")
    
    while appscreen == lv.screen_active():
        add_spinner_and_update()
        time.sleep(4)

       
try:
    run_benchmark()
except Exception as e:
    print(f"Error in benchmark: {e}")

print("lvgltest.py exiting")
