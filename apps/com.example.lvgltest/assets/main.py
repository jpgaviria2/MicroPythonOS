import lvgl as lv
import time
import random
import display_driver  # Replace with your display driver (e.g., ILI9341, ST7796)

# Configuration
SPRITE_SIZE = 20   # Size of each sprite (rectangle) in pixels
UPDATE_INTERVAL_MS = 100  # Update metrics display and add sprite every 100ms

# Global variables
sprite_count = 0
metrics_label = None

def update_metrics(timer):
    """Update on-screen metrics (sprite count)."""
    global sprite_count, metrics_label
    if metrics_label:
        metrics_label.set_text(f"Sprites: {sprite_count}")

def create_sprite(parent, index):
    """Create a single animated sprite (rectangle)."""
    sprite = lv.obj(parent)
    sprite.set_size(SPRITE_SIZE, SPRITE_SIZE)
    sprite.set_style_bg_color(lv.color_hex(random.randint(0, 0xFFFFFF)), 0)
    sprite.set_pos(random.randint(0, lv.screen_active().get_width() - SPRITE_SIZE),
                   random.randint(0, lv.screen_active().get_height() - SPRITE_SIZE))
    
    try:
        # Create animation for random movement in X
        anim = lv.anim_t()
        anim.init()
        anim.set_var(sprite)
        anim.set_time(1000)  # Animation duration (ms)
        anim.set_repeat_count(lv.ANIM_REPEAT_INFINITE)
        x_start = sprite.get_x()
        x_end = random.randint(0, lv.screen_active().get_width() - SPRITE_SIZE)
        anim.set_values(x_start, x_end)
        anim.set_path_cb(lv.anim_t.path_ease_in_out)
        # Use direct method call to avoid callback issues
        def x_cb(anim, val):
            anim.get_var().set_x(val)
        anim.set_exec_cb(x_cb)
        lv.anim_t.start(anim)
        
        # Create animation for random movement in Y
        anim_y = lv.anim_t()
        anim_y.init()
        anim_y.set_var(sprite)
        anim_y.set_time(1000)
        anim_y.set_repeat_count(lv.ANIM_REPEAT_INFINITE)
        y_start = sprite.get_y()
        y_end = random.randint(0, lv.screen_active().get_height() - SPRITE_SIZE)
        anim_y.set_values(y_start, y_end)
        anim_y.set_path_cb(lv.anim_t.path_ease_in_out)
        def y_cb(anim, val):
            anim.get_var().set_y(val)
        anim_y.set_exec_cb(y_cb)
        lv.anim_t.start(anim_y)
    except Exception as e:
        print(f"Failed to create animation for sprite {index}: {e}")
        sprite.delete()
        return None
    
    return sprite

def run_benchmark():
    global sprite_count, metrics_label
    print("Starting LVGL animation benchmark...")
    
    # Initialize LVGL and screen
    try:
        lv.init()
    except Exception as e:
        print(f"Failed to initialize LVGL: {e}")
        return
    
    scr = lv.screen_active()
    scr.set_style_bg_color(lv.color_black(), 0)
    
    # Create metrics label
    metrics_label = lv.label(scr)
    metrics_label.set_style_text_color(lv.color_white(), 0)
    metrics_label.set_style_bg_color(lv.color_black(), 0)
    metrics_label.set_style_bg_opa(lv.OPA.COVER, 0)
    metrics_label.set_pos(10, 10)
    metrics_label.set_text("Sprites: 0")
    
    # Create timer for updating metrics and adding sprites
    def add_sprite_and_update(timer):
        global sprite_count
        sprite = create_sprite(scr, sprite_count)
        if sprite:
            sprite_count += 1
            print(f"Added sprite {sprite_count}")
        update_metrics(timer)
    
    try:
        lv.timer_create(add_sprite_and_update, UPDATE_INTERVAL_MS, None)
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


