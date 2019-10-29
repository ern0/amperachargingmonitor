#!/bin/bash

dir=/mnt/ram

# Capture a short video

rm -f $dir/capture.avi

ffmpeg \
        -f v4l2 \
        -r 25 \
        -t 0.2 \
        -s 320x200 \
        -i /dev/video0 \
        $dir/capture.avi

# Analyze the video and print result on stdout:
#  0 - none
#  1 - light
#  2 - blink

./findgreendot.py $dir/capture.avi

# If you have no cam, you can try it with 
# sample videos in test-sample/
