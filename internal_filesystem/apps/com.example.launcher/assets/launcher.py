# bin files:
# All icons took: 1085ms
# All icons took: 1051ms
# All icons took: 1032ms
# All icons took: 1118ms
# png files:
# All icons took: 1258ms
# All icons took: 1457ms
# All icons took: 1250ms
# Most of this time is actually spent reading and parsing manifests.

import uos


#myscreen = lv.screen_active()

# Create a container for the grid
cont = lv.obj(subwindow)
cont.set_size(lv.pct(100), lv.pct(100))
cont.set_style_pad_all(10, 0)
cont.set_flex_flow(lv.FLEX_FLOW.ROW_WRAP)

# Grid parameters
icon_size = 64  # Adjust based on your display
label_height = 24
iconcont_width = icon_size + 24
iconcont_height = icon_size + label_height

import time
start = time.ticks_ms()

def load_icon(icon_path):
    with open(icon_path, 'rb') as f:
        f.seek(12) # first 12 bytes are headers
        image_data = f.read()
        image_dsc = lv.image_dsc_t({
            "header": {
                "magic": lv.IMAGE_HEADER_MAGIC,
                "w": 64,
                "h": 64,
                "stride": 64 * 2,
                "cf": lv.COLOR_FORMAT.RGB565A8
                },
            'data_size': len(image_data),
            'data': image_data
        })
    return image_dsc

# Get list of app directories
# Should we skip 'Launcher' apps from the list here?
apps_dir = "/apps"
for app_dir in [d for d in uos.listdir(apps_dir) if uos.stat(f"{apps_dir}/{d}")[0] & 0x4000]:
    # Paths
    app_dir_fullpath = f"{apps_dir}/{app_dir}"
    app_name, main_script = parse_manifest(f"{app_dir_fullpath}/META-INF/MANIFEST.MF")
    # Create a container for each app (icon + label)
    app_cont = lv.obj(cont)
    app_cont.set_size(iconcont_width, iconcont_height)
    app_cont.set_style_border_width(0, 0)
    app_cont.set_style_pad_all(0, 0)
    # Load and display icon
    icon_path = f"{app_dir_fullpath}/res/mipmap-mdpi/icon_64x64.bin"
    image = lv.image(app_cont)
    try:
        image.set_src(load_icon(icon_path))
    except Exception as e:
        print(f"Error loading icon {icon_path}: {e} - loading default icon")
        icon_path = "/resources/default_icon_64x64.bin"
        try:
            image.set_src(load_icon(icon_path))
        except Exception as e:
            print(f"Error loading default icon {icon_path}: {e} - using symbol")
            image.set_src(lv.SYMBOL.STOP)  # square block
    image.align(lv.ALIGN.TOP_MID, 0, 0)
    image.set_size(icon_size, icon_size)
    # Create label
    label = lv.label(app_cont)
    label.set_text(app_name)
    label.set_long_mode(lv.label.LONG.WRAP)
    label.set_width(iconcont_width)
    label.align(lv.ALIGN.BOTTOM_MID, 0, 0)
    label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
    app_cont.add_event_cb(lambda e, app_dir_fullpath=app_dir_fullpath: start_app(app_dir_fullpath), lv.EVENT.CLICKED, None)

end = time.ticks_ms()
print(f"Displaying all icons took: {end-start}ms")

#print("checking active...")
#while myscreen == lv.screen_active():
#    print("still active")
#    time.sleep_ms(500)
