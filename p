#!/bin/bash
clear

trap reset SIGINT

make -j4
reset
cat final.txt
