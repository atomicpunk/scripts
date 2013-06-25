#!/bin/sh

SERVER='local'
if [ $# -gt 0 ]; then
    SERVER=$1
    if [ "$SERVER" != "local" ]; then
        CHECK=`ping -q -w 1 $SERVER | grep ", 0% packet loss,"`
        if [ -z "$CHECK" ]; then
            echo "Host $SERVER is unreachable"
            exit
        fi
    fi
fi

if [ "$SERVER" != "local" ]; then
    OS=`ssh $SERVER 'lsb_release -i -r -s | tr "\n" " "'`
    ARCH=`ssh $SERVER "arch"`
else
    SERVER=`hostname`
    SERVER="$SERVER (local)"
    OS=`lsb_release -i -r -s | tr '\n' ' '`
    ARCH=`arch`
fi

echo "$SERVER: $OS$ARCH"
