import lcd_bus
import lvgl as lv
import sdl_display
import task_handler
import sys
sys.path.append('lib/')
import sdl_pointer
import sdl_keyboard

# Initialize display
TFT_HOR_RES = 320
TFT_VER_RES = 240
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

# Create group
group = lv.group_create()
group.set_default()
keyboard.set_group(group)

# Create widgets
screen = lv.screen_active()

# Textarea
ta = lv.textarea(screen)
ta.set_one_line(True)
ta.set_placeholder_text("Type here")
ta.align(lv.ALIGN.TOP_LEFT, 10, 10)
group.add_obj(ta)

# Switch
sw = lv.switch(screen)
sw.align(lv.ALIGN.TOP_LEFT, 10, 50)
group.add_obj(sw)

# Test Button
btn = lv.button(screen)
btn.align(lv.ALIGN.TOP_LEFT, 10, 90)
lbl = lv.label(btn)
lbl.set_text("Test Button")
group.add_obj(btn)

# Simulate NEXT key button
btn_next = lv.button(screen)
btn_next.align(lv.ALIGN.BOTTOM_LEFT, 10, -10)
lbl_next = lv.label(btn_next)
lbl_next.set_text("NEXT")
def btn_next_cb(event):
    if event.get_code() == lv.EVENT.CLICKED:
        keyboard._keypad_cb(None, 1, 9, 0)  # Simulate KEY_TAB (lv.KEY.NEXT) press
        keyboard._keypad_cb(None, 0, 9, 0)  # Simulate release
btn_next.add_event_cb(btn_next_cb, lv.EVENT.CLICKED, None)

# Simulate ENTER key button
btn_enter = lv.button(screen)
btn_enter.align(lv.ALIGN.BOTTOM_LEFT, 100, -10)
lbl_enter = lv.label(btn_enter)
lbl_enter.set_text("ENTER")
def btn_enter_cb(event):
    if event.get_code() == lv.EVENT.CLICKED:
        keyboard._keypad_cb(None, 1, 13, 0)  # Simulate KEY_RETURN (lv.KEY.ENTER) press
        keyboard._keypad_cb(None, 0, 13, 0)  # Simulate release
btn_enter.add_event_cb(btn_enter_cb, lv.EVENT.CLICKED, None)

# Debug focus
def check_focus():
    focused = lv.group_get_focused(group)
    print(f"Focused widget: {focused}")
th = task_handler.TaskHandler(duration=5)
th.register_task(check_focus, 1000)

# Debug events
def event_cb(event, name):
    event_code = event.get_code()
    print(f"{name} event: code={event_code}, name={getattr(lv, 'EVENT_' + str(event_code), 'UNKNOWN')}")
ta.add_event_cb(lambda e: event_cb(e, "Textarea"), lv.EVENT.ALL, None)
sw.add_event_cb(lambda e: event_cb(e, "Switch"), lv.EVENT.ALL, None)
btn.add_event_cb(lambda e: event_cb(e, "Button"), lv.EVENT.ALL, None)
