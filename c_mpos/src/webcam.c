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

// Module name
#define MODULE_NAME "webcam"

// Default webcam device
#define VIDEO_DEVICE "/dev/video0"
#define WIDTH 240
#define HEIGHT 240

// Structure to hold webcam state
typedef struct {
    int fd; // File descriptor for the webcam
    void *buffer; // Memory-mapped buffer
    size_t buffer_length; // Length of the buffer
} webcam_t;

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

// Function to capture a grayscale image
static mp_obj_t webcam_capture_grayscale(void) {
    webcam_t cam = { .fd = -1, .buffer = NULL, .buffer_length = 0 };
    struct v4l2_format fmt = {0};
    struct v4l2_buffer buf = {0};
    struct v4l2_requestbuffers req = {0};

    // Open the webcam device
    cam.fd = open(VIDEO_DEVICE, O_RDWR);
    if (cam.fd < 0) {
        mp_raise_OSError(errno);
    }

    // Set format to YUYV
    fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    fmt.fmt.pix.width = WIDTH;
    fmt.fmt.pix.height = HEIGHT;
    fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_YUYV;
    fmt.fmt.pix.field = V4L2_FIELD_ANY;
    if (ioctl(cam.fd, VIDIOC_S_FMT, &fmt) < 0) {
        close(cam.fd);
        mp_raise_OSError(errno);
    }

    // Request one buffer
    req.count = 1;
    req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    req.memory = V4L2_MEMORY_MMAP;
    if (ioctl(cam.fd, VIDIOC_REQBUFS, &req) < 0) {
        close(cam.fd);
        mp_raise_OSError(errno);
    }

    // Query and map the buffer
    buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    buf.memory = V4L2_MEMORY_MMAP;
    buf.index = 0;
    if (ioctl(cam.fd, VIDIOC_QUERYBUF, &buf) < 0) {
        close(cam.fd);
        mp_raise_OSError(errno);
    }

    cam.buffer_length = buf.length;
    cam.buffer = mmap(NULL, buf.length, PROT_READ | PROT_WRITE, MAP_SHARED, cam.fd, buf.m.offset);
    if (cam.buffer == MAP_FAILED) {
        close(cam.fd);
        mp_raise_OSError(errno);
    }

    // Queue the buffer
    if (ioctl(cam.fd, VIDIOC_QBUF, &buf) < 0) {
        munmap(cam.buffer, cam.buffer_length);
        close(cam.fd);
        mp_raise_OSError(errno);
    }

    // Start streaming
    enum v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    if (ioctl(cam.fd, VIDIOC_STREAMON, &type) < 0) {
        munmap(cam.buffer, cam.buffer_length);
        close(cam.fd);
        mp_raise_OSError(errno);
    }

    // Dequeue the buffer (capture frame)
    if (ioctl(cam.fd, VIDIOC_DQBUF, &buf) < 0) {
        ioctl(cam.fd, VIDIOC_STREAMOFF, &type);
        munmap(cam.buffer, cam.buffer_length);
        close(cam.fd);
        mp_raise_OSError(errno);
    }

    // Convert YUYV to grayscale
    size_t grayscale_size = WIDTH * HEIGHT;
    uint8_t *grayscale_buf = (uint8_t *)malloc(grayscale_size);
    if (!grayscale_buf) {
        ioctl(cam.fd, VIDIOC_STREAMOFF, &type);
        munmap(cam.buffer, cam.buffer_length);
        close(cam.fd);
        mp_raise_OSError(ENOMEM);
    }
    yuyv_to_grayscale((uint8_t *)cam.buffer, grayscale_buf, WIDTH, HEIGHT);

    // Create MicroPython bytes object
    mp_obj_t result = mp_obj_new_bytes(grayscale_buf, grayscale_size);

    // Clean up
    free(grayscale_buf);
    ioctl(cam.fd, VIDIOC_STREAMOFF, &type);
    munmap(cam.buffer, cam.buffer_length);
    close(cam.fd);

    return result;
}
MP_DEFINE_CONST_FUN_OBJ_0(webcam_capture_grayscale_obj, webcam_capture_grayscale);

// Module definition
static const mp_rom_map_elem_t webcam_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_webcam) },
    { MP_ROM_QSTR(MP_QSTR_capture_grayscale), MP_ROM_PTR(&webcam_capture_grayscale_obj) },
};
static MP_DEFINE_CONST_DICT(webcam_module_globals, webcam_module_globals_table);

const mp_obj_module_t webcam_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&webcam_module_globals,
};

// Register the module
MP_REGISTER_MODULE(MP_QSTR_webcam, webcam_user_cmodule);

