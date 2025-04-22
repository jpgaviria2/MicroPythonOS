import lvgl as lv
import time
import random
import display_driver  # Replace with your display driver (e.g., ILI9341, ST7796)

# Configuration
SPINNER_SIZE = 20   # Size of each spinner in pixels
UPDATE_INTERVAL_MS = 1000  # Add spinner and update metrics every 100ms

# Global variables
spinner_count = 0
metrics_label = None

def add_spinner_and_update(timer):
    """Add a new spinner and update on-screen metrics."""
    global spinner_count, metrics_label
    try:
        # Create spinner with only parent argument
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
    
    # Update metrics
    if metrics_label:
        metrics_label.set_text(f"Spinners: {spinner_count}")
    
    print(f"Added spinner {spinner_count}")

def run_benchmark():
    global spinner_count, metrics_label
    print("Starting LVGL spinner benchmark...")
    
    # Initialize LVGL and screen
    try:
        lv.init()
    except Exception as e:
        print(f"Failed to initialize LVGL: {e}")
        return
    
    scr = lv.screen_active()
    scr.set_style_bg_color(lv.color_black(), 0)
    
    # Create metrics label
    try:
        metrics_label = lv.label(scr)
        metrics_label.set_style_text_color(lv.color_white(), 0)
        metrics_label.set_style_bg_color(lv.color_black(), 0)
        metrics_label.set_style_bg_opa(lv.OPA.COVER, 0)
        metrics_label.set_pos(10, 10)
        metrics_label.set_text("Spinners: 0")
    except Exception as e:
        print(f"Failed to create metrics label: {e}")
        return
    
    # Create timer for adding spinners and updating metrics
    try:
        lv.timer_create(add_spinner_and_update, UPDATE_INTERVAL_MS, None)
    except Exception as e:
        print(f"Failed to create timer: {e}")
        return
    
    # Run indefinitely until user resets the board
    try:
        while True:
            lv.task_handler()
            time.sleep_ms(10)  # Yield to LVGL tasks
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    try:
        run_benchmark()
    except Exception as e:
        print(f"Error in benchmark: {e}")
