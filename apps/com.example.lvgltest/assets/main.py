import time
import random

# Configuration
SPINNER_SIZE = 20   # Size of each spinner in pixels
UPDATE_INTERVAL_MS = 3000  # Add spinner and update metrics every 100ms

# Global variables
spinner_count = 0
metrics_label = None

canary = lv.obj(subwindow)
canary.add_flag(0x0001) # LV_OBJ_FLAG_HIDDEN is 0x0001

def add_spinner_and_update():
    global spinner_count, metrics_label
    try:
        spinner = lv.spinner(lv.screen_active())
        spinner.set_size(SPINNER_SIZE, SPINNER_SIZE)
        spinner.set_pos(
            random.randint(0, lv.screen_active().get_width() - SPINNER_SIZE),
            random.randint(0, lv.screen_active().get_height() - SPINNER_SIZE)
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
    
    scr = lv.screen_active()
    scr.set_style_bg_color(lv.color_black(), 0)
    
    metrics_label = lv.label(scr)
    metrics_label.set_style_text_color(lv.color_white(), 0)
    metrics_label.set_style_bg_color(lv.color_black(), 0)
    metrics_label.set_style_bg_opa(lv.OPA.COVER, 0)
    metrics_label.set_pos(10, 10)
    metrics_label.set_text("Spinners: 0")
    
    while canary.get_class():
        add_spinner_and_update()
        time.sleep_ms(UPDATE_INTERVAL_MS)

       
try:
    run_benchmark()
except Exception as e:
    print(f"Error in benchmark: {e}")
