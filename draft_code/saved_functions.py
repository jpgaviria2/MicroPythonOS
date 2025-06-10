


import network
import time
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("SSIDHERE", "PASSWORDHERE")
print("Connecting to Wi-Fi...")
time.sleep(5)
start_app("/apps/com.example.appstore")




import mip
mip.install('github:echo-lalia/qmi8658-micropython')
# remove multi line comments

from machine import Pin, I2C
from qmi8658 import QMI8658
import time
import machine
sensor = QMI8658(I2C(0, sda=machine.Pin(48), scl=machine.Pin(47)))
print(f"""
QMI8685
{sensor.temperature=}
{sensor.acceleration=}
{sensor.gyro=}
""")



wifi_icon = lv.label(lv.screen_active())
wifi_icon.set_text("Test label")
wifi_icon.align(lv.ALIGN.CENTER, 0, 0)
wifi_icon.set_style_text_color(lv.color_hex(0x0000FF), 0)




# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()



# Fetch Bitcoin block height from mempool.space
def get_block_height():
    try:
        response = urequests.get("https://mempool.space/api/blocks/tip/height")
        if response.status_code == 200:
            height = response.text.strip()  # Returns plain text (e.g., "853123")
            response.close()
            return height
        else:
            response.close()
            return "Error: HTTP " + str(response.status_code)
    except Exception as e:
        return "Error: " + str(e)

def show_block_height():
	# Create a label for block height
	label = lv.label(scr)
	label.set_text("Bitcoin Block Height: Fetching...")
	label.set_style_text_color(lv.color_make(0, 255, 0), 0)  # Green text
	label.set_style_text_font(lv.font_montserrat_16, 0)  # Larger font (if available)
	label.align(lv.ALIGN.TOP_LEFT, 10, 200)
	#label.center()
	
	# Style for label background
	style = lv.style_t()
	style.init()
	style.set_bg_color(lv.palette_main(lv.PALETTE.DARK))  # Dark background
	style.set_border_width(2)
	style.set_border_color(lv.color_make(255, 255, 255))  # White border
	style.set_pad_all(10)
	style.set_radius(10)
	label.add_style(style, 0)
	
	height = get_block_height()
	label.set_text(f"Block Height: {height}")
	






# Create file explorer widget
file_explorer = lv.file_explorer(lv.screen_active())
#file_explorer.set_root_path("/")
#file_explorer.explorer_open_dir('/')
file_explorer.explorer_open_dir('P:.') # POSIX works, fs_driver doesn't because it doesn't have dir_open, dir_read, dir_close
#file_explorer.explorer_open_dir('S:/')
file_explorer.set_size(210, 210)
#file_explorer.set_mode(lv.FILE_EXPLORER.MODE.DEFAULT)  # Default browsing mode
#file_explorer.set_sort(lv.FILE_EXPLORER.SORT.NAME_ASC)  # Sort by name, ascending
file_explorer.align(lv.ALIGN.CENTER, 0, 0)
def file_explorer_event_cb(e):
    code = e.get_code()
    print(f"file_explorer_event_cb {code}")
    obj = e.get_target_obj()
    if code == lv.EVENT.VALUE_CHANGED:
        #selected_path = obj.get_selected_file_name()
        selected_path = file_explorer.explorer_get_selected_file_name()
        print("Selected:", selected_path)
        #if obj.is_selected_dir():
        #    print("This is a directory")
        #else:
        #    print("This is a file")


# Attach event callback
file_explorer.add_event_cb(file_explorer_event_cb, lv.EVENT.VALUE_CHANGED, None)





#show_block_height()

# Connect to Wi-Fi and fetch block height
#if connect_wifi():
#else:
#    label.set_text("Block Height: Wi-Fi Error")


import os
print(os.listdir('/')) 
try:
    with open('/boot.py', 'r') as file:
        print("Contents of /boot.py:")
        print("-" * 20)
        for line in file:
            print(line.rstrip())  # Remove trailing newlines for clean output
except OSError as e:
    print("Error reading /boot.py:", e)

#with open('/block_height.txt', 'w') as f:
#    f.write('853123')






# ffmpeg isn't compiled in...
# Create video widget
subwindow.clean()
video = lv.video(subwindow)
video.set_size(320, 200)
video.center()

# Open and play video using LVGL's FFmpeg backend
video_path = "/video/video_320x180.avi"
video.set_src(f"file://{video_path}")
video.set_play_mode(lv.VIDEO_PLAY_MODE.PLAY)  # Start playback
video.play()


script_globals = {
    'lv': lv,
    #'subwindow': lvgl_obj,
}

with open("/launcher.py", 'r') as f:
    script_source = f.read()


exec(script_source, script_globals)







