from mpos.apps import Activity
import mpos.ui

indev_error_x = 160
indev_error_y = 120

DARKPINK = lv.color_hex(0xEC048C)

# doesnt work:
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




class Draw(Activity):

    hor_res = 0
    ver_res = 0

    # Widgets:
    canvas = None

    def onCreate(self):
        screen = lv.obj()
        self.canvas = lv.canvas(screen)
        disp = lv.display_get_default()
        self.hor_res = disp.get_horizontal_resolution()
        self.ver_res = disp.get_vertical_resolution()
        self.canvas.set_size(self.hor_res, self.ver_res)
        self.canvas.set_style_bg_color(lv.color_white(), 0)
        buffer = bytearray(self.hor_res * self.ver_res * 4)
        self.canvas.set_buffer(buffer, self.hor_res, self.ver_res, lv.COLOR_FORMAT.NATIVE)
        self.canvas.fill_bg(lv.color_white(), lv.OPA.COVER)
        self.canvas.add_flag(lv.obj.FLAG.CLICKABLE)
        self.canvas.add_event_cb(self.touch_cb, lv.EVENT.ALL, None)
        self.setContentView(screen)

    def touch_cb(self, event):
        event_code=event.get_code()
        # Ignore:
        # =======
        # 19: HIT_TEST
        # COVER_CHECK
        # DRAW_MAIN
        # DRAW_MAIN_BEGIN
        # DRAW_MAIN_END
        # DRAW_POST
        # DRAW_POST_BEGIN
        # DRAW_POST_END
        # GET_SELF_SIZE
        if event_code not in [19,23,25,26,27,28,29,30,49]:
            name = mpos.ui.get_event_name(event_code)
            #print(f"lv_event_t: code={event_code}, name={name}") # target={event.get_target()}, user_data={event.get_user_data()}, param={event.get_param()}
            if event_code == lv.EVENT.PRESSING: # this is probably enough
            #if event_code in [lv.EVENT.PRESSED, lv.EVENT.PRESSING, lv.EVENT.LONG_PRESSED, lv.EVENT.LONG_PRESSED_REPEAT]:
                x, y = mpos.ui.get_pointer_xy()
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
                            newx, newy = x + dx, y + dy
                            if 0 <= newx <= self.hor_res and 0 <= newy <= self.ver_res: # don't draw outside of canvas because that may crash
                                self.canvas.set_px(x + dx, y + dy, DARKPINK, lv.OPA.COVER)
    
