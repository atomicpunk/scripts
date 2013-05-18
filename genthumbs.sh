#!/bin/sh

WWWDIR="/var/www/private"
IMGDIR="/media/tebrandt/fatman2/Pictures/scans"

cd $IMGDIR
IMAGES=`ls scan*.jpg`
TOTAL=`ls scan*.jpg | wc -l`
for i in $IMAGES;
do
    if [ ! -e $WWWDIR/$i ]; then
        echo exporting $i
        cp $i $WWWDIR/$i
    fi
done
exit
cd $WWWDIR
IMAGES=`ls scan*.jpg`
TOTAL=`ls scan*.jpg | wc -l`
for i in $IMAGES;
do
    if [ ! -e "th-$i" ]; then
        echo $i
        convert -define jpeg:size=200x200 $i -thumbnail 150x150^ -gravity center -extent 150x150 th-$i
    fi
done
echo "var total = $TOTAL;" > js/total.js

