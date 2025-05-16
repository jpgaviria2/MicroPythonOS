import time
import random

# Configuration
SPINNER_SIZE = 40   # Size of each spinner in pixels

# Global variables
spinner_count = 0
metrics_label = None

def add_spinner(timer):
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


def janitor_cb(timer):
    if lv.screen_active() != appscreen:
        print("lvgltest.py backgrounded, cleaning up...")
        janitor.delete()
        add_spinner_timer.delete()

appscreen = lv.screen_active()
metrics_label = lv.label(appscreen)
metrics_label.set_style_text_color(lv.color_white(), 0)
metrics_label.set_style_bg_color(lv.color_black(), 0)
metrics_label.set_style_bg_opa(lv.OPA.COVER, 0)
metrics_label.set_pos(10, 10)
metrics_label.set_text("Spinners: 0")

print("Starting LVGL spinner benchmark...")
janitor = lv.timer_create(janitor_cb, 400, None)
add_spinner_timer = lv.timer_create(add_spinner, 2000, None)

