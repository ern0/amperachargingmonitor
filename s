#!/bin/bash
clear

rm -rf /tmp/image.png

./findgreendot.py sample/dark-light-2.avi $1

./q
sleep 0.2
