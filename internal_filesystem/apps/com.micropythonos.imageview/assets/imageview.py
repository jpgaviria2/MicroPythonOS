import os
import time

from mpos.apps import Activity

class ImageView(Activity):

    #imagedir = "../icons/"
    imagedir = "../artwork/"
    #imagedir = "/home/user/Downloads/"
    #imagedir = "/home/user/images/"
    images = []
    image_nr = 0
    image_timer = None
    image = None

    def onCreate(self):
        screen = lv.obj()
        self.label = lv.label(screen)
        self.label.set_text('Hello Images!')
        self.label.align(lv.ALIGN.TOP_MID,0,0)
        self.image = lv.image(screen)
        self.image.set_size(128, 128)
        self.image.align(lv.ALIGN.BOTTOM_MID,0,0)
        self.setContentView(screen)

    def onResume(self, screen):
        #lv.libjpeg_turbo_init()
        #first = lv.image_decoder_t()
        #decoder = lv.image.decoder_get_next(first)
        #decoder = lv.image_decoder_t.get_next(first)
        #decoder.delete()
        self.images.clear()
        for item in os.listdir(self.imagedir):
            print(item)
            #if item.endswith(".jpg") or item.endswith(".jpeg"):
            if item.endswith(".jpg") or item.endswith(".jpeg") or item.endswith(".png"):
            #if item.endswith(".png"):
                fullname = f"{self.imagedir}/{item}"
                size = os.stat(fullname)[6]
                print(f"size: {size}")
                if size > 10 * 1024*1024:
                #if size > 60000:
                    print(f"Skipping file of size {size}")
                    continue
                self.images.append(fullname)
        self.image_timer = lv.timer_create(self.show_next_image, 1000, None)

    def onStop(self, screen):
        if self.image_timer:
            print("ImageView: deleting image_timer")
            self.image_timer.delete()

    def show_next_image(self, event):
        print("showing next image...")
        if len(self.images) < 1:
            return
        if self.image_nr  >= len(self.images):
            self.image_nr = 0
        name = self.images[self.image_nr]
        print(f"show_next_image showing {name}")
        self.show_image(name)
        self.image_nr = self.image_nr + 1

    def show_image(self, name):
        try:
            self.label.set_text(name)
            self.image.set_src(f"P:{name}")
            w = self.image.get_width()
            h = self.image.get_height()
            print(f"the LVGL image has size: {w}x{h}")
            header = lv.image_header_t()
            self.image.decoder_get_info(self.image.get_src(), header)
            print(f"the real image has size: {header.w}x{header.h}")
            #image.set_size(128, 128)
            self.image.set_scale(512)
            print(f"done with show_image({name}) got {w}x{h}")
        except Exception as e:
            print(f"show_image got exception: {e}")
