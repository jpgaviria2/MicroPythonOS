#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/videodev2.h>
#include <sys/mman.h>
#include <string.h>
#include <errno.h>
#include "py/obj.h"
#include "py/runtime.h"
#include "py/mperrno.h"

#define WIDTH 640
#define HEIGHT 480
#define NUM_BUFFERS 4
#define OUTPUT_WIDTH 240
#define OUTPUT_HEIGHT 240

// Forward declaration of the webcam type
static const mp_obj_type_t webcam_type;

typedef struct _webcam_obj_t {
    mp_obj_base_t base;
    int fd;
    void *buffers[NUM_BUFFERS];
    size_t buffer_length;
    int frame_count;
    unsigned char *gray_buffer; // Persistent buffer for memoryview
} webcam_obj_t;

static void yuyv_to_grayscale_240x240(unsigned char *yuyv, unsigned char *gray, int in_width, int in_height) {
    float x_ratio = (float)in_width / OUTPUT_WIDTH;
    float y_ratio = (float)in_height / OUTPUT_HEIGHT;

    for (int y = 0; y < OUTPUT_HEIGHT; y++) {
        for (int x = 0; x < OUTPUT_WIDTH; x++) {
            int src_x = (int)(x * x_ratio);
            int src_y = (int)(y * y_ratio);
            int src_index = (src_y * in_width + src_x) * 2;
            gray[y * OUTPUT_WIDTH + x] = yuyv[src_index];
        }
    }
}

static void save_raw(const char *filename, unsigned char *data, int width, int height) {
    FILE *fp = fopen(filename, "wb");
    if (!fp) {
        fprintf(stderr, "Cannot open file %s: %s\n", filename, strerror(errno));
        return;
    }
    fwrite(data, 1, width * height, fp);
    fclose(fp);
}

static int init_webcam(webcam_obj_t *self, const char *device) {
    self->fd = open(device, O_RDWR);
    if (self->fd < 0) {
        fprintf(stderr, "Cannot open device: %s\n", strerror(errno));
        return -1;
    }

    struct v4l2_format fmt = {0};
    fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    fmt.fmt.pix.width = WIDTH;
    fmt.fmt.pix.height = HEIGHT;
    fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_YUYV;
    fmt.fmt.pix.field = V4L2_FIELD_ANY;
    if (ioctl(self->fd, VIDIOC_S_FMT, &fmt) < 0) {
        fprintf(stderr, "Cannot set format: %s\n", strerror(errno));
        close(self->fd);
        return -1;
    }

    struct v4l2_requestbuffers req = {0};
    req.count = NUM_BUFFERS;
    req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    req.memory = V4L2_MEMORY_MMAP;
    if (ioctl(self->fd, VIDIOC_REQBUFS, &req) < 0) {
        fprintf(stderr, "Cannot request buffers: %s\n", strerror(errno));
        close(self->fd);
        return -1;
    }

    for (int i = 0; i < NUM_BUFFERS; i++) {
        struct v4l2_buffer buf = {0};
        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf.memory = V4L2_MEMORY_MMAP;
        buf.index = i;
        if (ioctl(self->fd, VIDIOC_QUERYBUF, &buf) < 0) {
            fprintf(stderr, "Cannot query buffer: %s\n", strerror(errno));
            close(self->fd);
            return -1;
        }
        self->buffer_length = buf.length;
        self->buffers[i] = mmap(NULL, buf.length, PROT_READ | PROT_WRITE, MAP_SHARED, self->fd, buf.m.offset);
        if (self->buffers[i] == MAP_FAILED) {
            fprintf(stderr, "Cannot map buffer: %s\n", strerror(errno));
            close(self->fd);
            return -1;
        }
    }

    for (int i = 0; i < NUM_BUFFERS; i++) {
        struct v4l2_buffer buf = {0};
        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf.memory = V4L2_MEMORY_MMAP;
        buf.index = i;
        if (ioctl(self->fd, VIDIOC_QBUF, &buf) < 0) {
        fprintf(stderr, "Cannot queue buffer: %s\n", strerror(errno));
            return -1;
        }
    }

    enum v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    if (ioctl(self->fd, VIDIOC_STREAMON, &type) < 0) {
        fprintf(stderr, "Cannot start streaming: %s\n", strerror(errno));
        return -1;
    }

    self->frame_count = 0;
    self->gray_buffer = (unsigned char *)malloc(OUTPUT_WIDTH * OUTPUT_HEIGHT);
    if (!self->gray_buffer) {
        fprintf(stderr, "Cannot allocate gray buffer: %s\n", strerror(errno));
        close(self->fd);
        return -1;
    }
    return 0;
}

