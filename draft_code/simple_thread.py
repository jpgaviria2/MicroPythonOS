import _thread

# Function to execute the child script as a coroutine
def execute_script(script_source, lvgl_obj):
    try:
        script_globals = {
            'lv': lv,
            'subwindow': lvgl_obj,
        }
        print("Child script: Compiling")
        code = compile(script_source, "<string>", "exec")
        exec(code, script_globals)
        app_main = script_globals.get('app_main')
        if app_main:
            print("Child script: Starting app_main")
            app_main()
            print("Script finished!")
        else:
            print("Child script error: No app_main function defined")
    except Exception as e:
        print("Child script error:", e)


# Child script buffer: updates label, adds button and slider
script_buffer = """
import time
def app_main():
    print("Child coroutine: Creating UI")
    # Label
    label = lv.label(subwindow)
    label.set_text("Child: 0")
    label.set_style_text_font(lv.font_montserrat_12, 0)
    label.align(lv.ALIGN.TOP_MID, 0, 10)
    # Button
    button = lv.button(subwindow)
    button.set_size(80, 40)
    button.align(lv.ALIGN.CENTER, 0, 0)
    button_label = lv.label(button)
    button_label.set_text("Quit")
    button_label.set_style_text_font(lv.font_montserrat_12, 0)
    # Slider
    slider = lv.slider(subwindow)
    slider.set_range(0, 100)
    slider.align(lv.ALIGN.BOTTOM_MID, 0, -30)
    # Quit flag
    should_continue = True
    # Button callback
    def button_cb(e):
        nonlocal should_continue
        print("Quit button clicked, exiting child")
        should_continue = False
    button.add_event_cb(button_cb, lv.EVENT.CLICKED, None)
    # Slider callback
    def slider_cb(e):
        value = slider.get_value()
        print("Child slider value:", value)
    slider.add_event_cb(slider_cb, lv.EVENT.VALUE_CHANGED, None)
    # Update loop
    count = 0
    while should_continue:
        count += 1
        print("Child coroutine: Updating label to", count)
        label.set_text(f"Child: {count}")
        time.sleep_ms(1000)
    print("Child coroutine: Exiting")
"""


# Start the event loop in a background thread
gc.collect()
print("Free memory before loop:", gc.mem_free())
try:
    _thread.stack_size(8192)
    _thread.start_new_thread(execute_script, (script_buffer, subwindow))
    print("Event loop started in background thread")
except Exception as e:
    print("Error starting event loop thread:", e)
