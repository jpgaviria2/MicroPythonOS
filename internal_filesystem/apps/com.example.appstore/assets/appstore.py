import lvgl as lv
import json
import urequests
import gc

class App:
    def __init__(self, name, publisher, short_description, long_description, icon_url):
        self.name = name
        self.publisher = publisher
        self.short_description = short_description
        self.long_description = long_description
        self.icon_url = icon_url

class AppStore:
    def __init__(self, subwindow, json_url):
        print("__init__")
        self.subwindow = subwindow
        self.json_url = json_url
        self.apps = []
        self.app_detail_screen = None
        self.install_button = None
        print("__init__")
        self.main_screen_init()
    def main_screen_init(self):
        self.please_wait_label = lv.label(self.subwindow)
        self.please_wait_label.set_text("Please wait...")
        self.please_wait_label.center()
        self.download_apps()
    def download_apps(self):
        try:
            response = urequests.get(self.json_url)
            print("download_apps")
            if response.status_code == 200:
                print(f"Got response text: {response.text}")
                self.apps = [App(**app) for app in json.loads(response.text)]
                response.close()
                self.please_wait_label.add_flag(lv.obj.FLAG.HIDDEN)
                self.create_apps_list()
        except Exception as e:
            print("Download failed:", e)
    def create_apps_list(self):
        print("create_apps_list")
        self.apps_list = lv.list(self.subwindow)
        self.apps_list.set_size(lv.pct(100), lv.pct(100))
        print("create_apps_list iterating")
        for app in self.apps:
            print("create_apps_list app found")
            item = self.apps_list.add_button(lv.SYMBOL.REFRESH, "Test")
            print("create_apps_list app found 1")
            item.add_flag(lv.obj.FLAG.CLICKABLE)
            print("create_apps_list app found 2")
            item.add_event_cb(lambda e, a=app: self.show_app_detail(a), lv.EVENT.CLICKED, None)
            print("create_apps_list app found 3")
            cont = lv.obj(item)
            print("create_apps_list app found 4")
            cont.set_flex_flow(lv.FLEX_FLOW.ROW)
            print("create_apps_list app found 5")
            cont.set_size(lv.pct(100), lv.SIZE_CONTENT)
            print("create_apps_list app found 6")
            icon_spacer = lv.obj(cont)
            icon_spacer.set_size(40, 40)
            label_cont = lv.obj(cont)
            label_cont.set_flex_flow(lv.FLEX_FLOW.COLUMN)
            label_cont.set_size(lv.pct(100), lv.SIZE_CONTENT)
            name_label = lv.label(label_cont)
            name_label.set_text(app.name)
            name_label.set_style_text_font(lv.font_montserrat_16, 0)
            desc_label = lv.label(label_cont)
            desc_label.set_text(app.short_description)
            desc_label.set_style_text_font(lv.font_montserrat_12, 0)
            print("create_apps_list app one done")
        print("create_apps_list app done")
    def show_app_detail(self, app):
        self.app_detail_screen = lv.obj(None)
        self.app_detail_screen.set_size(lv.pct(100), lv.pct(100))
        back_button = lv.button(self.app_detail_screen)
        back_button.set_size(30, 30)
        back_button.add_flag(lv.obj.FLAG.CLICKABLE)
        back_button.add_event_cb(self.back_to_main, lv.EVENT.CLICKED, None)
        back_label = lv.label(back_button)
        back_label.set_text(lv.SYMBOL.LEFT)
        back_label.center()
        cont = lv.obj(self.app_detail_screen)
        cont.set_size(lv.pct(100), lv.pct(100))
        cont.set_pos(0, 40)
        cont.set_flex_flow(lv.FLEX_FLOW.ROW)
        icon_spacer = lv.obj(cont)
        icon_spacer.set_size(60, 60)
        detail_cont = lv.obj(cont)
        detail_cont.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        detail_cont.set_size(lv.pct(100), lv.SIZE_CONTENT)
        name_label = lv.label(detail_cont)
        name_label.set_text(app.name)
        name_label.set_style_text_font(lv.font_montserrat_24, 0)
        publisher_label = lv.label(detail_cont)
        publisher_label.set_text(app.publisher)
        publisher_label.set_style_text_font(lv.font_montserrat_16, 0)
        self.install_button = lv.button(detail_cont)
        self.install_button.set_size(lv.pct(100), 40)
        self.install_button.add_flag(lv.obj.FLAG.CLICKABLE)
        self.install_button.add_event_cb(self.toggle_install, lv.EVENT.CLICKED, None)
        install_label = lv.label(self.install_button)
        install_label.set_text("Install")
        install_label.center()
        long_desc_label = lv.label(detail_cont)
        long_desc_label.set_text(app.long_description)
        long_desc_label.set_style_text_font(lv.font_montserrat_12, 0)
        long_desc_label.set_width(lv.pct(100))
        lv.screen_load(self.app_detail_screen)
    def toggle_install(self, event):
        label = self.install_button.get_child(0)
        if label.get_text() == "Install":
            label.set_text("Cancel")
        else:
            label.set_text("Install")
    def back_to_main(self, event):
        if self.app_detail_screen:
            self.app_detail_screen.delete()
            self.app_detail_screen = None
            lv.screen_load(self.subwindow)
            gc.collect()


# Example usage:
app_store = AppStore(subwindow, "http://demo.lnpiggy.com:2121/apps.json")

# Wait until the user stops the app
import time
while appscreen == lv.screen_active() or app_store.app_detail_screen == lv.screen_active():
    time.sleep_ms(50)
