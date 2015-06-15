#!/bin/bash
#
# GPS Privacy: a tool to remove personal data from image files before
# submitting them publicly. Your phone can stamp images with a lat/lon
# giving total strangers a map to your house. Even without the GPS stamp
# some image sites will find your location via your IP address. This script
# deletes the GPS stamp for all images found and replaces it with a fake
# location. This way the image sites will always map the photos to a fake
# location in the middle of the Pacific ocean.
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

fakeGPS() {
	exiv2 \
	-M"set Exif.GPSInfo.GPSVersionID 1 2 3 4" \
	-M"set Exif.GPSInfo.GPSLatitudeRef S" \
	-M"set Exif.GPSInfo.GPSLatitude 6/1 19/1 57932/1000" \
	-M"set Exif.GPSInfo.GPSLongitudeRef W" \
	-M"set Exif.GPSInfo.GPSLongitude 114/1 14/1 32003/1000" \
	-M"set Exif.GPSInfo.GPSAltitudeRef 0" \
	-M"set Exif.GPSInfo.GPSAltitude 0/1" \
	$1
}

copyright() {
	exiv2 \
	-M"set Exif.Image.Copyright 2014 Todd Brandt <tebrandt@frontier.com>" \
	$1
}

editMetaData() {
	B=`echo $1 | tr '.' '\n' | head -1`
	E=`echo $1 | tr '.' '\n' | tail -1`
	INPUT=$1
	OUTPUT=${B}_private.${E}
	cp -f $INPUT $OUTPUT
	fakeGPS $OUTPUT
#	copyright $OUTPUT
}

printHelp() {
	echo -e "\nUSAGE: privacy.sh <image file list>\n"
}

onError() {
	echo -e "\nERROR: $1"
	exit
}

fileExists() {
	if [ ! -e "$1" ]; then onError "$1 doesn't exist"; fi
}

if [ $# -lt 1 ]; then printHelp; fi

while [ $1 ]; do
	editMetaData $1
	shift
done
