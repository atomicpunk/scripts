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
#

TMPDIR="/tmp/movie-from-images"
MP4NAME="out.mp4"
TITLE="timelapse"
MODE="all"
SLOW="1.0"
HOUR=""
DATE=""
PREFIX=`pwd | sed "s/.*\///"`

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

addAudioTrack() {
    genTempVid
    avconv -i "$1" -an -c:v copy "$TMPVID"
    if [ -e $TMPVID -a -s $TMPVID ]; then
        MUTEFILE=$TMPVID
    else
        echo "ERROR: avconv failed to remove the existing audio track"
        rm $TMPVID
        return
    fi
    genTempVid
    avconv -y -i "$MUTEFILE" -i "$2" $3 -vcodec copy -acodec copy $TMPVID
    rm $MUTEFILE
    if [ -e $TMPVID -a -s $TMPVID ]; then
        mv -f $TMPVID $1
    else
        echo "ERROR: avconf failed to add the new track"
        rm $TMPVID
        return
    fi

    stampMetadata "$1"
}

setup() {
	if [ -e $MP4NAME ]; then
		rm $MP4NAME
	fi
	if [ -d $TMPDIR ]; then
		rm -f $TMPDIR/*
	else
		mkdir $TMPDIR
	fi
}

finish() {
	if [ -d $TMPDIR ]; then
		rm -r $TMPDIR/*
	fi
}

copyFrame() {
	FILE=$1
	IDX=$2
	M=`echo $FILE | cut -c1-2`
	D=`echo $FILE | cut -c3-4`
	Y=`echo $FILE | cut -c5-6`
	H=`echo $FILE | cut -c22-23`
	I=`echo $FILE | cut -c24-25`
	echo "$IDX: $FILE"
	TIME=`date -d "$Y$M$D $H:$I" "+%b %d  %H:%M"`
	convert -font Arial-Regular -pointsize 40 -fill white -draw "text 10,1070\"$TIME\"" $FILE $TMPDIR/image${IDX}.jpg
}

list10min() {
	DIRS="$DATE"
	if [ -z "$DATE" ]; then
		DIRS=`ls -1d ??????`
	fi
	COUNT=0
	for dir in $DIRS; do
		if [ ! -d $dir ]; then continue; fi
		for i in `seq -f "%02.0f" 0 23`; do
			for j in `seq 0 5`; do
				FILE=`ls -1 $dir/${PREFIX}-$dir-${i}${j}???.jpg 2>/dev/null | head -1`
				if [ -n "$FILE" ]; then
					IDX=`seq -f "%05.0f" $COUNT $COUNT`
					copyFrame $FILE $IDX
					COUNT=`expr $COUNT + 1`
				fi
			done
		done
	done
}

list30min() {
	DIRS="$DATE"
	if [ -z "$DATE" ]; then
		DIRS=`ls -1d ??????`
	fi
	COUNT=0
	for dir in $DIRS; do
		if [ ! -d $dir ]; then continue; fi
		for i in `seq -f "%02.0f" 0 23`; do
			for j in `seq 0 3 3`; do
				FILE=`ls -1 $dir/${PREFIX}-$dir-${i}${j}???.jpg 2>/dev/null | head -1`
				if [ -n "$FILE" ]; then
					IDX=`seq -f "%05.0f" $COUNT $COUNT`
					copyFrame $FILE $IDX
					COUNT=`expr $COUNT + 1`
				fi
			done
		done
	done
}

listHourly() {
	DIRS="$DATE"
	if [ -z "$DATE" ]; then
		DIRS=`ls -1d ??????`
	fi
	COUNT=0
	for dir in $DIRS; do
		if [ ! -d $dir ]; then continue; fi
		for i in `seq -f "%02.0f" 0 23`; do
			FILE=`ls -1 $dir/${PREFIX}-$dir-${i}0???.jpg 2>/dev/null | head -1`
			if [ -n "$FILE" ]; then
				IDX=`seq -f "%05.0f" $COUNT $COUNT`
				copyFrame $FILE $IDX
				COUNT=`expr $COUNT + 1`
			fi
		done
	done
}

listDaily() {
	DIRS="$DATE"
	if [ -z "$DATE" ]; then
		DIRS=`ls -1d ??????`
	fi
	COUNT=0
	for dir in $DIRS; do
		if [ ! -d $dir ]; then continue; fi
		FILE=`ls -1 $dir/${PREFIX}-$dir-${HOUR}0???.jpg 2>/dev/null | head -1`
		if [ -n "$FILE" ]; then
			IDX=`seq -f "%05.0f" $COUNT $COUNT`
			copyFrame $FILE $IDX
			COUNT=`expr $COUNT + 1`
		fi
	done
}

listAll() {
	DIRS="$DATE"
	if [ -z "$DATE" ]; then
		DIRS=`ls -1d ??????`
	fi
	COUNT=0
	for dir in $DIRS; do
		if [ ! -d $dir ]; then continue; fi
		for file in `ls -1 $dir/${PREFIX}-$dir-??????.jpg 2>/dev/null`; do
			IDX=`seq -f "%05.0f" $COUNT $COUNT`
			copyFrame $file $IDX
			COUNT=`expr $COUNT + 1`
		done
	done
}

generate() {
	echo "Creating $TITLE..."
	case "$SLOW" in
		1.0)
			avconv -i $TMPDIR/image%05d.jpg -c:v libx264 -r 24 $MP4NAME
		;;
		*)
			avconv -i $TMPDIR/image%05d.jpg -c:v libx264 -r 24 -vf "setpts=${SLOW}*PTS" $MP4NAME
		;;
	esac
	stampMetadata "$MP4NAME"
}

printHelp() {
    echo ""
    echo "USAGE: movie.sh <args>"
    echo "  Arguments:"
    echo "     -t <title>"
    echo "        desc : set the title of the movie"
    echo "     -m <mode>"
    echo "        desc : set the timelapse mode - hourly/all (default: all)"
    echo "     -s <speed>"
    echo "        desc : set the movie speed - normal/half/quarter (default: normal)"
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

# -- init --

checkTool "avconv"

# -- parse commands and arguments --

if [ $# -lt 1 ]; then printHelp; fi

while [ "$1" ] ; do
	case "$1" in
		-t)
			shift
			if [ ! "$1" ]; then onError "-t: missing argument"; fi
			TITLE=`echo "$1" | sed "s/\..*//;s/_/ /g;s/-/ /g"`
			MP4NAME="${1}.mp4"
		;;
		-m)
			shift
			if [ ! "$1" ]; then onError "-m: missing argument"; fi
			MODE="$1"
		;;
		-s)
			shift
			if [ ! "$1" ]; then onError "-s: missing argument"; fi
			SLOW="$1"
		;;
		-h)
			shift
			if [ ! "$1" ]; then onError "-h: missing argument"; fi
			HOUR="$1"
		;;
		-d)
			shift
			if [ ! "$1" ]; then onError "-d: missing argument"; fi
			DATE="$1"
		;;
		*)
			onError "Invalid argument ($1)"
		;;
	esac
	shift
done

setup
case "$MODE" in
	all)
		listAll
	;;
	10min)
		list10min
	;;
	30min)
		list30min
	;;
	hourly)
		listHourly
	;;
	daily)
		if [ -z "$HOUR" ]; then onError "daily: -h is required"; fi
		listDaily
	;;
	*)
		onError "Invalid mode ($MODE)"
	;;
esac
generate
#finish
