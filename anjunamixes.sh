#!/bin/sh

BASE="/media/fatman/Music/music/anjunamixes"
SERVER="http://static.anjunabeats.com/tatw-archives"
#SERVER="http://tatw-archives.anjunabeats.com"

echo "Synchronizing anjunamixes:"
i=`expr 500`
while [ $i -gt 0 ]
do
    DL=0
    FILE="TATW$i.mp3"
    WSIZE=`wget --spider $SERVER/$FILE 2>&1 | grep Length | awk '{print $2}'`
    if [ -z "$WSIZE" ]; then
        echo -n "$FILE not on server       \r"
    else
        LSIZE=`ls -l $BASE/$FILE | awk '{print $5}'`
        if [ $WSIZE -gt $LSIZE ]; then
            echo "DOWNLOADING $FILE..."
            wget $SERVER/$FILE -O $BASE/$FILE
        else
            echo -n "$FILE is valid        \r"
        fi
    fi
    i=`expr $i - 1`
done
