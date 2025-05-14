#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/videodev2.h>
#include <sys/mman.h>
#include <string.h>
#include <errno.h>

#define WIDTH 640
#define HEIGHT 480
#define NUM_BUFFERS 4

// Global variables
int fd = -1;
struct v4l2_buffer buf;
void *buffers[NUM_BUFFERS];
size_t buffer_length;

// Convert YUYV to RGB for PPM output
void yuyv_to_rgb(unsigned char *yuyv, unsigned char *rgb, int width, int height) {
    for (int i = 0; i < width * height; i++) {
        int index = i * 2;
        int y = yuyv[index];
        int u = yuyv[index + 1];
        int v = yuyv[index + 3];

        int r = y + (1.402 * (v - 128));
        int g = y - (0.344 * (u - 128)) - (0.714 * (v - 128));
        int b = y + (1.772 * (u - 128));

        r = r < 0 ? 0 : (r > 255 ? 255 : r);
        g = g < 0 ? 0 : (g > 255 ? 255 : g);
        b = b < 0 ? 0 : (b > 255 ? 255 : b);

        rgb[i * 3 + 0] = r;
        rgb[i * 3 + 1] = g;
        rgb[i * 3 + 2] = b;
    }
}

// Save frame as PPM
void save_ppm(const char *filename, unsigned char *data, int width, int height) {
    FILE *fp = fopen(filename, "wb");
    if (!fp) {
        perror("Cannot open file");
        return;
    }
    fprintf(fp, "P6\n%d %d\n255\n", width, height);
    unsigned char *rgb = malloc(width * height * 3);
    yuyv_to_rgb(data, rgb, width, height);
    fwrite(rgb, 1, width * height * 3, fp);
    fclose(fp);
    free(rgb);
}

int init_webcam(const char *device) {
    // Open device
    fd = open(device, O_RDWR);
    if (fd < 0) {
        perror("Cannot open device");
        return -1;
    }

    // Set format
    struct v4l2_format fmt = {0};
    fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    fmt.fmt.pix.width = WIDTH;
    fmt.fmt.pix.height = HEIGHT;
    fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_YUYV;
    fmt.fmt.pix.field = V4L2_FIELD_ANY;
    if (ioctl(fd, VIDIOC_S_FMT, &fmt) < 0) {
        perror("Cannot set format");
        close(fd);
        return -1;
    }

    // Request buffers
    struct v4l2_requestbuffers req = {0};
    req.count = NUM_BUFFERS;
    req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    req.memory = V4L2_MEMORY_MMAP;
    if (ioctl(fd, VIDIOC_REQBUFS, &req) < 0) {
        perror("Cannot request buffers");
        close(fd);
        return -1;
    }

    // Map buffers
    for (int i = 0; i < NUM_BUFFERS; i++) {
        struct v4l2_buffer buf = {0};
        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf.memory = V4L2_MEMORY_MMAP;
        buf.index = i;
        if (ioctl(fd, VIDIOC_QUERYBUF, &buf) < 0) {
            perror("Cannot query buffer");
            close(fd);
            return -1;
        }
        buffer_length = buf.length;
        buffers[i] = mmap(NULL, buf.length, PROT_READ | PROT_WRITE, MAP_SHARED, fd, buf.m.offset);
        if (buffers[i] == MAP_FAILED) {
            perror("Cannot map buffer");
            close(fd);
            return -1;
        }
    }

    // Queue buffers
    for (int i = 0; i < NUM_BUFFERS; i++) {
        struct v4l2_buffer buf = {0};
        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf.memory = V4L2_MEMORY_MMAP;
        buf.index = i;
        if (ioctl(fd, VIDIOC_QBUF, &buf) < 0) {
            perror("Cannot queue buffer");
            return -1;
        }
    }

    // Start streaming
    enum v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    if (ioctl(fd, VIDIOC_STREAMON, &type) < 0) {
        perror("Cannot start streaming");
        return -1;
    }

    return 0;
}

void deinit_webcam() {
    if (fd < 0) return;

    // Stop streaming
    enum v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    ioctl(fd, VIDIOC_STREAMOFF, &type);

    // Unmap buffers
    for (int i = 0; i < NUM_BUFFERS; i++) {
        if (buffers[i] != MAP_FAILED) {
            munmap(buffers[i], buffer_length);
        }
    }

    // Close device
    close(fd);
    fd = -1;
}

int capture_frame(char *filename) {
    // Dequeue buffer
    struct v4l2_buffer buf = {0};
    buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    buf.memory = V4L2_MEMORY_MMAP;
    if (ioctl(fd, VIDIOC_DQBUF, &buf) < 0) {
        perror("Cannot dequeue buffer");
        return -1;
    }

    // Save frame
    save_ppm(filename, buffers[buf.index], WIDTH, HEIGHT);

    // Requeue buffer
    if (ioctl(fd, VIDIOC_QBUF, &buf) < 0) {
        perror("Cannot requeue buffer");
        return -1;
    }

    return 0;
}

int capture_frames(int n) {
    for (int i = 0; i < n; i++) {
        char filename[32];
        snprintf(filename, sizeof(filename), "frame_%03d.ppm", i);
        if (capture_frame(filename) < 0) {
            printf("Failed to capture frame %d\n", i);
            return -1;
        }
        printf("Captured frame %d to %s\n", i, filename);
    }
    return 0;
}

int main() {
    if (init_webcam("/dev/video0") < 0) {
        printf("Webcam initialization failed\n");
        return -1;
    }

    if (capture_frames(100) < 0) {
        printf("Frame capture failed\n");
        deinit_webcam();
        return -1;
    }

    deinit_webcam();
    printf("Webcam deinitialized\n");
    return 0;
}
