import uos
#import ufs
import uio
import machine

# Function to parse MANIFEST.MF
def parse_manifest(manifest_path):
    name = "Unknown"
    try:
        with uio.open(manifest_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith("Name:"):
                    name = line.split(":", 1)[1].strip()
                    break
    except OSError:
        print(f"Error reading {manifest_path}")
    return name

# Function to load PNG icon
def load_icon(icon_path):
    try:
        img = lv.img(lv.screen_active())
        img.set_src(icon_path)
        return img
    except Exception as e:
        print(f"Error loading icon {icon_path}: {e}")
        # Fallback: create a placeholder image
        img = lv.img(lv.screen_active())
        img.set_src(lv.SYMBOL.DUMMY)  # Or use a default image
        return img

# Function to handle icon/label click
def on_app_click(event, app_name, app_dir):
    if event.get_code() == lv.EVENT.CLICKED:
        print(f"Launching app: {app_name} ({app_dir})")

# Create the app launcher
def create_app_launcher():
    # Get list of app directories
    apps_dir = "/apps"
    app_dirs = []
    try:
        app_dirs = [d for d in uos.listdir(apps_dir) if uos.stat(f"{apps_dir}/{d}")[0] & 0x4000]  # Directories only
    except OSError:
        print("Error accessing /apps directory")
        return

    # Create a container for the grid
    cont = lv.obj(lv.screen_active())
    cont.set_size(lv.pct(100), lv.pct(100))
    cont.set_style_pad_all(10, 0)
    cont.set_style_border_width(0, 0)
    cont.set_flex_flow(lv.FLEX_FLOW.ROW_WRAP)

    # Grid parameters
    icon_size = 64  # Adjust based on your display
    label_height = 20
    col_gap = 20
    row_gap = 20

    for app_dir in app_dirs:
        # Paths
        base_path = f"{apps_dir}/{app_dir}"
        icon_path = f"{base_path}/res/mipmap-mdpi/launcher_icon.png"
        manifest_path = f"{base_path}/META-INF/MANIFEST.MF"

        # Get app name from MANIFEST.MF
        app_name = parse_manifest(manifest_path)

        # Create a container for each app (icon + label)
        app_cont = lv.obj(cont)
        app_cont.set_size(icon_size, icon_size + label_height)
        app_cont.set_style_border_width(0, 0)
        app_cont.set_style_pad_all(0, 0)

        # Load and display icon
        img = load_icon(icon_path)
        img.align(lv.ALIGN.TOP_MID, 0, 0)
        img.set_size(icon_size, icon_size)

        # Create label
        label = lv.label(app_cont)
        label.set_text(app_name)
        label.set_long_mode(lv.label.LONG.WRAP)
        label.set_width(icon_size)
        label.align(lv.ALIGN.BOTTOM_MID, 0, 0)
        label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)

        # Add click event to both icon and label
        img.add_event_cb(lambda e: on_app_click(e, app_name, app_dir), lv.EVENT.CLICKED, None)
        label.add_event_cb(lambda e: on_app_click(e, app_name, app_dir), lv.EVENT.CLICKED, None)

# Run the app launcher
create_app_launcher()