# Debug file system
image_path = "/test.jpg"
try:
    print("Checking file system...")
    print(f"Apps dir: {uos.listdir('/apps')}")
    print(f"App1 dir: {uos.listdir('/apps/com.example.app1')}")
    print(f"Res dir: {uos.listdir('/apps/com.example.app1/res')}")
    print(f"Mipmap dir: {uos.listdir('/apps/com.example.app1/res/mipmap-mdpi')}")
    print(f"File exists: {image_path in uos.listdir('/apps/com.example.app1/res/mipmap-mdpi')}")
except Exception as e:
    print(f"File system error: {e}")

# Load and display the image
print("Creating image widget...")
image = lv.image(lv.screen_active())
try:
    print(f"Loading image: {image_path}")
    image.set_src(image_path)
    image.align(lv.ALIGN.CENTER, 0, 0)
    print("Image loaded and aligned")
except Exception as e:
    print(f"Image load error: {e}")

# Debug screen and widget
print(f"Screen active: {lv.screen_active()}")
print(f"Image widget: {image}")







# Debug display
#print(f"Display registered: {lv.disp}")
#print(f"Display resolution: {lv.display_get_horizontal_resolution(lv.disp)}x{lv.display_get_vertical_resolution(lv.disp)}")

# lv.lodepng_init() not needed


# PNG:
with open("/icon_64x64.png", 'rb') as f:
  image_data = f.read()
image_dsc = lv.image_dsc_t({
    'data_size': len(image_data),
    'data': image_data 
})
image1 = lv.image(lv.screen_active())
image1.set_src(image_dsc)
image1.set_pos(150,100)




# GIF:
#with open("../icons/spongebob_happy_love_it.gif", 'rb') as f:
with open("../icons/corel-draw-icon-5662.png", 'rb') as f:
with open("../icons/cpu_3dbd2b17ab4c68a4eb7e4034ab7c1c0e.jpg", 'rb') as f:
with open("../icons/pngtree-update-icon-glossy-blue-round-button-symbol-rotate-button-photo-image_18021430.jpg", 'rb') as f:
with open("../icons/hello_world_8844577_64x64.png", 'rb') as f: # one of the only images that works!
with open("../icons/Spinning-Wheel-Vector-PNG-Cutout_64x64.png", 'rb') as f: # this also works...
with open("../icons/pngtree-update-icon-glossy-blue-round-button-symbol-rotate-button-photo-image_18021430_square.png", 'rb') as f: # dontwork
    print("loading image...")
    image_data = f.read()
    image_dsc = lv.image_dsc_t({
        'data_size': len(image_data),
        'data': image_data 
    })
    print(f"loaded {len(image_data)} bytes")
    screen = lv.screen_active()
    screen.clean()
    image = lv.image(screen)
    image.set_src(image_dsc)
    #image1.set_pos(10,10)
    #image.set_size(323,404)
    image.align(lv.ALIGN.TOP_MID, 0, 0)
    print("done")


# lv.gd_open_gif_file())

#with open("../icons/graphics-snakes-834669.gif", 'rb') as f: # works
with open("../icons/spongebob_happy_love_it.gif", 'rb') as f: # works
with open("../icons/big-buck-bunny_320x180.gif", 'rb') as f: # works
    print("loading image...")
    image_data = f.read()
    image_dsc = lv.image_dsc_t({
        'data_size': len(image_data),
        'data': image_data 
    })
    print(f"loaded {len(image_data)} bytes")
    screen = lv.screen_active()
    screen.clean()
    gif = lv.gif(screen)
    gif.set_src(image_dsc)
    gif.align(lv.ALIGN.TOP_MID, 0, 0)
    print("done")



# BIN
with open("/icon_64x64.bin", 'rb') as f:
  image_data = f.read()

image_dsc = lv.image_dsc_t({
    'data_size': len(image_data),
    'data': image_data 
})
image1 = lv.image(subwindow)
image1.set_src(image_data)
image1.set_pos(150,100)




# BIN
with open("/icon_64x64.bin", 'rb') as f:
  image_data = f.read()

image_dsc = lv.image_dsc_t({
    'data_size': len(image_data),
    'data': image_data 
})
image1 = lv.image(subwindow)
image1.set_src("A:/icon_64x64.bin")
image1.set_pos(150,100)
image1 = lv.image(subwindow)
image1.set_src("/icon_64x64.bin")
image1.set_pos(150,100)

# WORKING BIN:
import lvgl as lv
import utime

# Initialize LVGL (assuming already done)
lv.init()

# Load the binary image data (including 12-byte header)
with open("/icon_64x64.bin", 'rb') as f:
    image_data = f.read()

# Verify the data size (64x64 RGB565 + 12-byte header = 8204 bytes)
if len(image_data) != 8204:
    raise ValueError("Invalid image data size")

