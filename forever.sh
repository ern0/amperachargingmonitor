#!/bin/bash

t=/dev/shm/result-tmp.txt
while true
do
  mkdir -p /dev/shm/result
  f=/dev/shm/result/`date -Iseconds | cut -d+ -f1 `.txt
  /home/kiosk/amperachargingmonitor/runme.sh > $t
  if [ -s $f ]
  then
    mv $t $f
  fi
done
