#define PWDN_GPIO_NUM 17  //power down is not used
#define RESET_GPIO_NUM -1 //software reset will be performed
#define XCLK_GPIO_NUM 8
#define SIOD_GPIO_NUM 21
#define SIOC_GPIO_NUM 16

#define Y9_GPIO_NUM 2
#define Y8_GPIO_NUM 7
#define Y7_GPIO_NUM 10
#define Y6_GPIO_NUM 14
#define Y5_GPIO_NUM 11
#define Y4_GPIO_NUM 15
#define Y3_GPIO_NUM 13
#define Y2_GPIO_NUM 12
#define VSYNC_GPIO_NUM 6
#define HREF_GPIO_NUM 4
#define PCLK_GPIO_NUM 9

#define CAM_LEDC_TIMER      LEDC_TIMER_1
#define CAM_LEDC_CHANNEL    LEDC_CHANNEL_0


from camera import Camera, GrabMode, PixelFormat, FrameSize, GainCeiling

cam = Camera(
    data_pins=[12,13,15,11,14,10,7,2],
    vsync_pin=6,
    href_pin=4,
    sda_pin=21,
    scl_pin=16,
    pclk_pin=9,
    xclk_pin=8,
    xclk_freq=20000000,
    powerdown_pin=-1,
    reset_pin=-1,
    #pixel_format=PixelFormat.RGB565,frame_size=FrameSize.QQVGA,grab_mode=GrabMode.LATEST # 160x120, FrameSize.QVGA = 320x240
    #pixel_format=PixelFormat.JPEG,frame_size=FrameSize.QVGA,grab_mode=GrabMode.LATEST
)

cam.init()

#cam.reconfigure(pixel_format=PixelFormat.RAW,frame_size=FrameSize.QVGA,grab_mode=GrabMode.LATEST, fb_count=2)
#cam.reconfigure(pixel_format=PixelFormat.YUV420,frame_size=FrameSize.QVGA,grab_mode=GrabMode.LATEST, fb_count=2)

#img = cam.capture()

def memoryview_to_hex_spaced(mv: memoryview) -> str:
    """Convert the first 50 bytes of a memoryview to a spaced hex string."""
    sliced = mv[:50]
    return ' '.join('{:02x}'.format(b & 0xFF) for b in sliced)

#memoryview_to_hex_spaced(img)


def capture():
    width = 160
    height = 120
    image = lv.image(subwindow)
    image_data = cam.capture()
    memoryview_to_hex_spaced(image_data)
    image_dsc = lv.image_dsc_t({
        "header": {
            "magic": lv.IMAGE_HEADER_MAGIC,
            "w": width,
            "h": height,
            "stride": width * 2,
            "cf": lv.COLOR_FORMAT.RGB565
            },
        'data_size': len(image_data),
        'data': image_data
    })
    image.set_src(image_dsc)
    image.align(lv.ALIGN.TOP_MID, 0, 0)
    image.set_size(width, height)

#for _ in range(10):
#    capture()

capture()
