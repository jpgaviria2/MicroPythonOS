import os
import time

from mpos.apps import Activity

class ImageView(Activity):

    imagedir = "../icons/"
    images = []
    image_nr = 0
    image_timer = None
    image = None
    image_dsc = None

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
        self.images.clear()
        for item in os.listdir(self.imagedir):
            print(item)
            if item.endswith(".jpg") or item.endswith(".jpeg") or item.endswith(".png"):
            #if item.endswith(".png"):
                fullname = f"{self.imagedir}/{item}"
                size = os.stat(fullname)[6]
                print(f"size: {size}")
                #if size > 1024*1024:
                if size > 60000:
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
            f = open(name, 'rb')
            image_data = f.read()
            print(f"loaded {len(image_data)} bytes")
            f.close()
            self.image_dsc = lv.image_dsc_t({
                'data_size': len(image_data),
                'data': image_data 
            })
            #image.set_size(128, 128)
            #image.set_scale(512)
            self.image.set_src(self.image_dsc)
            print(f"done with show_image({name})")
        except Exception as e:
            print("show_image got exception: {e}")
