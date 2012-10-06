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
TERMS=3

if [ $# -eq 1 -o $# -gt 2 ]; then
    echo "USAGE: $0 \<1/2/3\> \<left/middle/right\>"
    exit
elif [ $# -eq 2 ]; then
    if [ "$2" = "left" -o "$2" = "middle" -o "$2" = "right" ]; then
        POS=$2
    else
        echo "ERROR: left, middle, or right position please"
        exit
    fi
    if [ $1 -eq 1 -o $1 -eq 2 -o $1 -eq 3 ]; then
        TERMS=$1
    else
        echo "ERROR: 1, 2, or 3 terms please"
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
TW=`expr $W / 9 / $TERMS`
if [ $TERMS -eq 3 ]; then
    TW=`expr $W / 24`
fi

echo "Terminal Dimensions $TW"x"$TH"

TY=$Y
T1X=`expr $X`

if [ $TERMS -lt 3 ]; then
    T2X=`expr $W / 2 + $X`
else
    T2X=`expr $W / 3 - 50 + $X`
    T3X=`expr 2 \* $W / 3 - 50 + $X`
fi

if [ $TERMS -gt 0 ]; then
    gnome-terminal --geometry="$TW"x"$TH"+"$T1X"+"$TY"
fi
if [ $TERMS -gt 1 ]; then
    gnome-terminal --geometry="$TW"x"$TH"+"$T2X"+"$TY"
fi
if [ $TERMS -gt 2 ]; then
    gnome-terminal --geometry="$TW"x"$TH"+"$T3X"+"$TY"
fi
