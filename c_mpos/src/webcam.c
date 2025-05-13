#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/videodev2.h>
#include <sys/mman.h>
#include <string.h>

#include "py/obj.h"
#include "py/runtime.h"
#include "py/mperrno.h"

// Debug print macro
#define WEBCAM_DEBUG_PRINT(...) mp_printf(&mp_plat_print, __VA_ARGS__)

// Module name
#define MODULE_NAME "webcam"

// Default webcam device
#define VIDEO_DEVICE "/dev/video0"
#define CAPTURE_WIDTH 640  // Capture at 640x480
#define CAPTURE_HEIGHT 480
#define OUTPUT_WIDTH 240   // Resize to 240x240
#define OUTPUT_HEIGHT 240

// Webcam object type
typedef struct _webcam_obj_t {
    mp_obj_base_t base;
    int fd; // File descriptor for the webcam
    void *buffer; // Memory-mapped buffer
    size_t buffer_length; // Length of the buffer
    bool streaming; // Streaming state
} webcam_obj_t;

// Forward declaration of the webcam type
static const mp_obj_type_t webcam_type;

// Convert YUYV to grayscale (extract Y component)
static void yuyv_to_grayscale(uint8_t *src, uint8_t *dst, size_t width, size_t height) {
    for (size_t i = 0; i < width * height * 2; i += 2) {
        dst[i / 2] = src[i]; // Y component is every other byte
    }
}

// Resize 640x480 grayscale to 240x240
static void resize_640x480_to_240x240(uint8_t *src, uint8_t *dst) {
    const int src_width = 640;
    const int src_height = 480;
    const int dst_width = 240;
    const int dst_height = 240;

    // Scaling factors
    float x_ratio = (float)src_width / dst_width;
    float y_ratio = (float)src_height / dst_height;

    for (int y = 0; y < dst_height; y++) {
        for (int x = 0; x < dst_width; x++) {
            // Nearest-neighbor interpolation
            int src_x = (int)(x * x_ratio);
            int src_y = (int)(y * y_ratio);
            dst[y * dst_width + x] = src[src_y * src_width + src_x];
        }
    }
}

// Initialize the webcam
static mp_obj_t webcam_init(void) {
    webcam_obj_t *self = m_new_obj(webcam_obj_t);
    self->base.type = &webcam_type;
    self->fd = -1;
    self->buffer = NULL;
    self->buffer_length = 0;
    self->streaming = false;

    // Open the webcam device
    self->fd = open(VIDEO_DEVICE, O_RDWR);
    if (self->fd < 0) {
        WEBCAM_DEBUG_PRINT("webcam: Failed to open device %s\n", VIDEO_DEVICE);
        mp_raise_OSError(errno);
    }

    // Set format to YUYV at 640x480
    struct v4l2_format fmt = {0};
    fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    fmt.fmt.pix.width = CAPTURE_WIDTH;
    fmt.fmt.pix.height = CAPTURE_HEIGHT;
    fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_YUYV;
    fmt.fmt.pix.field = V4L2_FIELD_ANY;
    if (ioctl(self->fd, VIDIOC_S_FMT, &fmt) < 0) {
        WEBCAM_DEBUG_PRINT("webcam: Failed to set YUYV format at %dx%d\n", CAPTURE_WIDTH, CAPTURE_HEIGHT);
        close(self->fd);
        mp_raise_OSError(errno);
    }

    // Request one buffer
    struct v4l2_requestbuffers req = {0};
    req.count = 1;
    req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    req.memory = V4L2_MEMORY_MMAP;
    if (ioctl(self->fd, VIDIOC_REQBUFS, &req) < 0) {
        WEBCAM_DEBUG_PRINT("webcam: Failed to request memory-mapped buffer\n");
        close(self->fd);
        mp_raise_OSError(errno);
    }

    // Query and map the buffer
    struct v4l2_buffer buf = {0};
    buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    buf.memory = V4L2_MEMORY_MMAP;
    buf.index = 0;
    if (ioctl(self->fd, VIDIOC_QUERYBUF, &buf) < 0) {
        WEBCAM_DEBUG_PRINT("webcam: Failed to query buffer properties\n");
        close(self->fd);
        mp_raise_OSError(errno);
    }

    self->buffer_length = buf.length;
    self->buffer = mmap(NULL, buf.length, PROT_READ | PROT_WRITE, MAP_SHARED, self->fd, buf.m.offset);
    if (self->buffer == MAP_FAILED) {
        WEBCAM_DEBUG_PRINT("webcam: Failed to map buffer memory\n");
        close(self->fd);
        mp_raise_OSError(errno);
    }

    return MP_OBJ_FROM_PTR(self);
}
MP_DEFINE_CONST_FUN_OBJ_0(webcam_init_obj, webcam_init);

