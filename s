#!/bin/bash
clear

#./findgreendot.py sample/morning-none-1.avi /tmp show_progress
./findgreendot.py sample/morning-blink-1.avi /tmp show_progress
open /tmp/image.png
