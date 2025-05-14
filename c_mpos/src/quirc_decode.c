#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "py/obj.h"
#include "py/runtime.h"
#include "py/mperrno.h"

#ifdef __xtensa__
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#else
size_t uxTaskGetStackHighWaterMark(void * unused) {
    return 99999999;
}
#endif

#include "../quirc/lib/quirc.h"

#define QRDECODE_DEBUG_PRINT(...) mp_printf(&mp_plat_print, __VA_ARGS__)

static mp_obj_t qrdecode(mp_uint_t n_args, const mp_obj_t *args) {
    QRDECODE_DEBUG_PRINT("qrdecode: Starting\n");
    QRDECODE_DEBUG_PRINT("qrdecode: Stack high-water mark: %u bytes\n", uxTaskGetStackHighWaterMark(NULL));

    if (n_args != 3) {
        mp_raise_ValueError(MP_ERROR_TEXT("quirc_decode expects 3 arguments: buffer, width, height"));
    }

    mp_buffer_info_t bufinfo;
    mp_get_buffer_raise(args[0], &bufinfo, MP_BUFFER_READ);

    mp_int_t width = mp_obj_get_int(args[1]);
    mp_int_t height = mp_obj_get_int(args[2]);
    QRDECODE_DEBUG_PRINT("qrdecode: Width=%u, Height=%u\n", width, height);

    if (width <= 0 || height <= 0) {
        mp_raise_ValueError(MP_ERROR_TEXT("width and height must be positive"));
    }
    if (bufinfo.len != (size_t)(width * height)) {
        mp_raise_ValueError(MP_ERROR_TEXT("buffer size must match width * height"));
    }

    struct quirc *qr = quirc_new();
    if (!qr) {
        mp_raise_OSError(MP_ENOMEM);
    }

    if (quirc_resize(qr, width, height) < 0) {
        quirc_destroy(qr);
        mp_raise_OSError(MP_ENOMEM);
    }

    uint8_t *image;
    quirc_begin(qr, NULL, NULL);
    image = quirc_begin(qr, NULL, NULL);
    memcpy(image, bufinfo.buf, width * height);
    quirc_end(qr);

    int count = quirc_count(qr);
    if (count == 0) {
        quirc_destroy(qr);
        mp_raise_ValueError(MP_ERROR_TEXT("no QR code found"));
    }

    struct quirc_code *code = (struct quirc_code *)malloc(sizeof(struct quirc_code));
    if (!code) {
        quirc_destroy(qr);
        mp_raise_OSError(MP_ENOMEM);
    }
    quirc_extract(qr, 0, code);

    struct quirc_data *data = (struct quirc_data *)malloc(sizeof(struct quirc_data));
    if (!data) {
        free(code);
        quirc_destroy(qr);
        mp_raise_OSError(MP_ENOMEM);
    }
    int err = quirc_decode(code, data);
    if (err != QUIRC_SUCCESS) {
        free(data);
        free(code);
        quirc_destroy(qr);
        mp_raise_ValueError(MP_ERROR_TEXT("failed to decode QR code"));
    }

    mp_obj_t result = mp_obj_new_bytes((const uint8_t *)data->payload, data->payload_len);

    free(data);
    free(code);
    quirc_destroy(qr);
    return result;
}

static mp_obj_t qrdecode_rgb565(mp_uint_t n_args, const mp_obj_t *args) {
    QRDECODE_DEBUG_PRINT("qrdecode_rgb565: Starting\n");

    if (n_args != 3) {
        mp_raise_ValueError(MP_ERROR_TEXT("qrdecode_rgb565 expects 3 arguments: buffer, width, height"));
    }

    mp_buffer_info_t bufinfo;
    mp_get_buffer_raise(args[0], &bufinfo, MP_BUFFER_READ);

    mp_int_t width = mp_obj_get_int(args[1]);
    mp_int_t height = mp_obj_get_int(args[2]);
    QRDECODE_DEBUG_PRINT("qrdecode_rgb565: Width=%u, Height=%u\n", width, height);

    if (width <= 0 || height <= 0) {
        mp_raise_ValueError(MP_ERROR_TEXT("width and height must be positive"));
    }
    if (bufinfo.len != (size_t)(width * height * 2)) {
        mp_raise_ValueError(MP_ERROR_TEXT("buffer size must match width * height * 2 for RGB565"));
    }

    uint8_t *gray_buffer = (uint8_t *)malloc(width * height * sizeof(uint8_t));
    if (!gray_buffer) {
        mp_raise_OSError(MP_ENOMEM);
    }

    uint16_t *rgb565 = (uint16_t *)bufinfo.buf;
    for (size_t i = 0; i < (size_t)(width * height); i++) {
        uint16_t pixel = rgb565[i];
        uint8_t r = ((pixel >> 11) & 0x1F) << 3;
        uint8_t g = ((pixel >> 5) & 0x3F) << 2;
        uint8_t b = (pixel & 0x1F) << 3;
        gray_buffer[i] = (uint8_t)((0.299 * r + 0.587 * g + 0.114 * b) + 0.5);
    }

    mp_obj_t gray_args[3] = {
        mp_obj_new_bytes(gray_buffer, width * height),
        mp_obj_new_int(width),
        mp_obj_new_int(height)
    };

    mp_obj_t result = qrdecode(3, gray_args);
    free(gray_buffer);
    return result;
}

static mp_obj_t qrdecode_wrapper(size_t n_args, const mp_obj_t *args) {
    return qrdecode(n_args, args);
}

static mp_obj_t qrdecode_rgb565_wrapper(size_t n_args, const mp_obj_t *args) {
    return qrdecode_rgb565(n_args, args);
}

static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(qrdecode_obj, 3, 3, qrdecode_wrapper);
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(qrdecode_rgb565_obj, 3, 3, qrdecode_rgb565_wrapper);

static const mp_rom_map_elem_t qrdecode_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_qrdecode) },
    { MP_ROM_QSTR(MP_QSTR_qrdecode), MP_ROM_PTR(&qrdecode_obj) },
    { MP_ROM_QSTR(MP_QSTR_qrdecode_rgb565), MP_ROM_PTR(&qrdecode_rgb565_obj) },
};

static MP_DEFINE_CONST_DICT(qrdecode_module_globals, qrdecode_module_globals_table);

const mp_obj_module_t qrdecode_module = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&qrdecode_module_globals,
};

MP_REGISTER_MODULE(MP_QSTR_qrdecode, qrdecode_module);
