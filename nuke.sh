#!/bin/sh

if [ $USER != "root" ]; then
    echo "must be root"
    exit
fi

if [ $# -eq 0 ]; then
    echo "USAGE: $0 <drive>"
    exit
fi

DRIVE=$1
if [ ! -e $DRIVE ]; then
    echo "$DRIVE doesn't exist"
    exit
fi

STAT=`fdisk -l $DRIVE`
if [ -z "$STAT" ]; then
    echo "$DRIVE doesn't appear to be a valid drive"
    exit
fi

STAT=`cat /proc/mounts | grep $DRIVE`
if [ -n "$STAT" ]; then
    echo "$DRIVE is mounted"
    exit
fi

echo "WRITING 0's to $DRIVE"
dd if=/dev/zero of=$DRIVE bs=1M
echo "WRITING 1's to $DRIVE"
tr '\000' '\377' < /dev/zero | dd of=$DRIVE bs=1M
echo "WRITING 0's to $DRIVE"
dd if=/dev/zero of=$DRIVE bs=1M
echo "$DRIVE is wiped"
