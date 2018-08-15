#!/bin/bash
clear

trap reset SIGINT

make -j4
