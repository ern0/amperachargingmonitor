#!/bin/bash

if [ "`uname -s`" = "Darwin" ]; then
	pkill Sequential
	open /tmp/image.png
else
	/usr/local/bin/open 2>/dev/null /tmp/image.png
fi
