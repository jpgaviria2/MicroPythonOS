print("button.py running")

from machine import Pin, Timer
import time

# Configure IO0 as input with pull-up resistor
button = Pin(0, Pin.IN, Pin.PULL_UP)

# Variables for long press detection
long_press_duration = 4000
press_start_time = 0
is_pressed = False

# Timer for checking long press
timer = Timer(-1)


def on_long_press(t): # Callback for when long press duration is reached.
    timer.deinit()  # Stop the timer
    global is_pressed
    if is_pressed and button.value() == 0:  # Ensure button is still pressed
        print("Button IO0 long pressed, going into bootloader mode...")
        import machine
        machine.bootloader()
    else:
        is_pressed = False


def button_handler(pin):
    """Interrupt handler for button press and release."""
    global press_start_time, is_pressed
    # Debounce: Ignore interrupts within 50ms of the last event
    if time.ticks_diff(time.ticks_ms(), press_start_time) < 50:
        return
    if button.value() == 0:  # Button pressed (LOW due to pull-up)
        print("Button IO0 pressed.")
        press_start_time = time.ticks_ms()
        is_pressed = True
        # Start timer to check for long press after long_press_duration
        timer.init(mode=Timer.ONE_SHOT, period=long_press_duration, callback=on_long_press)
    else:  # Button released (HIGH)
        print("Button IO0 released.")
        timer.deinit()  # Cancel timer if button is released early
        is_pressed = False


# Set up interrupt for both falling (press) and rising (release) edges
button.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_handler)

print("button.py finished")
