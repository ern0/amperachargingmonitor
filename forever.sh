#!/bin/bash

cd /home/kiosk/amperachargingmonitor/
dir=/mnt/ram

while true
do
  mkdir -p $dir/result
  rm -rf $dir/tmp-*
  t=$dir/tmp-`date -Iseconds | cut -d+ -f1 `.txt
  f=$dir/result/`date -Iseconds | cut -d+ -f1 `.txt
  ./runme.sh > $t
  if [ -s $t ]
  then
    mv $t $f
  fi
  sleep 1
done
