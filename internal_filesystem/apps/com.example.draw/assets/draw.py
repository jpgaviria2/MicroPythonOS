appscreen = lv.screen_active()

import lvgl as lv

def touch_cb(event):
    global canvas
    event_code=event.get_code()
    if event_code not in [23,25,26,27,28,29,30,49]:
        #print(f"got event: {event}")
        print(f"lv_event_t: code={event_code}, target={event.get_target()}, user_data={event.get_user_data()}, param={event.get_param()}")
        if event_code == lv.EVENT.PRESSING:
            print("lv.EVENT.PRESSING")
            indev = lv.indev_active()
            if indev:
                #point = indev.get_point()
                #x, y = point.x, point.y
                import random
                x = random.randrange(1,200)
                y = random.randrange(1,200)
                #print(f"got indev {x} {y} {point}")
                #canvas.draw_arc(x, y, 5, 0, 360, lv.color_black())
                canvas.set_px(x,y,lv.color_black(),lv.OPA.COVER)
            else:
                print("no indev!")


canvas = lv.canvas(appscreen)
disp = lv.display_get_default()
hor_res = disp.get_horizontal_resolution()
ver_res = disp.get_vertical_resolution()
canvas.set_size(hor_res, ver_res)
canvas.set_style_bg_color(lv.color_white(), 0)
buffer = bytearray(hor_res * ver_res * 4)
canvas.set_buffer(buffer, hor_res, ver_res, lv.COLOR_FORMAT.NATIVE)
canvas.fill_bg(lv.color_white(), lv.OPA.COVER)
canvas.add_flag(lv.obj.FLAG.CLICKABLE)
canvas.add_event_cb(touch_cb, lv.EVENT.ALL, None)


# Wait until the user closes the app
#while appscreen == lv.screen_active():
#    time.sleep_ms(1000)
