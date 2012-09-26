#!/bin/sh

#
# Copyright 2012 Todd Brandt <tebrandt@frontier.com>
#
# This program is free software; you may redistribute it and/or modify it
# under the same terms as Perl itself.
#    trancearoundtheworld mp3 archive sync utility
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

BASE="/media/fatman/Music/music/anjunamixes"
SERVER="http://static.anjunabeats.com/tatw-archives"

if [ $# -gt 1 ]; then
    echo "USAGE: $0 \<local path\>"
    exit
elif [ $# -eq 1 ]; then
    BASE=$1
    if [ ! -d "$BASE" ]; then
        echo "ERROR: $BASE is not a valid directory"
        exit
    elif [ ! -w "$BASE" -o ! -x "$BASE" ]; then
        echo "ERROR: $BASE is not writable by this user"
        exit
    fi
fi

echo "Synchronizing anjunamixes:"
i=`expr 400`
while [ $i -gt 0 ]
do
    FILE="TATW$i.mp3"
    SFILE="$SERVER/$FILE"
    LFILE="$BASE/$FILE"
    SSIZE=`wget --spider $SFILE 2>&1 | grep Length | awk '{print $2}'`
    if [ -z "$SSIZE" ]; then
        echo -n "$FILE not on server       \r"
    else
        if [ -f $LFILE ]; then
            LSIZE=`ls -l $LFILE | awk '{print $5}'`
        fi
        if [ ! -f $LFILE -o $WSIZE -gt $LSIZE ]; then
            echo "DOWNLOADING $FILE..."
            wget $SERVER/$FILE -O $BASE/$FILE
        else
            echo -n "$FILE is valid        \r"
        fi
    fi
    i=`expr $i - 1`
done
