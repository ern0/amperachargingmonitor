#!/bin/bash


# Capture a short video

rm -f /mnt/ram/capture.avi

ffmpeg \
	-f v4l2 \
	-r 25 \
	-t 5 \
	-s 320x200 \
	-i /dev/video0 \
	/mnt/ram/capture.avi


# Analyze the video and print result on stdout:
#  0 - nones
#  1 - light
#  2 - blink

./findgreendot.py /mnt/ram/capture.avi

# If you have no cam, you can try it with 
# sample videos in test-sample/