#!/bin/bash

if [ `uname -s` = "Darwin" ]; then
	DIR="/media/b2/media/storage/data/garage/result/"
else # Linux
	DIR="/media/garage/mnt/ram/result/"
fi

./reportlastfiles.py \
	$DIR \
	`./detectdevice.sh` \
	1.4 \
	0
