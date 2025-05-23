import time

def build_main_ui():
    appscreen.clean()
    balance_label = lv.label(appscreen)
    balance_label.align(lv.ALIGN.TOP_LEFT, 0, 0)
    balance_label.set_style_text_font(lv.font_montserrat_20, 0)
    balance_label.set_text('123456')
    style_line = lv.style_t()
    style_line.init()
    style_line.set_line_width(4)
    style_line.set_line_color(lv.palette_main(lv.PALETTE.PINK))
    style_line.set_line_rounded(True)
    balance_line = lv.line(appscreen)
    balance_line.set_points([{'x':0,'y':35},{'x':300,'y':35}],2)
    balance_line.add_style(style_line, 0)

def janitor_cb(timer):
    if lv.screen_active() != appscreen:
        print("app backgrounded, cleaning up...")
        janitor.delete()
        # No cleanups to do, but in a real app, you might stop timers, deinitialize hardware devices you used, close network connections, etc.

appscreen = lv.screen_active()
janitor = lv.timer_create(janitor_cb, 1000, None)

build_main_ui()
