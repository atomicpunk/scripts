#!/bin/sh

SERVER=""
REBOOT="no"
KBUILD="ubuntu-raring"
KVER="3.8"
OPATH="/home/tebrandt/workspace/"
BPATH="/home/tebrandt/workspace/$KBUILD"
ARCH="amd64"

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
CONCURRENCY_LEVEL=12 DEB_HOST_ARCH=${ARCH} AUTOBUILD=1 NOEXTRAS=1 fakeroot debian/rules binary-headers binary-generic
cd $OPATH
if [ -n "$SERVER" ]; then
    if [ $SERVER = "local" ]; then
        echo "INSTALLING LOCALLY"
        PKGS=`ls -1 linux-*${KVER}*_${ARCH}.deb | head -2 | tr '\n' ' '`
        sudo dpkg -i $PKGS
        if [ "$REBOOT" = "yes" ]; then
            echo "REBOOTING $SERVER"
            sudo reboot
        fi
    else
        echo "INSTALLING ON $SERVER"
        PKGS=`ls -1 linux-*${KVER}*_${ARCH}.deb | head -2 | tr '\n' ' '`
        scp $PKGS ${SERVER}:/home/tebrandt/Downloads/
        ssh -X root@$SERVER "cd /home/tebrandt/Downloads; dpkg -i $PKGS"
        if [ "$REBOOT" = "yes" ]; then
            echo "REBOOTING $SERVER"
            ssh -X root@$SERVER "reboot"
        fi
    fi
else
    echo "BUILD COMPLETE"
    ls -1 $OPATH/linux-*${KVER}*_${ARCH}.deb
fi
