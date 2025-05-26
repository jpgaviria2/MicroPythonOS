from machine import Timer

# Callback function to be executed periodically
def timer_callback(timer):
    print("Timer 500 triggered!")

# Initialize a timer
timer = Timer(500)  # Must be 0-20 on unix/desktop

# Set up a periodic timer (e.g., trigger every 1000ms)
timer.init(period=1000, mode=Timer.PERIODIC, callback=timer_callback)
