#!/bin/sh
#
# Copyright 2020 Todd Brandt <tebrandt@frontier.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

TMPDIR=""
MP4NAME="out.mp4"
TITLE="timelapse"

stampMetadata() {
    AUTHOR="Todd E Brandt"
    COPYRIGHT="Copyright 2014 Todd Brandt <tebrandt@frontier.com>"

	TMPVID=`tempfile -s .mp4`
	if [ -e $TMPVID ]; then
		rm $TMPVID
	fi
    avconv -y -i "$1" -vcodec copy -acodec copy \
    -metadata title="$TITLE" \
    -metadata author="$AUTHOR" \
    -metadata copyright="$COPYRIGHT" \
    "$TMPVID"

    mv -f "$TMPVID" "$1"
}

setup() {
	if [ -e $MP4NAME ]; then
		rm $MP4NAME
	fi
	TMPDIR=`mktemp -d`
}

finish() {
	if [ -d $TMPDIR ]; then
		rm -rf $TMPDIR
	fi
}

generate() {
	echo "Creating $TITLE..."
	case "$2" in
		1.0)
			avconv -y -i $TMPDIR/image%05d.jpg -c:v libx264 -r 24 $1
		;;
		*)
			avconv -y -i $TMPDIR/image%05d.jpg -c:v libx264 -r 24 -vf "setpts=${2}*PTS" $1
		;;
	esac
#	stampMetadata "$1"
}

printHelp() {
    echo ""
    echo "USAGE: $0 mp4name slowby <image file list>"
    echo ""
}

onError() {
	printHelp
	echo "ERROR: $1"
	echo ""
    exit
}

checkTool() {
    CHECK=`which $1`
    PKG=$1
    if [ $1 = "avconv" -o $1 = "avprobe" ]; then
        PKG="libav-tools"
    fi
    if [ -z "$CHECK" ]; then
        onError "$1 is not installed\ntry 'sudo apt-get install $PKG'"
    fi
}

if [ $# -lt 3 ]; then printHelp; exit; fi

checkTool "avconv"
setup
MP4NAME=$1
shift
SLOW=$1
shift
echo "Copying images..."
COUNT=0
while [ "$1" ] ; do
	IDX=`seq -f "%05.0f" $COUNT $COUNT`
	cp -np $1 $TMPDIR/image${IDX}.jpg
	COUNT=`expr $COUNT + 1`
	shift
done
generate $MP4NAME $SLOW
finish
