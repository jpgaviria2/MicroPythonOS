#include <stdio.h>
#include <esp_log.h> // For ESP-IDF logging
#include "py/obj.h"
#include "py/runtime.h"
#include "py/mperrno.h"
#include <string.h>
#include "../quirc/lib/quirc.h"

#define QRDECODE_DEBUG_PRINT(...) mp_printf(&mp_plat_print, __VA_ARGS__);

static const char *TAG = "qrdecode";

// Function to decode a QR code from a grayscale image buffer
static mp_obj_t qrdecode(mp_uint_t n_args, const mp_obj_t *args) {
    printf("qrdecode: Starting\n");
    ESP_LOGI(TAG, "qrdecode starting");
    QRDECODE_DEBUG_PRINT("mp_printf works in qrdecode!");
    fflush(stdout);

    // Check argument count (expecting buffer, width, height)
    QRDECODE_DEBUG_PRINT("qrdecode: Checking argument count\n");
    ESP_LOGI(TAG, "Checking argument count");
    fflush(stdout);
    if (n_args != 3) {
        mp_raise_ValueError(MP_ERROR_TEXT("quirc_decode expects 3 arguments: buffer, width, height"));
    }

    // Extract buffer
    QRDECODE_DEBUG_PRINT("qrdecode: Extracting buffer\n");
    ESP_LOGI(TAG, "Extracting buffer");
    fflush(stdout);
    mp_buffer_info_t bufinfo;
    mp_get_buffer_raise(args[0], &bufinfo, MP_BUFFER_READ);
    printf("qrdecode: Buffer extracted, len=%zu\n", bufinfo.len);
    ESP_LOGI(TAG, "Buffer extracted, len=%zu", bufinfo.len);

    // Extract width and height
    QRDECODE_DEBUG_PRINT("qrdecode: Extracting width and height\n");
    fflush(stdout);
    mp_int_t width = mp_obj_get_int(args[1]);
    mp_int_t height = mp_obj_get_int(args[2]);
    QRDECODE_DEBUG_PRINT("qrdecode: Width=%ld, Height=%ld\n", width, height);
    fflush(stdout);

    // Validate dimensions
    QRDECODE_DEBUG_PRINT("qrdecode: Validating dimensions\n");
    fflush(stdout);
    if (width <= 0 || height <= 0) {
        mp_raise_ValueError(MP_ERROR_TEXT("width and height must be positive"));
    }
    if (bufinfo.len != (size_t)(width * height)) {
        mp_raise_ValueError(MP_ERROR_TEXT("buffer size must match width * height"));
    }
    QRDECODE_DEBUG_PRINT("qrdecode: Dimensions validated\n");
    fflush(stdout);

    // Initialize quirc
    QRDECODE_DEBUG_PRINT("qrdecode: Initializing quirc\n");
    fflush(stdout);
    struct quirc *qr = quirc_new();
    if (!qr) {
        mp_raise_OSError(MP_ENOMEM);
    }
    QRDECODE_DEBUG_PRINT("qrdecode: quirc initialized\n");
    QRDECODE_DEBUG_PRINT("mp_printf works in qrdecode!");
    fflush(stdout);

    // Resize quirc for the image dimensions
    QRDECODE_DEBUG_PRINT("qrdecode: Resizing quirc\n");
    fflush(stdout);
    if (quirc_resize(qr, width, height) < 0) {
        quirc_destroy(qr);
        mp_raise_OSError(MP_ENOMEM);
    }
    QRDECODE_DEBUG_PRINT("qrdecode: quirc resized\n");
    fflush(stdout);

    // Get quirc image buffer and copy grayscale data
    QRDECODE_DEBUG_PRINT("qrdecode: Beginning quirc processing\n");
    fflush(stdout);
    uint8_t *image;
    quirc_begin(qr, NULL, NULL);
    image = quirc_begin(qr, NULL, NULL); // Get pointer to quirc's image buffer
    QRDECODE_DEBUG_PRINT("qrdecode: quirc image buffer obtained\n");
    fflush(stdout);
    QRDECODE_DEBUG_PRINT("qrdecode: Copying buffer, size=%zu\n", (size_t)(width * height));
    fflush(stdout);
    memcpy(image, bufinfo.buf, width * height);
    QRDECODE_DEBUG_PRINT
    fflush(stdout);
    quirc_end(qr);
    QRDECODE_DEBUG_PRINT("qrdecode: quirc processing ended\n");
    fflush(stdout);

    // Check for QR codes
    QRDECODE_DEBUG_PRINT("qrdecode: Counting QR codes\n");
    fflush(stdout);
    int count = quirc_count(qr);
    QRDECODE_DEBUG_PRINT("qrdecode: Found %d QR codes\n", count);
    fflush(stdout);
    if (count == 0) {
        quirc_destroy(qr);
        mp_raise_ValueError(MP_ERROR_TEXT("no QR code found"));
    }

    // Extract and decode the first QR code
    QRDECODE_DEBUG_PRINT("qrdecode: Extracting first QR code\n");
    fflush(stdout);
    struct quirc_code code;
    quirc_extract(qr, 0, &code);
    QRDECODE_DEBUG_PRINT("qrdecode: QR code extracted\n");
    fflush(stdout);

    // Decode the QR code
    QRDECODE_DEBUG_PRINT("qrdecode: Decoding QR code\n");
    fflush(stdout);
    struct quirc_data data;
    int err = quirc_decode(&code, &data);
    if (err != QUIRC_SUCCESS) {
        quirc_destroy(qr);
        mp_raise_ValueError(MP_ERROR_TEXT("failed to decode QR code"));
    }
    QRDECODE_DEBUG_PRINT("qrdecode: QR code decoded, payload_len=%d\n", data.payload_len);
    fflush(stdout);

    // Convert decoded data to Python string
    QRDECODE_DEBUG_PRINT("qrdecode: Creating Python string\n");
    fflush(stdout);
    mp_obj_t result = mp_obj_new_str((const char *)data.payload, data.payload_len);
    printf("qrdecode: Python string created\n");
    fflush(stdout);

    // Clean up
    QRDECODE_DEBUG_PRINT("qrdecode: Cleaning up\n");
    fflush(stdout);
    quirc_destroy(qr);
    QRDECODE_DEBUG_PRINT("qrdecode: quirc destroyed\n");
    fflush(stdout);

    printf("qrdecode: Returning result\n");
    return result;
    //return mp_const_none; // MicroPython functions typically return None
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
