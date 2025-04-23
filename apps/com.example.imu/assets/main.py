from machine import Pin, I2C
from qmi8658 import QMI8658
import time
import machine


sensor = QMI8658(I2C(0, sda=machine.Pin(48), scl=machine.Pin(47)))
print(f"""{sensor.temperature=}
{sensor.acceleration=}
{sensor.gyro=}""")

templabel = lv.label(subwindow)
templabel.align(lv.ALIGN.TOP_MID, 0, 10)

#acclabelx = lv.label(subwindow)
#acclabelx.align(lv.ALIGN.CENTER, -100, 0)
#acclabely = lv.label(subwindow)
#acclabely.align(lv.ALIGN.CENTER, 0, 0)
#acclabelz = lv.label(subwindow)
#acclabelz.align(lv.ALIGN.CENTER, 100, 0)

sliderx = lv.slider(subwindow)
sliderx.align(lv.ALIGN.CENTER, 0, -30)
slidery = lv.slider(subwindow)
slidery.align(lv.ALIGN.CENTER, 0, 0)
sliderz = lv.slider(subwindow)
sliderz.align(lv.ALIGN.CENTER, 0, 30)

canary = lv.obj(subwindow)
canary.add_flag(0x0001) # LV_OBJ_FLAG_HIDDEN is 0x0001

while canary.get_class():
    ax = sensor.acceleration[0]
    axp = int((ax * 100 + 100)/2)
    ay = sensor.acceleration[1]
    ayp = int((ay * 100 + 100)/2)
    az = sensor.acceleration[2]
    azp = int((az * 100 + 100)/2)
    templabel.set_text(f"Temperature: {sensor.temperature}")
    #acclabelx.set_text(f"AXP: { axp}")
    #acclabely.set_text(f"AY: {sensor.acceleration[1]}")
    #acclabelz.set_text(f"AZ: {sensor.acceleration[2]}")
    sliderx.set_value(axp, lv.ANIM.OFF)
    slidery.set_value(ayp, lv.ANIM.OFF)
    sliderz.set_value(azp, lv.ANIM.OFF)
    time.sleep_ms(100)


