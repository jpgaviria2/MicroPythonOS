appscreen = lv.screen_active()

import lvgl as lv

class DrawApp:
    def __init__(self):
        self.canvas = None
        self.init_gui()
    def init_gui(self):
        self.canvas = lv.canvas(lv.screen_active())
        disp = lv.display_get_default()
        self.canvas.set_size(disp.get_hor_res(), disp.get_ver_res())
        self.canvas.set_style_bg_color(lv.color_white(), 0)
        buffer = bytearray(disp.get_hor_res() * disp.get_ver_res() * 4)
        self.canvas.set_buffer(buffer, disp.get_hor_res(), disp.get_ver_res(), lv.COLOR_FORMAT.NATIVE)
        self.canvas.fill_bg(lv.color_white(), lv.OPA.COVER)
        self.canvas.add_event_cb(self.touch_cb, lv.EVENT.PRESSING, None)
    def touch_cb(self, obj, event, user_data):
        if event == lv.EVENT.PRESSING:
            indev = lv.indev_active()
            if indev:
                point = indev.get_point()
                x, y = point.x, point.y
                self.canvas.draw_arc(x, y, 5, 0, 360, lv.color_black())

draw_app = DrawApp()

# Wait until the user closes the app
while appscreen == lv.screen_active():
    time.sleep_ms(1000)
