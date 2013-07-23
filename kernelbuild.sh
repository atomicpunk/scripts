#!/bin/sh

printUsage() {
    echo "USAGE: kernelbuild.sh name <machine> <reboot>"
    exit
}

if [ $# -gt 3 -o $# -lt 1 ]; then
    printUsage
fi
if [ $# -gt 1 ]; then
    SERVER=$2
    if [ "$SERVER" != "local" ]; then
        CHECK=`ping -q -w 1 $SERVER | grep ", 0% packet loss,"`
        if [ -z "$CHECK" ]; then
            echo "Host $SERVER is unreachable"
            exit
        fi
        echo "$SERVER found"
    fi
fi
REBOOT="no"
if [ $# -eq 3 ]; then
    if [ $3 = "reboot" ]; then
        REBOOT="yes"
    else
        printUsage
    fi
fi

OUTPATH="$HOME/workspace"
SRCPATH="$HOME/workspace/linux"
KVER=`cd $SRCPATH; make kernelversion`
ARCH="amd64"
NAME=$1
PKGS="linux-firmware-image_${KVER}-${NAME}-*_${ARCH}.deb \
linux-headers-${KVER}-${NAME}_${KVER}-${NAME}-*_${ARCH}.deb \
linux-image-${KVER}-${NAME}_${KVER}-${NAME}-*_${ARCH}.deb \
linux-libc-dev_${KVER}-${NAME}-*_${ARCH}.deb"

echo "Bulding kernel ${KVER}-${NAME} for ${ARCH}"
for file in $PKGS
do
    rm -f $OUTPATH/$file
done
cd $SRCPATH
make oldconfig
make -j `getconf _NPROCESSORS_ONLN` deb-pkg LOCALVERSION=-$NAME
cd $OUTPATH
for file in $PKGS
do
    if [ ! -e $file ]; then
        echo "ERROR: $file doesn't exist"
        exit
    fi
done
PKGS=`ls -1 $PKGS | tr '\n' ' '`
echo $PKGS
echo "BUILD COMPLETE"
for file in $PKGS
do
    ls -1 $OUTPATH/$file
done

if [ -n "$SERVER" ]; then
    if [ $SERVER = "local" ]; then
        echo "INSTALLING LOCALLY"
        sudo dpkg -i $PKGS
        if [ "$REBOOT" = "yes" ]; then
            sleep 4
            echo "REBOOTING $HOSTNAME"
            sudo reboot
        fi
    else
        echo "INSTALLING ON $SERVER"
        scp $PKGS ${SERVER}:/tmp/
        ssh -X root@$SERVER "cd /tmp; dpkg -i $PKGS"
        if [ "$REBOOT" = "yes" ]; then
            sleep 4
            echo "REBOOTING $SERVER"
            ssh -X root@$SERVER "reboot"
        fi
    fi
fi
