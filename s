#!/bin/bash
clear

rm -rf /tmp/image.png

./findgreendot.py sample/sunshine-light-1.avi $1
#./findgreendot.py sample/sunshine-blink-1.avi $1
#./findgreendot.py sample/dark-light-1.avi $1

open 2> /dev/null /tmp/image.png
sleep 0.2 
