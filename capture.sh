rm -f /mnt/ram/capture.avi ; ffmpeg -f v4l2 -r 25 -t 5 -s 320x200 -i /dev/video0 /mnt/ram/capture.avi
