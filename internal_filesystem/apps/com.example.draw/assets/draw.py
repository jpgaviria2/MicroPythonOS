appscreen = lv.screen_active()

import lvgl as lv

indev_error_x = 160
indev_error_y = 120

DARKPINK = lv.color_hex(0xEC048C)

EVENT_MAP = {
    lv.EVENT.ALL: "ALL",
    lv.EVENT.CANCEL: "CANCEL",
    lv.EVENT.CHILD_CHANGED: "CHILD_CHANGED",
    lv.EVENT.CHILD_CREATED: "CHILD_CREATED",
    lv.EVENT.CHILD_DELETED: "CHILD_DELETED",
    lv.EVENT.CLICKED: "CLICKED",
    lv.EVENT.COLOR_FORMAT_CHANGED: "COLOR_FORMAT_CHANGED",
    lv.EVENT.COVER_CHECK: "COVER_CHECK",
    lv.EVENT.CREATE: "CREATE",
    lv.EVENT.DEFOCUSED: "DEFOCUSED",
    lv.EVENT.DELETE: "DELETE",
    lv.EVENT.DRAW_MAIN: "DRAW_MAIN",
    lv.EVENT.DRAW_MAIN_BEGIN: "DRAW_MAIN_BEGIN",
    lv.EVENT.DRAW_MAIN_END: "DRAW_MAIN_END",
    lv.EVENT.DRAW_POST: "DRAW_POST",
    lv.EVENT.DRAW_POST_BEGIN: "DRAW_POST_BEGIN",
    lv.EVENT.DRAW_POST_END: "DRAW_POST_END",
    lv.EVENT.DRAW_TASK_ADDED: "DRAW_TASK_ADDED",
    lv.EVENT.FLUSH_FINISH: "FLUSH_FINISH",
    lv.EVENT.FLUSH_START: "FLUSH_START",
    lv.EVENT.FLUSH_WAIT_FINISH: "FLUSH_WAIT_FINISH",
    lv.EVENT.FLUSH_WAIT_START: "FLUSH_WAIT_START",
    lv.EVENT.FOCUSED: "FOCUSED",
    lv.EVENT.GESTURE: "GESTURE",
    lv.EVENT.GET_SELF_SIZE: "GET_SELF_SIZE",
    lv.EVENT.HIT_TEST: "HIT_TEST",
    lv.EVENT.HOVER_LEAVE: "HOVER_LEAVE",
    lv.EVENT.HOVER_OVER: "HOVER_OVER",
    lv.EVENT.INDEV_RESET: "INDEV_RESET",
    lv.EVENT.INSERT: "INSERT",
    lv.EVENT.INVALIDATE_AREA: "INVALIDATE_AREA",
    lv.EVENT.KEY: "KEY",
    lv.EVENT.LAST: "LAST",
    lv.EVENT.LAYOUT_CHANGED: "LAYOUT_CHANGED",
    lv.EVENT.LEAVE: "LEAVE",
    lv.EVENT.LONG_PRESSED: "LONG_PRESSED",
    lv.EVENT.LONG_PRESSED_REPEAT: "LONG_PRESSED_REPEAT",
    lv.EVENT.PREPROCESS: "PREPROCESS",
    lv.EVENT.PRESSED: "PRESSED",
    lv.EVENT.PRESSING: "PRESSING",
    lv.EVENT.PRESS_LOST: "PRESS_LOST",
    lv.EVENT.READY: "READY",
    lv.EVENT.REFRESH: "REFRESH",
    lv.EVENT.REFR_EXT_DRAW_SIZE: "REFR_EXT_DRAW_SIZE",
    lv.EVENT.REFR_READY: "REFR_READY",
    lv.EVENT.REFR_REQUEST: "REFR_REQUEST",
    lv.EVENT.REFR_START: "REFR_START",
    lv.EVENT.RELEASED: "RELEASED",
    lv.EVENT.RENDER_READY: "RENDER_READY",
    lv.EVENT.RENDER_START: "RENDER_START",
    lv.EVENT.RESOLUTION_CHANGED: "RESOLUTION_CHANGED",
    lv.EVENT.ROTARY: "ROTARY",
    lv.EVENT.SCREEN_LOADED: "SCREEN_LOADED",
    lv.EVENT.SCREEN_LOAD_START: "SCREEN_LOAD_START",
    lv.EVENT.SCREEN_UNLOADED: "SCREEN_UNLOADED",
    lv.EVENT.SCREEN_UNLOAD_START: "SCREEN_UNLOAD_START",
    lv.EVENT.SCROLL: "SCROLL",
    lv.EVENT.SCROLL_BEGIN: "SCROLL_BEGIN",
    lv.EVENT.SCROLL_END: "SCROLL_END",
    lv.EVENT.SCROLL_THROW_BEGIN: "SCROLL_THROW_BEGIN",
    lv.EVENT.SHORT_CLICKED: "SHORT_CLICKED",
    lv.EVENT.SIZE_CHANGED: "SIZE_CHANGED",
    lv.EVENT.STYLE_CHANGED: "STYLE_CHANGED",
    lv.EVENT.VALUE_CHANGED: "VALUE_CHANGED",
    lv.EVENT.VSYNC: "VSYNC"
}

