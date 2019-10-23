#!/bin/bash
clear

pkill eom
rm -rf /tmp/image.png
./findgreendot.py test-sample/sunshine-blink-2.avi $1

./q
sleep 0.2
