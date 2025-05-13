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
#define NUM_BUFFERS 3      // Use 5 buffers, as it achieved 5 captures
#define QUEUE_RETRIES 3    // Number of retry attempts for queueing
#define QUEUE_RETRY_DELAY_US 100000  // 100ms delay between retries

// Webcam object type
typedef struct _webcam_obj_t {
    mp_obj_base_t base;
    int fd; // File descriptor for the webcam
    struct {
        void *start; // Memory-mapped buffer
        size_t length; // Buffer length
    } buffers[NUM_BUFFERS]; // Array of buffers
    size_t num_buffers; // Number of allocated buffers
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

// Reset streaming state
static void webcam_reset_streaming(webcam_obj_t *self) {
    if (self->streaming) {
        enum v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        WEBCAM_DEBUG_PRINT("webcam: Stopping video streaming for reset\n");
        if (ioctl(self->fd, VIDIOC_STREAMOFF, &type) < 0) {
            WEBCAM_DEBUG_PRINT("webcam: Failed to stop video streaming (errno=%d)\n", errno);
        }
        self->streaming = false;
    }

    // Re-queue all buffers
    for (size_t i = 0; i < self->num_buffers; i++) {
        struct v4l2_buffer buf = {0};
        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf.memory = V4L2_MEMORY_MMAP;
        buf.index = i;

        // Query buffer state
        WEBCAM_DEBUG_PRINT("webcam: Querying buffer state during reset (index=%zu)\n", i);
        if (ioctl(self->fd, VIDIOC_QUERYBUF, &buf) < 0) {
            WEBCAM_DEBUG_PRINT("webcam: Failed to query buffer state (index=%zu, errno=%d)\n", i, errno);
            continue;
        }

        // Queue buffer
        WEBCAM_DEBUG_PRINT("webcam: Re-queuing buffer during reset (index=%zu)\n", i);
        if (ioctl(self->fd, VIDIOC_QBUF, &buf) < 0) {
            WEBCAM_DEBUG_PRINT("webcam: Failed to re-queue buffer during reset (index=%zu, errno=%d)\n", i, errno);
        }
    }

    // Restart streaming
    enum v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    WEBCAM_DEBUG_PRINT("webcam: Restarting video streaming\n");
    if (ioctl(self->fd, VIDIOC_STREAMON, &type) < 0) {
        WEBCAM_DEBUG_PRINT("webcam: Failed to restart video streaming (errno=%d)\n", errno);
    } else {
        self->streaming = true;
    }
}

// Capture a grayscale image
static mp_obj_t webcam_capture_grayscale(mp_obj_t self_in) {
    webcam_obj_t *self = MP_OBJ_TO_PTR(self_in);

    // Try to queue a buffer with retries
    struct v4l2_buffer buf = {0};
    bool queued = false;
    for (int attempt = 0; attempt < QUEUE_RETRIES && !queued; attempt++) {
        for (size_t i = 0; i < self->num_buffers; i++) {
            memset(&buf, 0, sizeof(buf));
            buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
            buf.memory = V4L2_MEMORY_MMAP;
            buf.index = i;

            // Query buffer state
            WEBCAM_DEBUG_PRINT("webcam: Querying buffer state (index=%zu, attempt=%d)\n", i, attempt + 1);
            if (ioctl(self->fd, VIDIOC_QUERYBUF, &buf) < 0) {
                WEBCAM_DEBUG_PRINT("webcam: Failed to query buffer state (index=%zu, errno=%d)\n", i, errno);
                continue;
            }

            WEBCAM_DEBUG_PRINT("webcam: Attempting to queue buffer (index=%zu, attempt=%d)\n", i, attempt + 1);
            if (ioctl(self->fd, VIDIOC_QBUF, &buf) == 0) {
                WEBCAM_DEBUG_PRINT("webcam: Successfully queued buffer (index=%zu)\n", i);
                queued = true;
                break;
            }
            WEBCAM_DEBUG_PRINT("webcam: Failed to queue buffer (index=%zu, errno=%d)\n", i, errno);
        }
        if (!queued && attempt < QUEUE_RETRIES - 1) {
            WEBCAM_DEBUG_PRINT("webcam: No buffers available, retrying after delay\n");
            usleep(QUEUE_RETRY_DELAY_US); // Wait 100ms
        }
    }

    if (!queued) {
        WEBCAM_DEBUG_PRINT("webcam: No buffers available after %d retries, resetting streaming\n", QUEUE_RETRIES);
        webcam_reset_streaming(self);
        // Retry queuing one more time after reset
        for (size_t i = 0; i < self->num_buffers; i++) {
            memset(&buf, 0, sizeof(buf));
            buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
            buf.memory = V4L2_MEMORY_MMAP;
            buf.index = i;

            WEBCAM_DEBUG_PRINT("webcam: Querying buffer state after reset (index=%zu)\n", i);
            if (ioctl(self->fd, VIDIOC_QUERYBUF, &buf) < 0) {
                WEBCAM_DEBUG_PRINT("webcam: Failed to query buffer state after reset (index=%zu, errno=%d)\n", i, errno);
                continue;
            }

            WEBCAM_DEBUG_PRINT("webcam: Attempting to queue buffer after reset (index=%zu)\n", i);
            if (ioctl(self->fd, VIDIOC_QBUF, &buf) == 0) {
                WEBCAM_DEBUG_PRINT("webcam: Successfully queued buffer after reset (index=%zu)\n", i);
                queued = true;
                break;
            }
            WEBCAM_DEBUG_PRINT("webcam: Failed to queue buffer after reset (index=%zu, errno=%d)\n", i, errno);
        }
    }

    if (!queued) {
        WEBCAM_DEBUG_PRINT("webcam: No buffers available even after reset\n");
        mp_raise_OSError(EAGAIN);
    }

    // Start streaming if not already started
    if (!self->streaming) {
        enum v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        WEBCAM_DEBUG_PRINT("webcam: Starting video streaming\n");
        if (ioctl(self->fd, VIDIOC_STREAMON, &type) < 0) {
            WEBCAM_DEBUG_PRINT("webcam: Failed to start video streaming (errno=%d)\n", errno);
            mp_raise_OSError(errno);
        }
        self->streaming = true;
    }

    // Dequeue a buffer (capture frame)
    memset(&buf, 0, sizeof(buf));
    buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    buf.memory = V4L2_MEMORY_MMAP;
    WEBCAM_DEBUG_PRINT("webcam: Dequeuing buffer\n");
    if (ioctl(self->fd, VIDIOC_DQBUF, &buf) < 0) {
        WEBCAM_DEBUG_PRINT("webcam: Failed to dequeue captured frame (errno=%d)\n", errno);
        mp_raise_OSError(errno);
    }
    size_t buf_index = buf.index;

    // Convert YUYV to grayscale (640x480)
    size_t capture_size = CAPTURE_WIDTH * CAPTURE_HEIGHT;
    uint8_t *grayscale_buf = (uint8_t *)malloc(capture_size);
    if (!grayscale_buf) {
        WEBCAM_DEBUG_PRINT("webcam: Failed to allocate memory for grayscale buffer (%zu bytes)\n", capture_size);
        mp_raise_OSError(ENOMEM);
    }
    yuyv_to_grayscale((uint8_t *)self->buffers[buf_index].start, grayscale_buf, CAPTURE_WIDTH, CAPTURE_HEIGHT);

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

    // Re-queue the buffer
    memset(&buf, 0, sizeof(buf));
    buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    buf.memory = V4L2_MEMORY_MMAP;
    buf.index = buf_index;
    WEBCAM_DEBUG_PRINT("webcam: Querying buffer state before re-queue (index=%zu)\n", buf_index);
    if (ioctl(self->fd, VIDIOC_QUERYBUF, &buf) < 0) {
        WEBCAM_DEBUG_PRINT("webcam: Failed to query buffer state before re-queue (index=%zu, errno=%d)\n", buf_index, errno);
    }
    WEBCAM_DEBUG_PRINT("webcam: Re-queuing buffer (index=%zu)\n", buf_index);
    if (ioctl(self->fd, VIDIOC_QBUF, &buf) < 0) {
        WEBCAM_DEBUG_PRINT("webcam: Failed to re-queue buffer (index=%zu, errno=%d)\n", buf_index, errno);
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
        WEBCAM_DEBUG_PRINT("webcam: Stopping video streaming\n");
        if (ioctl(self->fd, VIDIOC_STREAMOFF, &type) < 0) {
            WEBCAM_DEBUG_PRINT("webcam: Failed to stop video streaming (errno=%d)\n", errno);
            mp_raise_OSError(errno);
        }
        self->streaming = false;
    }

    // Unmap buffers
    for (size_t i = 0; i < self->num_buffers; i++) {
        if (self->buffers[i].start != NULL && self->buffers[i].start != MAP_FAILED) {
            WEBCAM_DEBUG_PRINT("webcam: Unmapping buffer %zu\n", i);
            munmap(self->buffers[i].start, self->buffers[i].length);
            self->buffers[i].start = NULL;
            self->buffers[i].length = 0;
        }
    }
    self->num_buffers = 0;

    // Close device
    if (self->fd >= 0) {
        WEBCAM_DEBUG_PRINT("webcam: Closing device\n");
        close(self->fd);
        self->fd = -1;
    }

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_1(webcam_deinit_obj, webcam_deinit);

// Initialize the webcam and return a tuple with the object and methods
static mp_obj_t webcam_init(void) {
    webcam_obj_t *self = m_new_obj(webcam_obj_t);
    self->base.type = &webcam_type;
    self->fd = -1;
    self->num_buffers = 0;
    self->streaming = false;
    for (size_t i = 0; i < NUM_BUFFERS; i++) {
        self->buffers[i].start = NULL;
        self->buffers[i].length = 0;
    }

    // Open the webcam device
    WEBCAM_DEBUG_PRINT("webcam: Opening device %s\n", VIDEO_DEVICE);
    self->fd = open(VIDEO_DEVICE, O_RDWR);
    if (self->fd < 0) {
        WEBCAM_DEBUG_PRINT("webcam: Failed to open device %s (errno=%d)\n", VIDEO_DEVICE, errno);
        mp_raise_OSError(errno);
    }

    // Set format to YUYV at 640x480
    struct v4l2_format fmt = {0};
    fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    fmt.fmt.pix.width = CAPTURE_WIDTH;
    fmt.fmt.pix.height = CAPTURE_HEIGHT;
    fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_YUYV;
    fmt.fmt.pix.field = V4L2_FIELD_ANY;
    WEBCAM_DEBUG_PRINT("webcam: Setting format to YUYV %dx%d\n", CAPTURE_WIDTH, CAPTURE_HEIGHT);
    if (ioctl(self->fd, VIDIOC_S_FMT, &fmt) < 0) {
        WEBCAM_DEBUG_PRINT("webcam: Failed to set YUYV format at %dx%d (errno=%d)\n", CAPTURE_WIDTH, CAPTURE_HEIGHT, errno);
        close(self->fd);
        mp_raise_OSError(errno);
    }

    // Request buffers
    struct v4l2_requestbuffers req = {0};
    req.count = NUM_BUFFERS;
    req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    req.memory = V4L2_MEMORY_MMAP;
    WEBCAM_DEBUG_PRINT("webcam: Requesting %d memory-mapped buffers\n", NUM_BUFFERS);
    if (ioctl(self->fd, VIDIOC_REQBUFS, &req) < 0) {
        WEBCAM_DEBUG_PRINT("webcam: Failed to request memory-mapped buffers (errno=%d)\n", errno);
        close(self->fd);
        mp_raise_OSError(errno);
    }
    self->num_buffers = req.count;
    if (self->num_buffers < NUM_BUFFERS) {
        WEBCAM_DEBUG_PRINT("webcam: Insufficient buffers allocated (%zu)\n", self->num_buffers);
        close(self->fd);
        mp_raise_OSError(ENOMEM);
    }

    // Query and map buffers
    for (size_t i = 0; i < self->num_buffers; i++) {
        struct v4l2_buffer buf = {0};
        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf.memory = V4L2_MEMORY_MMAP;
        buf.index = i;
        WEBCAM_DEBUG_PRINT("webcam: Querying buffer %zu properties\n", i);
        if (ioctl(self->fd, VIDIOC_QUERYBUF, &buf) < 0) {
            WEBCAM_DEBUG_PRINT("webcam: Failed to query buffer %zu properties (errno=%d)\n", i, errno);
            for (size_t j = 0; j < i; j++) {
                if (self->buffers[j].start != NULL) {
                    munmap(self->buffers[j].start, self->buffers[j].length);
                }
            }
            close(self->fd);
            mp_raise_OSError(errno);
        }

        self->buffers[i].length = buf.length;
        WEBCAM_DEBUG_PRINT("webcam: Mapping buffer %zu of length %zu\n", i, buf.length);
        self->buffers[i].start = mmap(NULL, buf.length, PROT_READ | PROT_WRITE, MAP_SHARED, self->fd, buf.m.offset);
        if (self->buffers[i].start == MAP_FAILED) {
            WEBCAM_DEBUG_PRINT("webcam: Failed to map buffer %zu memory (errno=%d)\n", i, errno);
            for (size_t j = 0; j < i; j++) {
                if (self->buffers[j].start != NULL) {
                    munmap(self->buffers[j].start, self->buffers[j].length);
                }
            }
            close(self->fd);
            mp_raise_OSError(errno);
        }

        // Queue buffer upfront
        memset(&buf, 0, sizeof(buf));
        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf.memory = V4L2_MEMORY_MMAP;
        buf.index = i;
        WEBCAM_DEBUG_PRINT("webcam: Initial queuing of buffer %zu\n", i);
        if (ioctl(self->fd, VIDIOC_QBUF, &buf) < 0) {
            WEBCAM_DEBUG_PRINT("webcam: Failed to queue buffer %zu initially (errno=%d)\n", i, errno);
            for (size_t j = 0; j <= i; j++) {
                if (self->buffers[j].start != NULL) {
                    munmap(self->buffers[j].start, self->buffers[j].length);
                }
            }
            close(self->fd);
            mp_raise_OSError(errno);
        }
    }

    return mp_obj_new_tuple(3, (mp_obj_t[]){MP_OBJ_FROM_PTR(self), MP_OBJ_FROM_PTR(&webcam_capture_grayscale_obj), MP_OBJ_FROM_PTR(&webcam_deinit_obj)});
}
MP_DEFINE_CONST_FUN_OBJ_0(webcam_init_obj, webcam_init);

// Module definition
static const mp_rom_map_elem_t webcam_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_webcam) },
    { MP_ROM_QSTR(MP_QSTR_init), MP_ROM_PTR(&webcam_init_obj) },
    { MP_ROM_QSTR(MP_QSTR_capture_grayscale), MP_ROM_PTR(&webcam_capture_grayscale_obj) },
    { MP_ROM_QSTR(MP_QSTR_deinit), MP_ROM_PTR(&webcam_deinit_obj) },
};



static MP_DEFINE_CONST_DICT(webcam_module_globals, webcam_module_globals_table);

// Webcam type definition
static const mp_obj_type_t webcam_type = {
    { &mp_type_type },
    .name = MP_QSTR_webcam,
};

const mp_obj_module_t webcam_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&webcam_module_globals,
};

// Register the module
MP_REGISTER_MODULE(MP_QSTR_webcam, webcam_user_cmodule);
