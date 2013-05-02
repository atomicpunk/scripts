#!/bin/sh

if [ $USER != "root" ]; then
    echo "Need root access"
    exit
fi

while [ 1 ]; do
    dmesg -c
    sleep 0.2
done
