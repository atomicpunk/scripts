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

INFILE=""
OUTFILE=""
TITLE=""
AUTHOR="Todd E Brandt"
COPYRIGHT="Copyright 2013 Todd Brandt <tebrandt@frontier.com>"

printHelp() {
    echo ""
    echo "USAGE: convertvideo.sh -i infile [-o outfile] [-c]"
    echo "  Arguments:"
    echo "   -i infile(s) : input video file, combines multiple files (file1,file2,...)"
    echo "   -o outfile   : output video file (default: infile.mp4)"
    echo "   -t title     : output video file title (default: outfile name)"
    echo "   -c           : perform color correction"
    echo "   -h           : print this help text"
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
    if [ -z "$CHECK" ]; then
        onError "$1 is not installed\ntry 'sudo apt-get install $1'"
    fi
}

filesExist() {
    FILES=`echo $1 | tr ',' '\n'`
    for file in $FILES;
    do
        if [ ! -e "$file" ]; then onError "$file doesn't exist"; fi
    done
    COUNT=`echo $1 | tr ',' '\n' | wc -l`
    if [ "$COUNT" != "1" ]; then
        return 1
    fi
    return 0
}

stampMetadata() {
    ATITLE=$TITLE
    if [ -z "$ATITLE" ]; then
        ATITLE=`echo $1 | sed "s/\..*//"`
    fi
    TMPFILE=`tempfile -s .mp4`
    avconv -y -i $1 -vcodec copy -acodec copy \
    -metadata title="$ATITLE" \
    -metadata author="$AUTHOR" \
    -metadata copyright="$COPYRIGHT" \
    $TMPFILE
    mv -f $TMPFILE $1
}

convertFile() {
    mencoder -of lavf -lavfopts format=mp4 -oac lavc -ovc lavc -lavcopts \
aglobal=1:vglobal=1:\
acodec=libfaac:vcodec=mpeg4:\
abitrate=96:vbitrate=1500:\
keyint=250:mbd=1:vqmax=10:lmax=10:vpass=1:turbo \
    -af lavcresample=44100 -vf harddup "$1" -o "$2"

    stampMetadata $2
}

combineFiles() {
    mencoder -oac copy -ovc copy -idx -o $1
    stampMetadata $1
}

checkTool "mencoder"
checkTool "avconv"

while [ "$1" ] ; do
  case "$1" in
    -i)
      shift
      if [ ! $1 ]; then onError "-i missing infile"; fi
      INFILE=$1
      ;;
    -o)
      shift
      if [ ! $1 ]; then onError "-o missing outfile"; fi
      OUTFILE=$1
      ;;
    -t)
      shift
      if [ ! $1 ]; then onError "-t missing title string"; fi
      TITLE=$1
      ;;
    -h)
      COLOR=1
      ;;
    *)
      onError "Unknown argument ($1)"
      ;;
  esac
  shift
done

if [ -z "$INFILE" ]; then
    printHelp
    exit
fi

filesExist $INFILE
ISLIST=$?
if [ -z "$OUTFILE" ]; then
    if [ $ISLIST -eq 1 ]; then
        onError "You must supply and output filename when combining files"
    else
        BASENAME=`echo $INFILE | sed "s/\..*//"`
        OUTFILE="$BASENAME.mp4"
    fi
fi

if [ $ISLIST -eq 0 ]; then
    echo "Converting $INFILE to $OUTFILE ..."
    convertFile $INFILE $OUTFILE
else
    CONFILES=""
    for file in $FILES;
    do
        BASENAME=`echo $file | sed "s/\..*//"`
        CONFILE="$BASENAME.mp4"
        CONFILES="$CONFILES $CONFILE"
        echo "Converting $file to $CONFILE ..."
        convertFile $file $CONFILE
    done
    echo "Combining $CONFILES into $OUTFILE ..."
    combineFiles "$OUTFILE $CONFILES"
fi
