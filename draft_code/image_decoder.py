

import lvgl as lv

def list_image_decoders():
    # Initialize LVGL
    lv.init()

    # Start with the first decoder
    first = lv.image_decoder_t()
    #decoder = lv.image.decoder_get_next(first)
    decoder = lv.image_decoder_t.get_next(first)
    index = 0

    # Iterate through all decoders
    while decoder is not None:
        print(f"Image Decoder {index}: {decoder}")
        index += 1
        #decoder = lv.image.decoder_get_next(decoder)
        decoder = lv.image_decoder_t.get_next(decoder)

    if index == 0:
        print("No image decoders found.")
    else:
        print(f"Total image decoders: {index}")

# Run the function
list_image_decoders()


i = lv.image(lv.screen_active());
#i.set_src("P:/home/user/sources/MicroPythonOS/artwork/image.jpg");
i.set_src("P:/home/user/sources/MicroPythonOS/artwork/icon_64x64.jpg");
i.center()
h = lv.image_header_t()
i.decoder_get_info(i.image_dsc, h)
print("image info:")
print(h)
print(f"widthxheight: {h.w}x{h.h}")
