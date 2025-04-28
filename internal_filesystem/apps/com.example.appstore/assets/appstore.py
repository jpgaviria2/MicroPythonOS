import lvgl as lv
import json
import urequests
import gc

apps = []
app_detail_screen = None
install_button = None
please_wait_label = None
app_detail_screen = None

class App:
    def __init__(self, name, publisher, short_description, long_description, icon_url):
        self.name = name
        self.publisher = publisher
        self.short_description = short_description
        self.long_description = long_description
        self.icon_url = icon_url


def download_apps(json_url):
    global apps
    try:
        response = urequests.get(json_url, timeout=10)
        print("download_apps")
        if response.status_code == 200:
            print(f"Got response text: {response.text}")
            apps = [App(**app) for app in json.loads(response.text)]
            response.close()
            please_wait_label.add_flag(lv.obj.FLAG.HIDDEN)
            create_apps_list()
    except Exception as e:
        print("Download failed:", e)


def create_apps_list():
    global apps
    print("create_apps_list")
    apps_list = lv.list(subwindow)
    apps_list.set_size(lv.pct(100), lv.pct(100))
    print("create_apps_list iterating")
    for app in apps:
        item = apps_list.add_button(None, "Test")
        item.add_flag(lv.obj.FLAG.CLICKABLE)
        item.add_event_cb(lambda e, a=app: show_app_detail(a), lv.EVENT.CLICKED, None)
        cont = lv.obj(item)
        cont.set_flex_flow(lv.FLEX_FLOW.ROW)
        cont.set_size(lv.pct(100), lv.SIZE_CONTENT)
        cont.add_event_cb(lambda e, a=app: show_app_detail(a), lv.EVENT.CLICKED, None)
        icon_spacer = lv.obj(cont)
        icon_spacer.set_size(40, 40)
        icon_spacer.add_event_cb(lambda e, a=app: show_app_detail(a), lv.EVENT.CLICKED, None)
        label_cont = lv.obj(cont)
        label_cont.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        label_cont.set_size(lv.pct(100), lv.SIZE_CONTENT)
        label_cont.add_event_cb(lambda e, a=app: show_app_detail(a), lv.EVENT.CLICKED, None)
        name_label = lv.label(label_cont)
        name_label.set_text(app.name)
        name_label.set_style_text_font(lv.font_montserrat_16, 0)
        name_label.add_event_cb(lambda e, a=app: show_app_detail(a), lv.EVENT.CLICKED, None)
        desc_label = lv.label(label_cont)
        desc_label.set_text(app.short_description)
        desc_label.set_style_text_font(lv.font_montserrat_12, 0)
        desc_label.add_event_cb(lambda e, a=app: show_app_detail(a), lv.EVENT.CLICKED, None)
        print("create_apps_list app one done")
    print("create_apps_list app done")


def show_app_detail(app):
    global app_detail_screen, install_button
    app_detail_screen = lv.obj()
    app_detail_screen.set_size(lv.pct(100), lv.pct(100))
    back_button = lv.button(app_detail_screen)
    back_button.set_size(30, 30)
    back_button.add_flag(lv.obj.FLAG.CLICKABLE)
    back_button.add_event_cb(back_to_main, lv.EVENT.CLICKED, None)
    back_label = lv.label(back_button)
    back_label.set_text(lv.SYMBOL.LEFT)
    back_label.center()
    cont = lv.obj(app_detail_screen)
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
    install_button = lv.button(detail_cont)
    install_button.set_size(lv.pct(100), 40)
    install_button.add_flag(lv.obj.FLAG.CLICKABLE)
    install_button.add_event_cb(toggle_install, lv.EVENT.CLICKED, None)
    install_label = lv.label(install_button)
    install_label.set_text("Install")
    install_label.center()
    long_desc_label = lv.label(detail_cont)
    long_desc_label.set_text(app.long_description)
    long_desc_label.set_style_text_font(lv.font_montserrat_12, 0)
    long_desc_label.set_width(lv.pct(100))
    lv.screen_load(app_detail_screen)


def toggle_install(event):
    global install_button
    label = install_button.get_child(0)
    if label.get_text() == "Install":
        label.set_text("Cancel")
    else:
        label.set_text("Install")


def back_to_main(event):
    if app_detail_screen:
        app_detail_screen.delete()
        app_detail_screen = None
    lv.screen_load(appscreen)


print("appstore.py starting")
please_wait_label = lv.label(subwindow)
please_wait_label.set_text("Please wait...")
please_wait_label.center()
download_apps("http://demo.lnpiggy.com:2121/apps.json")

# Wait until the user stops the app
import time
while appscreen == lv.screen_active() or app_detail_screen == lv.screen_active():
    time.sleep_ms(100)

print("reached end of appstore")
