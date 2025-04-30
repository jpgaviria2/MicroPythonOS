import lvgl as lv
import uasyncio as asyncio
import utime
import gc

# Create a subwindow for the child script (half the 320x240 display)
screen = lv.screen_active()
subwindow = lv.obj(screen)
subwindow.set_size(160, 240)  # Half width, full height
subwindow.align(lv.ALIGN.LEFT_MID, 0, 0)  # Left side
subwindow.set_style_bg_color(lv.color_hex(0xDDDDDD), lv.PART.MAIN)

# Create a label for parent updates
parent_label = lv.label(screen)
parent_label.set_text("Parent: 0")
parent_label.set_style_text_font(lv.font_montserrat_12, 0)
parent_label.align(lv.ALIGN.TOP_RIGHT, -10, 10)

# Create a parent button
parent_button = lv.button(screen)
parent_button.set_size(80, 40)
parent_button.align(lv.ALIGN.BOTTOM_RIGHT, -10, -50)
parent_button_label = lv.label(parent_button)
parent_button_label.set_text("Parent Btn")
parent_button_label.set_style_text_font(lv.font_montserrat_12, 0)

# Create a parent slider
parent_slider = lv.slider(screen)
parent_slider.set_size(100, 10)
parent_slider.set_range(0, 100)
parent_slider.align(lv.ALIGN.BOTTOM_RIGHT, -10, -10)

# Parent button callback
def parent_button_cb(e):
    print("Parent button clicked")

parent_button.add_event_cb(parent_button_cb, lv.EVENT.CLICKED, None)

# Parent slider callback
def parent_slider_cb(e):
    value = parent_slider.get_value()
    print("Parent slider value:", value)

parent_slider.add_event_cb(parent_slider_cb, lv.EVENT.VALUE_CHANGED, None)

# Function to execute the child script as a coroutine
async def execute_script(script_source, lvgl_obj):
    try:
        script_globals = {
            'lv': lv,
            'subwindow': lvgl_obj,
            'asyncio': asyncio,
            'utime': utime
        }
        print("Child script: Compiling")
        code = compile(script_source, "<string>", "exec")
        exec(code, script_globals)
        update_child = script_globals.get('update_child')
        if update_child:
            print("Child script: Starting update_child")
            await update_child()
        else:
            print("Child script error: No update_child function defined")
    except Exception as e:
        print("Child script error:", e)

# Child script buffer: updates label, adds button and slider
script_buffer = """
import asyncio
async def update_child():
    print("Child coroutine: Creating UI")
    # Label
    label = lv.label(subwindow)
    label.set_text("Child: 0")
    label.set_style_text_font(lv.font_montserrat_12, 0)
    label.align(lv.ALIGN.TOP_MID, 0, 10)
    # Button
    button = lv.button(subwindow)
    button.set_size(80, 40)
    button.align(lv.ALIGN.BOTTOM_MID, 0, -50)
    button_label = lv.label(button)
    button_label.set_text("Child Btn")
    button_label.set_style_text_font(lv.font_montserrat_12, 0)
    # Slider
    slider = lv.slider(subwindow)
    slider.set_size(100, 10)
    slider.set_range(0, 100)
    slider.align(lv.ALIGN.BOTTOM_MID, 0, -10)
    # Button callback
    def button_cb(e):
        print("Child button clicked")
    button.add_event_cb(button_cb, lv.EVENT.CLICKED, None)
    # Slider callback
    def slider_cb(e):
        value = slider.get_value()
        print("Child slider value:", value)
    slider.add_event_cb(slider_cb, lv.EVENT.VALUE_CHANGED, None)
    # Update loop
    count = 0
    while True:
        count += 1
        print("Child coroutine: Updating label to", count)
        label.set_text(f"Child: {count}")
        await asyncio.sleep_ms(2000)  # Update every 2s
"""

# Parent coroutine: updates parent label every 1 second
async def update_parent():
    count = 0
    while True:
        count += 1
        print("Parent coroutine: Updating label to", count)
        parent_label.set_text(f"Parent: {count}")
        gc.collect()
        print("Parent coroutine: Free memory:", gc.mem_free())
        await asyncio.sleep_ms(1000)  # Update every 1s

# Main async function to run all tasks
async def main():
    print("Main: Starting tasks")
    asyncio.create_task(update_parent())
    asyncio.create_task(execute_script(script_buffer, subwindow))
    while True:
        await asyncio.sleep_ms(100)

# Run the event loop
gc.collect()
print("Free memory before loop:", gc.mem_free())
try:
    asyncio.run(main())
except Exception as e:
    print("Main error:", e)

