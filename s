#!/bin/bash
clear

rm -rf /tmp/image.png

#./findgreendot.py sample/sunshine-blink-1.avi 87
#./findgreendot.py sample/sunshine-blink-1.avi $1
./findgreendot.py sample/afternoon-light-extra.avi 120

if [ "`uname -s`" = "Darwin" ]; then
	pkill Sequential
	open /tmp/image.png
else
	/usr/local/bin/open 2>/dev/null /tmp/image.png
fi

sleep 0.2
