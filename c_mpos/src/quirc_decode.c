#include "py/obj.h"
#include "py/runtime.h"
#include "py/mperrno.h"
#include <string.h>
#include "../quirc/lib/quirc.h"

// Function to decode a QR code from a grayscale image buffer
static mp_obj_t qrdecode(mp_uint_t n_args, const mp_obj_t *args) {
    printf("qrdecode: Starting\n");

    // Check argument count (expecting buffer, width, height)
    printf("qrdecode: Checking argument count\n");
    if (n_args != 3) {
        mp_raise_ValueError(MP_ERROR_TEXT("quirc_decode expects 3 arguments: buffer, width, height"));
    }

    // Extract buffer
    printf("qrdecode: Extracting buffer\n");
    mp_buffer_info_t bufinfo;
    mp_get_buffer_raise(args[0], &bufinfo, MP_BUFFER_READ);
    printf("qrdecode: Buffer extracted, len=%zu\n", bufinfo.len);

    // Extract width and height
    printf("qrdecode: Extracting width and height\n");
    mp_int_t width = mp_obj_get_int(args[1]);
    mp_int_t height = mp_obj_get_int(args[2]);
    printf("qrdecode: Width=%ld, Height=%ld\n", width, height);

    // Validate dimensions
    printf("qrdecode: Validating dimensions\n");
    if (width <= 0 || height <= 0) {
        mp_raise_ValueError(MP_ERROR_TEXT("width and height must be positive"));
    }
    if (bufinfo.len != (size_t)(width * height)) {
        mp_raise_ValueError(MP_ERROR_TEXT("buffer size must match width * height"));
    }
    printf("qrdecode: Dimensions validated\n");

    // Initialize quirc
    printf("qrdecode: Initializing quirc\n");
    struct quirc *qr = quirc_new();
    if (!qr) {
        mp_raise_OSError(MP_ENOMEM);
    }
    printf("qrdecode: quirc initialized\n");

    // Resize quirc for the image dimensions
    printf("qrdecode: Resizing quirc\n");
    if (quirc_resize(qr, width, height) < 0) {
        quirc_destroy(qr);
        mp_raise_OSError(MP_ENOMEM);
    }
    printf("qrdecode: quirc resized\n");

    // Get quirc image buffer and copy grayscale data
    printf("qrdecode: Beginning quirc processing\n");
    uint8_t *image;
    quirc_begin(qr, NULL, NULL);
    image = quirc_begin(qr, NULL, NULL); // Get pointer to quirc's image buffer
    printf("qrdecode: quirc image buffer obtained\n");
    printf("qrdecode: Copying buffer, size=%zu\n", (size_t)(width * height));
    memcpy(image, bufinfo.buf, width * height);
    printf("qrdecode: Buffer copied\n");
    quirc_end(qr);
    printf("qrdecode: quirc processing ended\n");

    // Check for QR codes
    printf("qrdecode: Counting QR codes\n");
    int count = quirc_count(qr);
    printf("qrdecode: Found %d QR codes\n", count);
    if (count == 0) {
        quirc_destroy(qr);
        mp_raise_ValueError(MP_ERROR_TEXT("no QR code found"));
    }

    // Extract and decode the first QR code
    printf("qrdecode: Extracting first QR code\n");
    struct quirc_code code;
    quirc_extract(qr, 0, &code);
    printf("qrdecode: QR code extracted\n");

    // Decode the QR code
    printf("qrdecode: Decoding QR code\n");
    struct quirc_data data;
    int err = quirc_decode(&code, &data);
    if (err != QUIRC_SUCCESS) {
        quirc_destroy(qr);
        mp_raise_ValueError(MP_ERROR_TEXT("failed to decode QR code"));
    }
    printf("qrdecode: QR code decoded, payload_len=%d\n", data.payload_len);

    // Convert decoded data to Python string
    printf("qrdecode: Creating Python string\n");
    mp_obj_t result = mp_obj_new_str((const char *)data.payload, data.payload_len);
    printf("qrdecode: Python string created\n");

    // Clean up
    printf("qrdecode: Cleaning up\n");
    quirc_destroy(qr);
    printf("qrdecode: quirc destroyed\n");

    printf("qrdecode: Returning result\n");
    return result;
}

// Wrapper function to fix incompatible pointer type warning
static mp_obj_t qrdecode_wrapper(size_t n_args, const mp_obj_t *args) {
    printf("qrdecode_wrapper: Called with %zu args\n", n_args);
    return qrdecode(n_args, args);
}

// Define the MicroPython function
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(qrdecode_obj, 3, 3, qrdecode_wrapper);

// Module definition
static const mp_rom_map_elem_t qrdecode_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_qrdecode) },
    { MP_ROM_QSTR(MP_QSTR_qrdecode), MP_ROM_PTR(&qrdecode_obj) },
};

static MP_DEFINE_CONST_DICT(qrdecode_module_globals, qrdecode_module_globals_table);

const mp_obj_module_t qrdecode_module = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&qrdecode_module_globals,
};

// Register the module
MP_REGISTER_MODULE(MP_QSTR_qrdecode, qrdecode_module);