static void deinit_webcam(webcam_obj_t *self) {
    if (self->fd < 0) return;

    enum v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    ioctl(self->fd, VIDIOC_STREAMOFF, &type);

    for (int i = 0; i < NUM_BUFFERS; i++) {
        if (self->buffers[i] != MAP_FAILED) {
            munmap(self->buffers[i], self->buffer_length);
        }
    }

    if (self->gray_buffer) {
        free(self->gray_buffer);
        self->gray_buffer = NULL;
    }

    close(self->fd);
    self->fd = -1;
}

static mp_obj_t capture_frame(webcam_obj_t *self) {
    struct v4l2_buffer buf = {0};
    buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    buf.memory = V4L2_MEMORY_MMAP;
    if (ioctl(self->fd, VIDIOC_DQBUF, &buf) < 0) {
        mp_raise_OSError(MP_EIO);
    }

    if (!self->gray_buffer) {
        mp_raise_OSError(MP_ENOMEM);
    }

    yuyv_to_grayscale_240x240(self->buffers[buf.index], self->gray_buffer, WIDTH, HEIGHT);

    //char filename[32];
    //snprintf(filename, sizeof(filename), "frame_%03d.raw", self->frame_count++);
    //save_raw(filename, self->gray_buffer, OUTPUT_WIDTH, OUTPUT_HEIGHT);

    mp_obj_t result = mp_obj_new_memoryview(0x01, OUTPUT_WIDTH * OUTPUT_HEIGHT, self->gray_buffer);

    if (ioctl(self->fd, VIDIOC_QBUF, &buf) < 0) {
        mp_raise_OSError(MP_EIO);
    }

    return result;
}

static mp_obj_t webcam_init(size_t n_args, const mp_obj_t *args) {
    mp_arg_check_num(n_args, 0, 0, 1, false);
    const char *device = "/dev/video0"; // Default device
    if (n_args == 1) {
        device = mp_obj_str_get_str(args[0]);
    }

    webcam_obj_t *self = m_new_obj(webcam_obj_t);
    self->base.type = &webcam_type;
    self->fd = -1;
    self->gray_buffer = NULL;

    if (init_webcam(self, device) < 0) {
        mp_raise_OSError(MP_EIO);
    }

    return MP_OBJ_FROM_PTR(self);
}
MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(webcam_init_obj, 0, 1, webcam_init);

static mp_obj_t webcam_deinit(mp_obj_t self_in) {
    webcam_obj_t *self = MP_OBJ_TO_PTR(self_in);
    deinit_webcam(self);
    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_1(webcam_deinit_obj, webcam_deinit);

static mp_obj_t webcam_capture_frame(mp_obj_t self_in) {
    webcam_obj_t *self = MP_OBJ_TO_PTR(self_in);
    if (self->fd < 0) {
        mp_raise_OSError(MP_EIO);
    }
    return capture_frame(self);
}
MP_DEFINE_CONST_FUN_OBJ_1(webcam_capture_frame_obj, webcam_capture_frame);

static const mp_obj_type_t webcam_type = {
    { &mp_type_type },
    .name = MP_QSTR_Webcam,
};

static const mp_rom_map_elem_t mp_module_webcam_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_webcam) },
    { MP_ROM_QSTR(MP_QSTR_Webcam), MP_ROM_PTR(&webcam_type) },
    { MP_ROM_QSTR(MP_QSTR_init), MP_ROM_PTR(&webcam_init_obj) },
    { MP_ROM_QSTR(MP_QSTR_capture_frame), MP_ROM_PTR(&webcam_capture_frame_obj) },
    { MP_ROM_QSTR(MP_QSTR_deinit), MP_ROM_PTR(&webcam_deinit_obj) },
};
static MP_DEFINE_CONST_DICT(mp_module_webcam_globals, mp_module_webcam_globals_table);

const mp_obj_module_t webcam_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&mp_module_webcam_globals,
};

MP_REGISTER_MODULE(MP_QSTR_webcam, webcam_user_cmodule);
