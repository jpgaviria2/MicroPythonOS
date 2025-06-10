import os
import time

from mpos.apps import Activity
import mpos.ui

class ImageView(Activity):

    #imagedir = "../icons/"
    #imagedir = "../artwork/"
    imagedir = "data/images"
    #imagedir = "/home/user/Downloads/"
    #imagedir = "/home/user/images/"
    images = []
    image_nr = None
    image_timer = None
    image = None

    def onCreate(self):
        screen = lv.obj()
        self.image = lv.image(screen)
        self.image.set_size(128, 128)
        self.image.center()
        self.label = lv.label(screen)
        self.label.set_text('Hello Images!')
        self.label.align(lv.ALIGN.TOP_MID,0,0)
        self.prev_button = lv.button(screen)
        self.prev_button.align(lv.ALIGN.BOTTOM_LEFT,0,0)
        self.prev_button.add_event_cb(lambda e: self.show_prev_image(),lv.EVENT.CLICKED,None)
        prev_label = lv.label(self.prev_button)
        prev_label.set_text(lv.SYMBOL.LEFT)
        self.play_button = lv.button(screen)
        self.play_button.align(lv.ALIGN.BOTTOM_MID,0,0)
        self.play_button.add_event_cb(lambda e: self.play(),lv.EVENT.CLICKED,None)
        play_label = lv.label(self.play_button)
        play_label.set_text(lv.SYMBOL.PLAY)
        self.next_button = lv.button(screen)
        self.next_button.align(lv.ALIGN.BOTTOM_RIGHT,0,0)
        self.next_button.add_event_cb(lambda e: self.show_next_image(),lv.EVENT.CLICKED,None)
        #self.next_button.add_event_cb(self.touch_cb, lv.EVENT.ALL, None)
        next_label = lv.label(self.next_button)
        next_label.set_text(lv.SYMBOL.RIGHT)
        #screen.add_event_cb(self.touch_cb, lv.EVENT.ALL, None)
        self.setContentView(screen)

    def onResume(self, screen):
        self.images.clear()
        for item in os.listdir(self.imagedir):
            print(item)
            if item.endswith(".jpg") or item.endswith(".jpeg") or item.endswith(".png"):
                fullname = f"{self.imagedir}/{item}"
                size = os.stat(fullname)[6]
                print(f"size: {size}")
                if size > 10 * 1024*1024:
                    print(f"Skipping file of size {size}")
                    continue
                self.images.append(fullname)
        # Begin with one image:
        self.show_next_image()
        #self.image_timer = lv.timer_create(self.show_next_image, 1000, None)

    def onStop(self, screen):
        if self.image_timer:
            print("ImageView: deleting image_timer")
            self.image_timer.delete()
    
    def touch_cb(self, event):
        global canvas
        event_code=event.get_code()
        #print(f"got event {event_code}")
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
        # 39: CHILD_CHANGED
        # GET_SELF_SIZE
        if event_code not in [19,23,25,26,27,28,29,30,39,49]:
            name = mpos.ui.get_event_name(event_code)
            print(f"lv_event_t: code={event_code}, name={name}") # target={event.get_target()}, user_data={event.get_user_data()}, param={event.get_param()}


    def show_prev_image(self, event=None):
        print("showing previous image...")
        if len(self.images) < 1:
            return
        if self.image_nr is None or self.image_nr == 0:
            self.image_nr = len(self.images) - 1
        else:
            self.image_nr = self.image_nr - 1
        name = self.images[self.image_nr]
        print(f"show_prev_image showing {name}")
        self.show_image(name)

    def play(self, event=None):
        print("playing...")

    def show_next_image(self, event=None):
        print("showing next image...")
        if len(self.images) < 1:
            return
        if self.image_nr is None or self.image_nr  >= len(self.images) - 1:
            self.image_nr = 0
        else:
            self.image_nr = self.image_nr + 1
        name = self.images[self.image_nr]
        print(f"show_next_image showing {name}")
        self.show_image(name)

    def show_image(self, name):
        try:
            self.label.set_text(name)
            self.image.set_src(f"M:{name}")
            print(f"the LVGL image has size: {self.image.get_width()}x{self.image.get_height()}")
            header = lv.image_header_t()
            self.image.decoder_get_info(self.image.get_src(), header)
            print(f"the real image has size: {header.w}x{header.h}")
            #image.set_size(128, 128)
            #self.image.set_scale(512)
            print(f"after set_scale, the LVGL image has size: {self.image.get_width()}x{self.image.get_height()}")
        except Exception as e:
            print(f"show_image got exception: {e}")
