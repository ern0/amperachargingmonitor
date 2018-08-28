#!/bin/bash
clear

./findgreendot.py sample/sunshine-light-1.avi $1
#./findgreendot.py sample/sunshine-blink-1.avi $1
#./findgreendot.py sample/morning-none-1.avi $1
xdg-open 2> /dev/null /tmp/image.png
sleep 0.2 