// Capture a grayscale image
static mp_obj_t webcam_capture_grayscale(mp_obj_t self_in) {
    webcam_obj_t *self = MP_OBJ_TO_PTR(self_in);

    // Queue the buffer
    struct v4l2_buffer buf = {0};
    buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    buf.memory = V4L2_MEMORY_MMAP;
    buf.index = 0;
    if (ioctl(self->fd, VIDIOC_QBUF, &buf) < 0) {
        WEBCAM_DEBUG_PRINT("webcam: Failed to queue buffer for capture\n");
        mp_raise_OSError(errno);
    }

    // Start streaming if not already started
    if (!self->streaming) {
        enum v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        if (ioctl(self->fd, VIDIOC_STREAMON, &type) < 0) {
            WEBCAM_DEBUG_PRINT("webcam: Failed to start video streaming\n");
            mp_raise_OSError(errno);
        }
        self->streaming = true;
    }

    // Dequeue the buffer (capture frame)
    if (ioctl(self->fd, VIDIOC_DQBUF, &buf) < 0) {
        WEBCAM_DEBUG_PRINT("webcam: Failed to dequeue captured frame\n");
        mp_raise_OSError(errno);
    }

    // Convert YUYV to grayscale (640x480)
    size_t capture_size = CAPTURE_WIDTH * CAPTURE_HEIGHT;
    uint8_t *grayscale_buf = (uint8_t *)malloc(capture_size);
    if (!grayscale_buf) {
        WEBCAM_DEBUG_PRINT("webcam: Failed to allocate memory for grayscale buffer (%zu bytes)\n", capture_size);
        mp_raise_OSError(ENOMEM);
    }
    yuyv_to_grayscale((uint8_t *)self->buffer, grayscale_buf, CAPTURE_WIDTH, CAPTURE_HEIGHT);

    // Resize to 240x240
    size_t output_size = OUTPUT_WIDTH * OUTPUT_HEIGHT;
    uint8_t *resized_buf = (uint8_t *)malloc(output_size);
    if (!resized_buf) {
        WEBCAM_DEBUG_PRINT("webcam: Failed to allocate memory for resized buffer (%zu bytes)\n", output_size);
        free(grayscale_buf);
        mp_raise_OSError(ENOMEM);
    }
    resize_640x480_to_240x240(grayscale_buf, resized_buf);
    free(grayscale_buf); // Free the 640x480 buffer

    // Create MicroPython bytes object
    mp_obj_t result = mp_obj_new_bytes(resized_buf, output_size);

    // Clean up
    free(resized_buf);

    // Re-queue the buffer for the next capture
    if (ioctl(self->fd, VIDIOC_QBUF, &buf) < 0) {
        WEBCAM_DEBUG_PRINT("webcam: Failed to re-queue buffer after capture\n");
        mp_raise_OSError(errno);
    }

    return result;
}
MP_DEFINE_CONST_FUN_OBJ_1(webcam_capture_grayscale_obj, webcam_capture_grayscale);

// Deinitialize the webcam
static mp_obj_t webcam_deinit(mp_obj_t self_in) {
    webcam_obj_t *self = MP_OBJ_TO_PTR(self_in);

    // Stop streaming if active
    if (self->streaming) {
        enum v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        if (ioctl(self->fd, VIDIOC_STREAMOFF, &type) < 0) {
            WEBCAM_DEBUG_PRINT("webcam: Failed to stop video streaming\n");
            mp_raise_OSError(errno);
        }
        self->streaming = false;
    }

    // Unmap buffer
    if (self->buffer != NULL && self->buffer != MAP_FAILED) {
        munmap(self->buffer, self->buffer_length);
        self->buffer = NULL;
        self->buffer_length = 0;
    }

    // Close device
    if (self->fd >= 0) {
        close(self->fd);
        self->fd = -1;
    }

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_1(webcam_deinit_obj, webcam_deinit);

// Method dispatch for webcam object
static mp_obj_t webcam_call(mp_obj_t self_in, mp_obj_t attr, mp_obj_t *dest) {
    if (dest[0] == MP_OBJ_NULL) {
        // Lookup attribute
        if (attr == MP_QSTR_capture_grayscale) {
            dest[0] = MP_OBJ_FROM_PTR(&webcam_capture_grayscale_obj);
            dest[1] = self_in;
        } else if (attr == MP_QSTR_deinit) {
            dest[0] = MP_OBJ_FROM_PTR(&webcam_deinit_obj);
            dest[1] = self_in;
        }
    }
    return MP_OBJ_NULL;
}

// Webcam type definition
static const mp_obj_type_t webcam_type = {
    { &mp_type_type },
    .name = MP_QSTR_webcam,
    .call = webcam_call,
};

// Module definition
static const mp_rom_map_elem_t webcam_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_webcam) },
    { MP_ROM_QSTR(MP_QSTR_init), MP_ROM_PTR(&webcam_init_obj) },
};
static MP_DEFINE_CONST_DICT(webcam_module_globals, webcam_module_globals_table);

const mp_obj_module_t webcam_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&webcam_module_globals,
};

// Register the module
MP_REGISTER_MODULE(MP_QSTR_webcam, webcam_user_cmodule);
