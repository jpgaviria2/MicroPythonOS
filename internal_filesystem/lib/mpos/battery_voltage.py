have_adc=True
try:
    from machine import ADC, Pin
    # Configure ADC on pin 5 (IO5 / BAT_ADC)
    adc = ADC(Pin(5))
    # Set ADC to 11dB attenuation for 0–3.3V range (common for ESP32)
    adc.atten(ADC.ATTN_11DB)
except Exception as e:
    print("Info: this platform has no ADC for measuring battery voltage")
    have_adc=False

import time

# ADC parameters
VREF = 3.3  # Reference voltage (3.3V for most boards, adjust if different)
ADC_MAX = 4095  # 12-bit ADC resolution
VOLTAGE_DIVIDER = 3  # (R1 + R2) / R2 = (200k + 100k) / 100k = 3

def read_battery_voltage():
    if not have_adc:
        import random
        return random.randint(370,420) / 100
    # Read raw ADC value
    total = 0
    # Read multiple times to try to reduce variability.
    # Reading 10 times takes around 3ms so it's fine...
    for _ in range(10):
        total = total + adc.read()
    raw_value = total / 10
    # Convert to voltage, accounting for divider and reference
    voltage = (raw_value / ADC_MAX) * VREF * VOLTAGE_DIVIDER
    # Clamp to 0–4.2V range for LiPo battery
    voltage = max(0, min(voltage, 4.2))
    return voltage

# Main loop to read and print battery voltage
if False:
#for _ in range(10):
    battery_voltage = read_battery_voltage()
    print("Battery Voltage: {:.2f} V".format(battery_voltage))
    time.sleep(1)  # Wait 1 second
