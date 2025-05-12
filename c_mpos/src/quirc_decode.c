#include "py/obj.h"
#include "py/runtime.h"
#include "py/mperrno.h"

#include <string.h>

#include "../quirc/lib/quirc.h"

// Function to decode a QR code from a grayscale image buffer
static mp_obj_t qrdecode(mp_uint_t n_args, const mp_obj_t *args) {
    printf("qrdecode running\n")
    // Check argument count (expecting buffer, width, height)
    if (n_args != 3) {
        mp_raise_ValueError(MP_ERROR_TEXT("quirc_decode expects 3 arguments: buffer, width, height"));
    }

    // Extract buffer
    mp_buffer_info_t bufinfo;
    mp_get_buffer_raise(args[0], &bufinfo, MP_BUFFER_READ);

    // Extract width and height
    mp_int_t width = mp_obj_get_int(args[1]);
    mp_int_t height = mp_obj_get_int(args[2]);

    // Validate dimensions
    if (width <= 0 || height <= 0) {
        mp_raise_ValueError(MP_ERROR_TEXT("width and height must be positive"));
    }
    if (bufinfo.len != (size_t)(width * height)) {
        mp_raise_ValueError(MP_ERROR_TEXT("buffer size must match width * height"));
    }

    // Initialize quirc
    struct quirc *qr = quirc_new();
    if (!qr) {
        mp_raise_OSError(MP_ENOMEM);
    }

    // Resize quirc for the image dimensions
    if (quirc_resize(qr, width, height) < 0) {
        quirc_destroy(qr);
        mp_raise_OSError(MP_ENOMEM);
    }

    // Get quirc image buffer and copy grayscale data
    uint8_t *image;
    quirc_begin(qr, NULL, NULL);
    image = quirc_begin(qr, NULL, NULL); // Get pointer to quirc's image buffer
    memcpy(image, bufinfo.buf, width * height); // Copy buffer directly (grayscale, 8-bit)
    quirc_end(qr);

    // Check for QR codes
    int count = quirc_count(qr);
    if (count == 0) {
        quirc_destroy(qr);
        mp_raise_ValueError(MP_ERROR_TEXT("no QR code found"));
    }

    // Extract and decode the first QR code
    struct quirc_code code;
    struct quirc_data data;
    quirc_extract(qr, 0, &code); // Extract first QR code

    // Decode the QR code
    int err = quirc_decode(&code, &data);
    if (err != QUIRC_SUCCESS) {
        quirc_destroy(qr);
        mp_raise_ValueError(MP_ERROR_TEXT("failed to decode QR code"));
    }

    // Convert decoded data to Python string
    mp_obj_t result = mp_obj_new_str((const char *)data.payload, data.payload_len);

    // Clean up
    quirc_destroy(qr);

    return result;
}

// Define the MicroPython function
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(qrdecode_obj, 3, 3, qrdecode);

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
