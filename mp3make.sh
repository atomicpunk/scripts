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

printHelp() {
	echo ""
	echo "mp3make - converts a youtube link/playlist to mp3s"
	echo "USAGE: mp3make <youtubelink>"
	echo "   or "
	echo "mp3make - converts a list of media files to mp3s"
	echo "USAGE: mp3make <filemask>"
	echo ""
	exit
}

onError() {
	echo ""
	echo "ERROR: $1"
	printHelp
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

convertFile() {
	MP3NAME=`echo "$1" | sed "s/\(.*\)\..*/\1\.mp3/"`
	echo "INPUT  : $1"
	echo "OUTPUT : $MP3NAME"
	if [ -e "$MP3NAME" ]; then
		echo "(already done)"
		return
	fi
	avconv -loglevel panic -i "$1" "$MP3NAME"
	if [ ! -e "$MP3NAME" ]; then onError "avconv failed to create $MP3NAME"; fi
}

youtubeDownload() {
	BASE=`pwd`
	TMP=`mktemp -d`
	cd $TMP
	youtube-dl "$1"
	for i in *;
	do
		convertFile "$i"
		mv "$TMP/$MP3NAME" "$BASE/"
		echo "SUCCESS: $BASE/$MP3NAME"
	done
	cd "$BASE"
	rm -r "$TMP"
}

if [ $# -lt 1 ]; then printHelp; fi

checkTool "avconv"

if [ -e "$1" ]; then
	while [ "$1" ] ; do
		if [ ! -e "$1" ]; then onError "$1 doesn't exist"; fi
		convertFile "$1"
		shift
	done
else
	checkTool "youtube-dl"
	youtubeDownload "$1"
fi
