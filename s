#!/bin/bash
clear

pkill eom
rm -rf /tmp/image.png

#./findgreendot.py sample/sunshine-light-1.avi $1
#./findgreendot.py sample/morning-blink-1.avi $1

# easy errors:
./findgreendot.py sample/sunshine-light-1.avi 9
#./findgreendot.py sample/afternoon-light-extra.avi $1

./q
sleep 0.2
