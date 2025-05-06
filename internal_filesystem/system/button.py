print("button.py running")

from machine import Pin, Timer
import time
import _thread

# Configure IO0 as input with pull-up resistor
button = Pin(0, Pin.IN, Pin.PULL_UP)

# Variables for long press detection
long_press_duration = 4000
press_start_time = 0
is_pressed = False

# Timer for checking long press
timer = Timer(-1)

message = "Bootloader mode activated.\nYou can now install firmware over USB.\n\n"

def handle_long_press():
    print(message)
    import lvgl as lv
    screen = lv.obj()
    label = lv.label(screen)
    label.set_text(message)
    label.center()
    lv.screen_load(screen)
    time.sleep(1)
    import machine
    machine.bootloader()

def on_long_press(t): # Callback for when long press duration is reached.
    global timer
    timer.deinit()  # Stop the timer
    global is_pressed
    if is_pressed and button.value() == 0:  # Ensure button is still pressed
        _thread.start_new_thread(handle_long_press, ())
    else:
        is_pressed = False


def button_handler(pin):
    """Interrupt handler for button press and release."""
    global press_start_time, is_pressed, timer
    if button.value() == 0:  # Button pressed (LOW due to pull-up)
        print("Button IO0 pressed")
        press_start_time = time.ticks_ms()
        is_pressed = True
        # Start timer to check for long press after long_press_duration
        timer.init(mode=Timer.ONE_SHOT, period=long_press_duration, callback=on_long_press)
    else:  # Button released (HIGH)
        print("Button IO0 released")
        timer.deinit()  # Cancel timer if button is released early
        is_pressed = False


# Set up interrupt for both falling (press) and rising (release) edges
button.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_handler)

print("button.py finished")
