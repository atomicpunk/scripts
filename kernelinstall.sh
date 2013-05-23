#!/bin/sh

SERVER="ixion.local"
RPATH="/home/tebrandt/workspace"
KVER="3.8.0-22"
ARCH="i386"

if [ "$USER" != "root" ]; then
    echo "Please run as root"
    exit;
fi

FILES="linux-headers-${KVER}_${KVER}.*_all.deb \
       linux-headers-${KVER}-generic_${KVER}.*_${ARCH}.deb \
       linux-image-${KVER}-generic_${KVER}.*_${ARCH}.deb \
       linux-image-extra-${KVER}-generic_${KVER}.*_${ARCH}.deb"

cd /tmp
for file in $FILES
do
    rm -f $file
    FULLNAME=`ssh $SERVER ls -1 $RPATH/$file 2>/dev/null`
    if [ -z "$FULLNAME" ]; then
        echo "CANNOT FIND: $file"
        exit;
    else
        echo $FULLNAME
        scp $SERVER:$FULLNAME .
    fi
done

dpkg -i $FILES
