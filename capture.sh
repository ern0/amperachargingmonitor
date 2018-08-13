# capture
ffmpeg -f v4l2 -r 25 -t 5 -s 320x200 -i /dev/video0 /mnt/ram/capture.avi

# extract frame
ffmpeg -i sample/dark-blink.avi -vf select="eq(n\,5)" -vsync 0 frame.png

# count frames
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_frames -of default=nokey=1:noprint_wrappers=1 input.mp4
