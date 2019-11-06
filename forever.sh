#!/bin/bash

cd /home/kiosk/amperachargingmonitor/
dir=/mnt/ram

while true
do
  
  mkdir -p $dir/result
  rm -rf $dir/tmp-*

  t=$dir/tmp-`date -Iseconds | cut -d+ -f1 `.txt
  f=$dir/result/`date -Iseconds | cut -d+ -f1 `.txt

  rm -rf $dir/capture.avi
  ffmpeg \
    -f v4l2 \
    -r 25 \
    -t 5 \
    -s 320x200 \
    -i /dev/video0 \
    $dir/capture.avi

  ./findgreendot.py $dir/capture.avi > $t

  if [ -s $t ] 
  then
    mv $t $f
  fi

  sleep 1

done
