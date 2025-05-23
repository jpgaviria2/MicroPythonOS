import time

def build_main_ui():
    appscreen.clean()
    balance_label = lv.label(appscreen)
    balance_label.align(lv.ALIGN.TOP_LEFT, 0, 0)
    balance_label.set_style_text_font(lv.font_montserrat_16, 0)
    balance_label.set_text('123456')
    point1 = lv.point_precise_t()
    point1.x = 10
    point1.y = 10
    point2 = lv.point_precise_t()
    point2.x = 200
    point2.y = 200
    line_points = [
        point1,
        point2
    ]
    style_line = lv.style_t()
    style_line.init()
    style_line.set_line_width(8)
    style_line.set_line_color(lv.palette_main(lv.PALETTE.BLUE))
    style_line.set_line_rounded(True)
    balance_line = lv.line()
    balance_line.set_points(line_points, 2)
    balance_line.add_style(style_line, 0)
    balance_line.center()
    l = lv.line(appscreen)
    l.set_points([{'x':100,'y':100},{'x':150,'y':100},{'x':150,'y':150}],3)
    l.add_style(style_line, 0)

def janitor_cb(timer):
    if lv.screen_active() != appscreen:
        print("app backgrounded, cleaning up...")
        janitor.delete()
        # No cleanups to do, but in a real app, you might stop timers, deinitialize hardware devices you used, close network connections, etc.

appscreen = lv.screen_active()
janitor = lv.timer_create(janitor_cb, 1000, None)

build_main_ui()
