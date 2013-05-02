#!/bin/sh

#
# Copyright 2012 Todd Brandt <tebrandt@frontier.com>
#
# This program is free software; you may redistribute it and/or modify it
# under the same terms as Perl itself.
#    utility to set up development windows quickly
#    Copyright (C) 2012 Todd Brandt <tebrandt@frontier.com>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

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