# Function to translate event code to name
def get_event_name(event_code):
    return EVENT_MAP.get(event_code, f"Unknown event {event_code}")

def get_xy():
    indev = lv.indev_active()
    if indev:
        point = lv.point_t()
        indev.get_point(point)
        return point.x, point.y
    else:
        return indev_error_x,indev_error_y # make it visible that this occurred

def draw_line(x, y):
    global canvas
    # Line drawing like this doesn't work:
    layer = lv.layer_t()
    canvas.init_layer(layer)
    dsc = lv.draw_line_dsc_t()
    dsc.color = DARKPINK
    dsc.width = 4
    dsc.round_end = 1
    dsc.round_start = 1
    dsc.p1 = lv.point_precise_t()
    dsc.p1.x = x
    dsc.p1.y = y
    dsc.p2 = lv.point_precise_t()
    dsc.p2.x = 100
    dsc.p2.y = 200
    #layer.draw_line(dsc) doesnt exist!
    lv.draw_line(layer,dsc) # doesnt do anything!
    canvas.finish_layer(layer)


def touch_cb(event):
    global canvas
    event_code=event.get_code()
    # Ignore:
    # =======
    # COVER_CHECK
    # DRAW_MAIN
    # DRAW_MAIN_BEGIN
    # DRAW_MAIN_END
    # DRAW_POST
    # DRAW_POST_BEGIN
    # DRAW_POST_END
    # GET_SELF_SIZE
    if event_code not in [23,25,26,27,28,29,30,49]:
        name = get_event_name(event_code)
        #x, y = get_xy()
        #print(f"lv_event_t: code={event_code}, name={name}, x={x}, y={y}") # target={event.get_target()}, user_data={event.get_user_data()}, param={event.get_param()}
        if event_code == lv.EVENT.PRESSING: # this is probably enough
        #if event_code in [lv.EVENT.PRESSED, lv.EVENT.PRESSING, lv.EVENT.LONG_PRESSED, lv.EVENT.LONG_PRESSED_REPEAT]:
            x, y = get_xy()
            # drawing a point works:
            #canvas.set_px(x,y,lv.color_black(),lv.OPA.COVER)
            #
            # drawing a square like this works:
            #for dx in range(-5,5):
            #    for dy in range(-5,5):
            #        canvas.set_px(x+dx,y+dy,DARKPINK,lv.OPA.COVER)
            #
            # drawing a circle works:
            radius = 7  # Set desired radius
            if x == indev_error_x and y == indev_error_y:
                radius = 25 # in case of indev error
            square = radius * radius
            for dx in range(-radius, radius):
                for dy in range(-radius, radius):
                    if dx * dx + dy * dy <= square:
                        canvas.set_px(x + dx, y + dy, DARKPINK, lv.OPA.COVER)


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

