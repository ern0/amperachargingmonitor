#!/bin/bash
clear

rm -rf /tmp/image.png

./findgreendot.py sample/morning-blink-2.avi $1
#./findgreendot.py sample/sunshine-blink-1.avi $1
#./findgreendot.py sample/sunshine-light-1.avi $1

if [ "`uname -s`" = "Darwin" ]; then
	open /tmp/image.png
else
	/usr/local/bin/open 2>/dev/null /tmp/image.png
fi

sleep 0.2 
