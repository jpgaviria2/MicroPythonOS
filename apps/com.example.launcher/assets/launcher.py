import uos

# Create a container for the grid
cont = lv.obj(subwindow)
cont.set_size(lv.pct(100), lv.pct(100))
cont.set_style_pad_all(10, 0)
cont.set_style_border_width(0, 0)
cont.set_flex_flow(lv.FLEX_FLOW.ROW_WRAP)

# Grid parameters
icon_size = 64  # Adjust based on your display
label_height = 24
iconcont_width = icon_size + 24
iconcont_height = icon_size + label_height

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
    #icon_path = f"{base_path}/res/mipmap-mdpi/launcher_icon.png"
    icon_path = "/resources/icon_64x64.bin"
    image = lv.image(app_cont)
    try:
        with open(icon_path, 'rb') as f:
            f.seek(12) # first 12 bytes are headers
            image_data = f.read()
            image_dsc = lv.image_dsc_t({
                "header": {
                    "magic": lv.IMAGE_HEADER_MAGIC,
                    "w": 64,
                    "h": 64,
                    "stride": 64 * 2,
                    "cf": lv.COLOR_FORMAT.RGB565
                 },
                'data_size': len(image_data),
                'data': image_data
            })
            image.set_src(image_dsc)
    except Exception as e:
        print(f"Error loading icon {icon_path}: {e}")
        image.set_src(lv.SYMBOL.DUMMY)  # Or use a default image
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


