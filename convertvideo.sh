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
    echo "USAGE: convertvideo.sh -i infile [-o outfile] [-c]"
    echo "  Arguments:"
    echo "   -i infile  : input video file"
    echo "   -o outfile : output video file (default: infile.mp4)"
    echo "   -c         : perform color correction"
    echo "   -h         : print this help text"
    echo ""
    exit
}

onError() {
    echo ""
    echo "ERROR: $1"
    printHelp
}

fileExists() {
    if [ ! -e "$1" ]; then onError "$1 doesn't exist"; fi
}

INFILE=""
OUTFILE=""
COLOR=0

while [ "$1" ] ; do
  case "$1" in
    -i)
      shift
      if [ ! $1 ]; then onError "-i missing infile"; fi
      INFILE=$1
      fileExists $INFILE
      ;;
    -o)
      shift
      if [ ! $1 ]; then onError "-o missing outfile"; fi
      OUTFILE=$1
      ;;
    -c)
      COLOR=1
      ;;
    -h)
      COLOR=1
      ;;
    *)
      onError "Unknown argument ($1)"
      ;;
  esac
  shift;
done;

if [ -z "$INFILE" ]; then
    printHelp
    exit
fi

if [ -z "$OUTFILE" ]; then
    BASENAME=`echo $INFILE | sed "s/\..*//"`
    OUTFILE="$BASENAME.mp4"
fi

echo "Converting $INFILE to $OUTFILE ..."

mencoder -of lavf -lavfopts format=mp4 -oac lavc -ovc lavc -lavcopts aglobal=1:\
vglobal=1:acodec=libfaac:vcodec=mpeg4:abitrate=96:vbitrate=1500:keyint=250:\
mbd=1:vqmax=10:lmax=10:vpass=1:turbo -af lavcresample=44100 -vf harddup \
"$INFILE" -o "$OUTFILE"
