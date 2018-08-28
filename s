#!/bin/bash
clear

./findgreendot.py sample/sunshine-blink-1.avi $1
xdg-open 2> /dev/null /tmp/image.png
sleep 0.2 
