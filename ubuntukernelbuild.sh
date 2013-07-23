#!/bin/sh

SERVER=""
REBOOT="no"
KBUILD="ubuntu-raring"
#OPATH="/ramdisk/"
#BPATH="/ramdisk/$KBUILD"
OPATH="/home/tebrandt/workspace/"
BPATH="/home/tebrandt/workspace/$KBUILD"
LOG="$OPATH/build.log"
KVER=`cat $BPATH/debian/control | grep "Package: linux-image" | head -1 | sed "s/Package: linux-image-//;s/-generic//"`
BVER=`head -1 $BPATH/debian/changelog | sed "s/.*(//;s/).*//"`
ARCH="amd64"
HEADPKG="linux-headers-${KVER}_${BVER}_all.deb"
HEADGENPKG="linux-headers-${KVER}-generic_${BVER}_${ARCH}.deb"
IMAGEPKG="linux-image-${KVER}-generic_${BVER}_${ARCH}.deb"
EXTRAPKG="linux-image-extra-${KVER}-generic_${BVER}_${ARCH}.deb"

if [ -z "$KVER" ]; then
    echo "Couldn't find the kernel version"
    exit
fi

if [ -z "$BVER" ]; then
    echo "Couldn't find the build version"
    exit
fi

if [ $# -gt 3 ]; then
    echo "USAGE: kernelbuild.sh <arch> <machine> <reboot>"
    exit
fi
if [ $# -eq 3 ]; then
    if [ $3 = "reboot" ]; then
        REBOOT="yes"
    else
        echo "USAGE: kernelbuild.sh <arch> <machine> <reboot>"
        exit
    fi
fi
if [ $# -gt 1 ]; then
    SERVER=$2
    if [ "$SERVER" != "local" ]; then
        CHECK=`ping -q -w 1 $SERVER | grep ", 0% packet loss,"`
        if [ -z "$CHECK" ]; then
            echo "Host $SERVER is unreachable"
            exit
        fi
    fi
fi
if [ $# -gt 0 ]; then
    ARCH=$1
fi

echo "Bulding $KBUILD kernel v${KVER}..."
rm -f $OPATH/linux-*${KVER}*_${ARCH}.deb
cd $BPATH
fakeroot debian/rules clean
echo "Beginning build" > $LOG
tail -f $LOG &
LOGPID=$!
leave() {
    kill $LOGPID
    exit
}
CONCURRENCY_LEVEL=12 DEB_HOST_ARCH=${ARCH} AUTOBUILD=1 NOEXTRAS=1 fakeroot debian/rules binary-headers binary-generic > $LOG 2>&1

# check on the output files
cd $OPATH
if [ ! -e $HEADPKG ]; then
    echo "Missing package: $HEADPKG"
    leave
fi
if [ ! -e $HEADGENPKG ]; then
    echo "Missing package: $HEADPKG"
    leave
fi
if [ ! -e $IMAGEPKG ]; then
    echo "Missing package: $HEADPKG"
    leave
fi
if [ ! -e $EXTRAPKG ]; then
    echo "Missing package: $HEADPKG"
    leave
fi

if [ -n "$SERVER" ]; then
    if [ $SERVER = "local" ]; then
        echo "INSTALLING LOCALLY"
        sudo dpkg -i $HEADPKG $HEADGENPKG $IMAGEPKG $EXTRAPKG
        if [ "$REBOOT" = "yes" ]; then
            echo "REBOOTING $SERVER"
            sudo reboot
        fi
    else
        echo "INSTALLING ON $SERVER"
        scp $HEADPKG $HEADGENPKG $IMAGEPKG $EXTRAPKG ${SERVER}:/home/tebrandt/Downloads/
        ssh -X root@$SERVER "cd /home/tebrandt/Downloads; dpkg -i $HEADPKG $HEADGENPKG $IMAGEPKG $EXTRAPKG"
        if [ "$REBOOT" = "yes" ]; then
            echo "REBOOTING $SERVER"
            ssh -X root@$SERVER "reboot"
        fi
    fi
else
    echo "BUILD COMPLETE"
    ls -1 $OPATH/linux-*${KVER}*_${ARCH}.deb
fi
date
leave
