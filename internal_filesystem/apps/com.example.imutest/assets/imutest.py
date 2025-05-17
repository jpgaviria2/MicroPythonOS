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

def refresh(timer):
    if have_imu:
        #print(f"""{sensor.temperature=} {sensor.acceleration=} {sensor.gyro=}""")
        temp = sensor.temperature
        ax = sensor.acceleration[0]
        axp = int((ax * 100 + 100)/2)
        ay = sensor.acceleration[1]
        ayp = int((ay * 100 + 100)/2)
        az = sensor.acceleration[2]
        azp = int((az * 100 + 100)/2)
        # values between -200 and 200 => /4 becomes -50 and 50 => +50 becomes 0 and 100
        gx = map_nonlinear(sensor.gyro[0])
        gy = map_nonlinear(sensor.gyro[1])
        gz = map_nonlinear(sensor.gyro[2])
    else:
        temp = 12.34
        axp = 25
        ayp = 50
        azp = 75
        gx = 45
        gy = 50
        gz = 55
    templabel.set_text(f"IMU chip temperature: {temp:.2f}°C")
    sliderx.set_value(axp, lv.ANIM.OFF)
    slidery.set_value(ayp, lv.ANIM.OFF)
    sliderz.set_value(azp, lv.ANIM.OFF)
    slidergx.set_value(gx, lv.ANIM.OFF)
    slidergy.set_value(gy, lv.ANIM.OFF)
    slidergz.set_value(gz, lv.ANIM.OFF)


def janitor_cb(timer):
    if lv.screen_active() != appscreen:
        print("imutest.py backgrounded, cleaning up...")
        janitor.delete()
        refresh_timer.delete()

have_imu = True
try:
    from machine import Pin, I2C
    from qmi8658 import QMI8658
    import machine
    sensor = QMI8658(I2C(0, sda=machine.Pin(48), scl=machine.Pin(47)))
except Exception as e:
    print(f"Warning: could not initialize IMU hardware: {e}")
    have_imu=False


appscreen = lv.screen_active()
templabel = lv.label(appscreen)
templabel.align(lv.ALIGN.TOP_MID, 0, 10)
sliderx = lv.slider(appscreen)
sliderx.align(lv.ALIGN.CENTER, 0, -60)
slidery = lv.slider(appscreen)
slidery.align(lv.ALIGN.CENTER, 0, -30)
sliderz = lv.slider(appscreen)
sliderz.align(lv.ALIGN.CENTER, 0, 0)
slidergx = lv.slider(appscreen)
slidergx.align(lv.ALIGN.CENTER, 0, 30)
slidergy = lv.slider(appscreen)
slidergy.align(lv.ALIGN.CENTER, 0, 60)
slidergz = lv.slider(appscreen)
slidergz.align(lv.ALIGN.CENTER, 0, 90)

refresh_timer = lv.timer_create(refresh, 100, None)
janitor = lv.timer_create(janitor_cb, 500, None)