# Keep image_data alive to prevent garbage collection
global_image_data = image_data  # Store globally to pin in memory

# Create an lv_image_dsc_t descriptor, letting LVGL parse the header
image_dsc = lv.image_dsc_t({
    "header": {
        "magic": lv.IMAGE_HEADER_MAGIC,
        "w": 64,
        "h": 64,
        "stride": 64 * 2,
        "cf": lv.COLOR_FORMAT.RGB565
    },
    "data": global_image_data,       # Entire 8204 bytes (header + pixel data)
    "data_size": len(image_data)     # Total size (8204 bytes)
})

# Create an image widget
img = lv.image(lv.screen_active())
img.set_src(image_dsc)  # Set the image source to the descriptor
img.center()  # Center the image on the screen









try:
    print("Checking file system...")
    print(f"Apps dir: {uos.listdir('/apps')}")
    print(f"App1 dir: {uos.listdir('/apps/com.example.app1')}")
    print(f"Res dir: {uos.listdir('/apps/com.example.app1/res')}")
    print(f"Mipmap dir: {uos.listdir('/apps/com.example.app1/res/mipmap-mdpi')}")
    print(f"File exists: {image_path in uos.listdir('/apps/com.example.app1/res/mipmap-mdpi')}")
except Exception as e:
    print(f"File system error: {e}")

# Create a label to ensure something displays
label = lv.label(lv.screen_active())
label.set_text("Loading image...")
label.align(lv.ALIGN.TOP_MID, 0, 10)
print("Label created")

# Load the image


# Load and display the image
print("Creating image widget...")
image = lv.image(lv.screen_active())
try:
    print(f"Loading image: {image_path}")
    image.set_src(image_path)
    image.align(lv.ALIGN.CENTER, 0, 0)
    print("Image loaded and aligned")
except Exception as e:
    print(f"Image load error: {e}")
    print("Falling back to SYMBOL.DUMMY")
    image.set_src(lv.SYMBOL.DUMMY)
    image.align(lv.ALIGN.CENTER, 0, 0)

# Debug image properties
print(f"Screen active: {lv.screen_active()}")
print(f"Image widget: {image}")
print(f"Image source: {image.get_src()}")
print(f"Image size: {image.get_width()}x{image.get_height()}")



wifi_icon = lv.label(lv.screen_active())
wifi_icon.set_text(lv.SYMBOL.WIFI)
wifi_icon.align(lv.ALIGN.RIGHT_CENTER, 0, 0)
wifi_icon.set_style_text_color(COLOR_TEXT_WHITE, 0)





# Create a label
label = lv.label(subwindow)
label.set_text("Monospace Text")
label.align(lv.ALIGN.CENTER, 0, -40)

# Create a style for the label
style = lv.style_t()
style.init()
style.set_text_font(lv.font_montserrat_12)  
label.add_style(style, 0)  # Apply style to the label


# Create a label
label = lv.label(subwindow)
label.set_text("Monospace Text")
label.align(lv.ALIGN.CENTER, 0, -20)

# Create a style for the label
style = lv.style_t()
style.init()
style.set_text_font(lv.font_montserrat_14)  # Default font
label.add_style(style, 0)  # Apply style to the label



# Create a label
label = lv.label(subwindow)
label.set_text("Monospace Text")
label.align(lv.ALIGN.CENTER, 0, 0)

# Create a style for the label
style = lv.style_t()
style.init()
style.set_text_font(lv.font_montserrat_16)  
label.add_style(style, 0)  # Apply style to the label


# Create a label
label = lv.label(subwindow)
label.set_text("Monospace Text")
label.align(lv.ALIGN.CENTER, 0, 40)

# Create a style for the label
style = lv.style_t()
style.init()
style.set_text_font(lv.font_unscii_8)  # Set monospace font
label.add_style(style, 0)  # Apply style to the label

# Create a label
label = lv.label(subwindow)
label.set_text("Monospace Text")
label.align(lv.ALIGN.CENTER, 0, 60)

# Create a style for the label
style = lv.style_t()
style.init()
style.set_text_font(lv.font_unscii_16)  # Set monospace font
label.add_style(style, 0)  # Apply style to the label





# delete folder:
import mip
mip.install("shutil")
import shutil
shutil.rmtree('/apps/com.example.files')



import vfs
vfs.umount('/')
vfs.VfsLfs2.mkfs(bdev)
vfs.mount(bdev, '/')



def memoryview_to_hex_spaced(mv: memoryview) -> str:
    """Convert the first 50 bytes of a memoryview to a spaced hex string."""
    sliced = mv[:50]
    return ' '.join('{:02x}'.format(b & 0xFF) for b in sliced)
















subwindow.clean()
canary = lv.obj(subwindow)
canary.add_flag(lv.obj.FLAG.HIDDEN)

