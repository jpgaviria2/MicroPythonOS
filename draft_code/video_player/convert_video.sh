# https://sample-videos.com/

ffmpeg -i SampleVideo_640x360_1mb.mp4 -c:v mjpeg -q:v 7 -vf "fps=15,scale=320:180:flags=lanczos" -c:a pcm_u8 video_320x180.avi
