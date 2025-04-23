from machine import Pin, I2C
from qmi8658 import QMI8658
import time
import machine


sensor = QMI8658(I2C(0, sda=machine.Pin(48), scl=machine.Pin(47)))

templabel = lv.label(subwindow)
templabel.align(lv.ALIGN.TOP_MID, 0, 10)

#scale = lv.scale(subwindow)
#scale.set_size(lv.pct(80), 50)
#scale.align(lv.ALIGN.TOP_MID, 0, 40)

#acclabelx = lv.label(subwindow)
#acclabelx.align(lv.ALIGN.CENTER, -100, 0)
#acclabely = lv.label(subwindow)
#acclabely.align(lv.ALIGN.CENTER, 0, 0)
#acclabelz = lv.label(subwindow)
#acclabelz.align(lv.ALIGN.CENTER, 100, 0)

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
    """Convert a value from [-200, 200] to [0, 100] with non-linear stretching around 0."""
    # Step 1: Normalize input from [-200, 200] to [-1, 1]
    normalized = value / 200.0
    # Step 2: Apply non-linear transformation (preserve sign)
    sign = 1 if normalized >= 0 else -1
    abs_normalized = abs(normalized)
    # Use square root (or another power < 1) to stretch small values
    non_linear = sign * (abs_normalized ** 0.5)
    # Step 3: Scale and shift to [0, 100]
    # Map [-1, 1] to [0, 100] (i.e., -1 -> 0, 0 -> 50, 1 -> 100)
    return int((non_linear + 1) * 50.0)

canary = lv.obj(subwindow)
canary.add_flag(0x0001) # LV_OBJ_FLAG_HIDDEN is 0x0001
while canary.get_class():
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