subwindow.set_style_bg_color(lv.color_black(), 0)

label = lv.label(subwindow)
label.set_text("Hello \uf0ac")  # Unicode for a symbol (e.g., globe)
label.align(lv.ALIGN.CENTER, 0, 0)

label2 = lv.label(subwindow)
label2.set_text("Hello " + lv.SYMBOL.DOWNLOAD)
label2.align(lv.ALIGN.CENTER, 0, 25)


label2 = lv.label(subwindow)
label2.set_text("Hello " + lv.SYMBOL.DUMMY)
label2.align(lv.ALIGN.CENTER, 0, 50)


image = lv.image(subwindow)
image.align(lv.ALIGN.CENTER, 0, -50)
image.set_src(lv.SYMBOL.STOP)  # Or use a default image





>>> import ota.update
>>> ota.update.from_file("https://demo.lnpiggy.com/static/firmware/ESP32_GENERIC_S3-SPIRAM_OCT_micropython.bin")


temp_zip_path = "/apps/temp.zip"
print('\nReading file')
with ZipFile(temp_zip_path) as myzip:
    with myzip.open('com.example.files/META-INF/MANIFEST.MF') as myfile:
        print(myfile.read())



import os
try:
    import zipfile
except ImportError:
    zipfile = None


temp_zip_path = "/apps/temp.zip"
print('\nReading file')
with zipfile.ZipFile(temp_zip_path) as myzip:
    with myzip.open('com.example.files/assets/files.py') as myfile:
        print(myfile.read())


import os
try:
    import zipfile
except ImportError:
    zipfile = None

temp_zip_path = "/apps/temp.zip"
print(f"Stat says: {os.stat(temp_zip_path)}")
with zipfile.ZipFile(temp_zip_path, "r") as zip_ref:
    print("extracting...")
    zip_ref.extractall("/apps")
    










subwindow = lv.obj(newscreen)
subwindow.set_size(TFT_HOR_RES, TFT_VER_RES - NOTIFICATION_BAR_HEIGHT)
subwindow.set_pos(0, NOTIFICATION_BAR_HEIGHT)
subwindow.set_style_border_width(0, 0)
subwindow.set_style_pad_all(0, 0)
lv.screen_load(newscreen)
script_globals = {
    'lv': lv,
    'appscreen': newscreen,
    'subwindow': subwindow,
    'start_app': start_app, # for launcher apps
    'parse_manifest': parse_manifest, # for launcher apps
    '__name__': "__main__"
}



import lvgl as lv

# Buffer to store FPS
fps_buffer = [0]

# Custom log callback to capture FPS
def log_callback(level, log_str):
    global fps_buffer
    # Convert log_str to string if it's a bytes object
    log_str = log_str.decode() if isinstance(log_str, bytes) else log_str
    # Optional: Print for debugging
    print(f"Level: {level}, Log: {log_str}")
    # Log message format: "sysmon: 25 FPS (refr_cnt: 8 | redraw_cnt: 1), ..."
    if "sysmon:" in log_str and "FPS" in log_str:
        try:
            # Extract FPS value (e.g., "25" from "sysmon: 25 FPS ...")
            fps_part = log_str.split("FPS")[0].split("sysmon:")[1].strip()
            fps = int(fps_part)
            fps_buffer[0] = fps
        except (IndexError, ValueError):
            pass

# Register log callback
lv.log_register_print_cb(log_callback)


# Function to get FPS
def get_fps():
    return fps_buffer[0]


#fps = get_fps()
#if fps > 0:  # Only print when FPS is updated
#    print("Current FPS:", fps)


# Main loop
def print_fps():
    for _ in range(100):
        import time
        fps = get_fps()
        if fps > 0:  # Only print when FPS is updated
            print("Current FPS:", fps)
        time.sleep(1)


import _thread
_thread.stack_size(12*1024)
_thread.start_new_thread(print_fps, ())

# crash:

label = lv.label(lv.screen_active())
label.delete()
gc.collect()
label.set_text("Crash!")  # This will crash
label.set_text(None)
label.set_size(100000, 1000000)

buf = lv.draw_buf_create(10, 10, lv.COLOR_FORMAT.RGB565, 1)
buf.data[1000000] = 0xFF  # Write way beyond buffer size

# this works to crash it:
from machine import mem32
mem32[0] = 0xDEADBEEF 



# testing stack size: recursion depth * 256 
#normally I get ~16KB

import _thread
_thread.stack_size(0)



import fs_driver
fs_drv = lv.fs_drv_t()
fs_driver.fs_register(fs_drv, 'M')

img = lv.image(lv.screen_active())
#img.set_src("P:/data/images/icon_64x64.jpg")
img.set_src("P:../artwork/icon_64x64.jpg")

