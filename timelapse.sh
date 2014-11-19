#!/bin/sh
#
# Copyright 2012 Todd Brandt <tebrandt@frontier.com>
#
# This program is free software; you may redistribute it and/or modify it
# under the same terms as Perl itself.
#    utility to organize media collections
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

getConfig() {
	HOUR=`date +"%H"`
	if [ $HOUR -lt 7 -o $HOUR -gt 16 ]; then
		# night
		CONFIG="night"
		EXPMODE="Manual Mode"
		EXPVAL="2047"
		EXPAUTOPRI="False"
		BRIGHTNESS="160"
	else
		# day
		CONFIG="day"
		EXPMODE="Aperture Priority Mode"
		EXPVAL="0"
		EXPAUTOPRI="True"
		BRIGHTNESS="128"
	fi
}

RESOLUTION="1920x1080"
DEVICE="/dev/video0"
FOCUS=0
D=`date "+%m%d%y"`
T=`date "+%H%M%S"`
OUTDIR="/home/tebrandt/Pictures/roof/${D}"
OUTFILE="roof-${D}-${T}.jpg"
LATEST="/home/tebrandt/Pictures/roof/latest.jpg"

getConfig

echo "Configuration           : $CONFIG"
echo "Filename                : $OUTFILE"
echo "Brightness              : $BRIGHTNESS"
echo "Exposure, Auto          : $EXPMODE"
echo "Exposure (Absolute)     : $EXPVAL"
echo "Exposure, Auto Priority : $EXPAUTOPRI"
echo "Focus (absolute)        : $FOCUS"

mkdir -p $OUTDIR
fswebcam -d $DEVICE -r $RESOLUTION --no-banner \
-s "Focus, Auto=False" \
-s "Focus (absolute)=$FOCUS" \
-s "Exposure, Auto=$EXPMODE" \
-s "Exposure (Absolute)=$EXPVAL" \
-s "Exposure, Auto Priority=$EXPAUTOPRI" \
-s "Brightness=$BRIGHTNESS" \
$OUTDIR/$OUTFILE
cp -f $OUTDIR/$OUTFILE $LATEST
