#!/bin/sh

IMAGEDIR="/home/tebrandt/workspace/websites/familyarchives/private/images"
THUMBDIR="/home/tebrandt/workspace/websites/familyarchives/private/thumbs"
IMGDIR="/media/fatman/Pictures/scans"

cd $IMGDIR
IMAGES=`ls *.jpg`
TOTAL=`ls *.jpg | wc -l`
for i in $IMAGES;
do
    if [ ! -e $IMAGEDIR/$i ]; then
        echo $IMAGEDIR/$i
        convert $i -resize 1280x720\> $IMAGEDIR/$i
        exiv2 -M"set Exif.Image.Copyright Copyright (c) 2013, Todd Brandt" $IMAGEDIR/$i
        exiv2 -M"set Exif.Photo.UserComment Not to be used without the explicit permission of Todd Brandt" $IMAGEDIR/$i
    fi
    if [ ! -e $THUMBDIR/$i ]; then
        echo $THUMBDIR/$i
        convert -define jpeg:size=150x150 $i -thumbnail 150x150^ -gravity center -extent 150x150 $THUMBDIR/$i
        exiv2 -M"set Exif.Image.Copyright Copyright (c) 2013, Todd Brandt" $THUMBDIR/$i
        exiv2 -M"set Exif.Photo.UserComment Not to be used without the explicit permission of Todd Brandt" $THUMBDIR/$i
    fi
done
