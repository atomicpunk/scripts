#!/bin/sh

#
# Copyright 2012 Todd Brandt <tebrandt@frontier.com>
#
# This program is free software; you may redistribute it and/or modify it
# under the same terms as Perl itself.
#    utility to set up development windows quickly
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

POS="left"
if [ $# -gt 1 ]; then
    echo "USAGE: $0 \<left/middle/right\>"
    exit
elif [ $# -eq 1 ]; then
    BASE=$1
    if [ "$1" = "left" -o "$1" = "middle" -o "$1" = "right" ]; then
        POS=$1
    else
        echo "ERROR: left, middle, or right please"
        exit
    fi
fi

VALS=`xrandr | grep "connected.*mm" | sed -e "s/ (.*//;s/.* connected //;s/[x+]/ /g" | awk '{print $3,$4,$1,$2}' | sort | tr '\n' ' '`
NUM=`echo $VALS | wc -w`
if [ $NUM -ne 12 -a $NUM -ne 8 -a $NUM -ne 4 ]; then
    echo "ERROR: xrandr output not understood"
    exit
fi

X=`echo $VALS | awk '{print $1}'`
Y=`echo $VALS | awk '{print $2}'`
W=`echo $VALS | awk '{print $3}'`
H=`echo $VALS | awk '{print $4}'`

if [ $NUM -eq 8 ]; then
    if [ "$POS" = "right" ]; then
        X=`echo $VALS | awk '{print $5}'`
        Y=`echo $VALS | awk '{print $6}'`
        W=`echo $VALS | awk '{print $7}'`
        H=`echo $VALS | awk '{print $8}'`
    fi
fi

if [ $NUM -eq 12 ]; then
    if [ "$POS" = "middle" ]; then
        X=`echo $VALS | awk '{print $5}'`
        Y=`echo $VALS | awk '{print $6}'`
        W=`echo $VALS | awk '{print $7}'`
        H=`echo $VALS | awk '{print $8}'`
    elif [ "$POS" = "right" ]; then
        X=`echo $VALS | awk '{print $9}'`
        Y=`echo $VALS | awk '{print $10}'`
        W=`echo $VALS | awk '{print $11}'`
        H=`echo $VALS | awk '{print $12}'`
    fi
fi

echo "Display: X=$X Y=$Y $W x $H"

TH=`expr $H / 18`
TW=`expr $W / 24`
T1X=`expr $X`
T2X=`expr $W / 3 - 50 + $X`
T3X=`expr 2 \* $W / 3 - 50 + $X`
TY=$Y

echo "Terminal Dimensions $TW"x"$TH"

gnome-terminal --geometry="$TW"x"$TH"+"$T1X"+"$TY"
gnome-terminal --geometry="$TW"x"$TH"+"$T2X"+"$TY"
gnome-terminal --geometry="$TW"x"$TH"+"$T3X"+"$TY"
