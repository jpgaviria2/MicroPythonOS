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

acclabelx = lv.label(subwindow)
acclabelx.align(lv.ALIGN.CENTER, -100, 0)
acclabely = lv.label(subwindow)
acclabely.align(lv.ALIGN.CENTER, 0, 0)
acclabelz = lv.label(subwindow)
acclabelz.align(lv.ALIGN.CENTER, 100, 0)

canary = lv.obj(subwindow)
canary.add_flag(0x0001) # LV_OBJ_FLAG_HIDDEN is 0x0001

while canary.get_class():
    templabel.set_text(f"Temperature: {sensor.temperature}")
    acclabelx.set_text(f"AX: {sensor.acceleration[0]}")
    acclabely.set_text(f"AY: {sensor.acceleration[1]}")
    acclabelz.set_text(f"AZ: {sensor.acceleration[2]}")
    time.sleep_ms(100)


