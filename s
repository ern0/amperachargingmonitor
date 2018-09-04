#!/bin/bash
clear

rm -rf /tmp/image.png

#./findgreendot.py sample/dark-light-2.avi $1
./findgreendot.py sample/afternoon-light-extra.avi $1

./q
sleep 0.2
