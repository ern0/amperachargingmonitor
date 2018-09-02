#!/bin/bash
clear

rm -rf /tmp/image.png

./findgreendot.py sample/morning-none-1.avi $1
#./findgreendot.py sample/sunshine-blink-1.avi 87
#./findgreendot.py sample/afternoon-light-extra.avi $1

./q
sleep 0.2
