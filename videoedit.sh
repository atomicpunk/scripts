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

stampMetadata() {
    if [ "$2" ]; then
        TITLE=$2
    else
        TITLE=`echo "$1" | sed "s/\..*//;s/_/ /g"`
    fi
    AUTHOR="Todd E Brandt"
    COPYRIGHT="Copyright 2013 Todd Brandt <tebrandt@frontier.com>"
    TMPFILE=`tempfile -s .mp4`

    avconv -y -i "$1" -vcodec copy -acodec copy \
    -metadata title="$TITLE" \
    -metadata author="$AUTHOR" \
    -metadata copyright="$COPYRIGHT" \
    "$TMPFILE"

    mv -f "$TMPFILE" "$1"
}

addAudioTrack() {
    TMPFILE=`tempfile -s .mp4`
    mencoder -ovc copy -nosound "$1" -o $TMPFILE
    if [ -e $TMPFILE -a -s $TMPFILE ]; then
        MUTEFILE=$TMPFILE
    else
        echo "ERROR: mencoder failed to remove the existing audio track"
        rm $TMPFILE
        return
    fi
    TMPFILE=`tempfile -s .mp4`
    avconv -y -i "$MUTEFILE" -i "$2" -shortest -vcodec copy -acodec copy $TMPFILE
    rm $MUTEFILE
    if [ -e $TMPFILE -a -s $TMPFILE ]; then
        mv -f $TMPFILE $1
    else
        echo "ERROR: avconf failed to add the new track"
        rm $TMPFILE
        return
    fi

    stampMetadata "$1"
}

convertFile() {
    echo "Converting $1 to $2 ..."

    mencoder -of lavf -lavfopts format=mp4 -oac lavc -ovc lavc -lavcopts \
aglobal=1:vglobal=1:acodec=libfaac:vcodec=mpeg4:abitrate=128:vbitrate=1500:\
keyint=250:mbd=1:vqmax=10:lmax=10:vpass=1:turbo \
    -af lavcresample=44100 -vf harddup "$1" -o "$2"

    stampMetadata "$2"
}

combineFiles() {
    mencoder -oac copy -ovc copy -idx -o "$1" $2
    stampMetadata "$1"
}

printHelp() {
    echo ""
    echo "USAGE: video.sh command <args>"
    echo "  Commands:"
    echo "     convert"
    echo "        desc : converts a list of video files from avi to mp4"
    echo "        args : file1 file2 file3 ..."
    echo "     combine"
    echo "        desc : combines multiple video files into one video file"
    echo "        args : outfile infile1 infile2 infile3 ..."
    echo "     audio"
    echo "        desc : add an audio track to a video file"
    echo "        args : videofile audiofile"
    echo "     title"
    echo "        desc : add a title to a video file"
    echo "        args : videofile titletext"
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

checkTool "mencoder"
checkTool "avconv"
checkTool "avprobe"

# -- parse commands and arguments --

if [ $# -lt 1 ]; then printHelp; fi

COMMAND=$1
shift
case "$COMMAND" in
    convert)
        if [ $# -lt 1 ]; then onError "convert requires at least one file"; fi
        while [ "$1" ] ; do
            fileExists "$1"
            OUTFILE=`echo "$1" | sed "s/\..*/\.mp4/"`
            convertFile "$1" "$OUTFILE"
            shift
        done
    ;;
    combine)
        if [ $# -lt 3 ]; then onError "combine requires at least two infiles and one outfile"; fi
        OUTFILE="$1"
        shift
        INFILES=""
        while [ "$1" ] ; do
            fileExists "$1"
            INFILES="$INFILES $1"
            shift
        done
        combineFiles "$OUTFILE" "$INFILES"
    ;;
    audio)
        if [ $# -ne 2 ]; then onError "audio track requires one audio and one video file"; fi
        fileExists "$1"
        fileExists "$2"
        addAudioTrack "$1" "$2"
    ;;
    title)
        if [ $# -ne 2 ]; then onError "setting the title requires one video file and a string"; fi
        fileExists "$1"
        stampMetadata "$1" "$2"
    ;;
    *)
        onError "Invalid command ($COMMAND)"
    ;;
esac
