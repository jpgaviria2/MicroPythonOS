from machine import Pin, I2C
from qmi8658 import QMI8658
import machine

sensor = QMI8658(I2C(0, sda=machine.Pin(48), scl=machine.Pin(47)))

templabel = lv.label(subwindow)
templabel.align(lv.ALIGN.TOP_MID, 0, 10)

sliderx = lv.slider(subwindow)
sliderx.align(lv.ALIGN.CENTER, 0, -60)
slidery = lv.slider(subwindow)
slidery.align(lv.ALIGN.CENTER, 0, -30)
sliderz = lv.slider(subwindow)
sliderz.align(lv.ALIGN.CENTER, 0, 0)

slidergx = lv.slider(subwindow)
slidergx.align(lv.ALIGN.CENTER, 0, 30)
slidergy = lv.slider(subwindow)
slidergy.align(lv.ALIGN.CENTER, 0, 60)
slidergz = lv.slider(subwindow)
slidergz.align(lv.ALIGN.CENTER, 0, 90)

def map_nonlinear(value: float) -> int:
    # Preserve sign and work with absolute value
    sign = 1 if value >= 0 else -1
    abs_value = abs(value)
    # Apply non-linear transformation (square root) to absolute value
    # Scale input range [0, 200] to [0, sqrt(200)] first
    sqrt_value = (abs_value ** 0.5)
    # Scale to output range [0, 100]
    # Map [0, sqrt(200)] to [50, 100] for positive, [0, 50] for negative
    max_sqrt = 200.0 ** 0.5  # Approx 14.142
    scaled = (sqrt_value / max_sqrt) * 50.0  # Scale to [0, 50]
    return int(50.0 + (sign * scaled))  # Shift to [0, 100]

import time
while appscreen == lv.screen_active():
    #print(f"""{sensor.temperature=} {sensor.acceleration=} {sensor.gyro=}""")
    templabel.set_text(f"Temperature: {sensor.temperature:.2f}")
    ax = sensor.acceleration[0]
    axp = int((ax * 100 + 100)/2)
    ay = sensor.acceleration[1]
    ayp = int((ay * 100 + 100)/2)
    az = sensor.acceleration[2]
    azp = int((az * 100 + 100)/2)
    sliderx.set_value(axp, lv.ANIM.OFF)
    slidery.set_value(ayp, lv.ANIM.OFF)
    sliderz.set_value(azp, lv.ANIM.OFF)
    # values between -200 and 200 => /4 becomes -50 and 50 => +50 becomes 0 and 100
    slidergx.set_value(map_nonlinear(sensor.gyro[0]), lv.ANIM.OFF)
    slidergy.set_value(map_nonlinear(sensor.gyro[1]), lv.ANIM.OFF)
    slidergz.set_value(map_nonlinear(sensor.gyro[2]), lv.ANIM.OFF)
    time.sleep_ms(100)

