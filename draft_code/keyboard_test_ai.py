import lcd_bus
import lvgl as lv
import sdl_display
import task_handler
import sys
sys.path.append('lib/')
import mpos.ui
import sdl_pointer
import sdl_keyboard

# Display resolution
TFT_HOR_RES = 320
TFT_VER_RES = 240

# Initialize display
bus = lcd_bus.SDLBus(flags=0)
buf1 = bus.allocate_framebuffer(TFT_HOR_RES * TFT_VER_RES * 2, 0)
display = sdl_display.SDLDisplay(
    data_bus=bus,
    display_width=TFT_HOR_RES,
    display_height=TFT_VER_RES,
    frame_buffer1=buf1,
    color_space=lv.COLOR_FORMAT.RGB565
)
display.init()

# Initialize mouse
mouse = sdl_pointer.SDLPointer()

# Initialize keyboard
keyboard = sdl_keyboard.SDLKeyboard()

# Create group for input devices
group = lv.group_create()
keyboard.set_group(group)


# Create textarea
screen = lv.screen_active()
ta = lv.textarea(screen)
ta.set_one_line(True)
ta.align(lv.ALIGN.TOP_LEFT, 0, 0)
ta.set_placeholder_text("Type here")
group.add_obj(ta)

# Optional: Debug event callback for textarea
def ta_event_cb(event):
    event_code = event.get_code()
    name = mpos.ui.get_event_name(event_code)
    print(f"Textarea event: code={event_code}, name={name}")

ta.add_event_cb(ta_event_cb, lv.EVENT.ALL, None)

# Optional: Create an on-screen keyboard
keyboard_widget = lv.keyboard(screen)
keyboard_widget.set_textarea(ta)
keyboard_widget.add_flag(lv.obj.FLAG.HIDDEN)

def ta_focus_cb(event):
    event_code = event.get_code()
    if event_code == lv.EVENT.FOCUSED:
        keyboard_widget.clear_flag(lv.obj.FLAG.HIDDEN)
    elif event_code == lv.EVENT.DEFOCUSED:
        keyboard_widget.add_flag(lv.obj.FLAG.HIDDEN)

ta.add_event_cb(ta_focus_cb, lv.EVENT.FOCUSED | lv.EVENT.DEFOCUSED, None)

# Task handler
th = task_handler.TaskHandler(duration=5)  # 5ms for desktop
