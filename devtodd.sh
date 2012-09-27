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

MON="left"
if [ $# -gt 1 ]; then
    echo "USAGE: $0 \<left/right\>"
    exit
elif [ $# -eq 1 ]; then
    BASE=$1
    if [ "$1" = "left" -o "$1" = "right" ]; then
        MON=$1
    else
        echo "ERROR: left or right please"
        exit
    fi
fi

VALS=`xrandr | grep "connected.*mm" | sed -e "s/ (.*//;s/.* connected //;s/[x+]/\n/g"`
NUM=`echo $VALS | wc -w`

if [ "$NUM" != "8" -a "$NUM" != "4" ]; then
    echo "ERROR: xrandr output not understood"
    exit
fi

CHECK=`echo $VALS | sed -e "s/.* 0 0 //" | wc -w`
if [ "$CHECK" = "4" ]; then
    m1s=`expr 0`
    m1f=`expr 3`
    m2s=`expr 4`
    m2f=`expr 7`
elif [ "$CHECK" = "0" ]; then
    m1s=`expr 4`
    m1f=`expr 7`
    m2s=`expr 0`
    m2f=`expr 3`
fi

i=`expr 0`
for val in $VALS
do
    if [ $i -ge $m1s -a $i -le $m1f ]; then
        j=`expr $i - $m1s`
        if [ $j -eq 0 ]; then
            MON1W=$val
        elif [ $j -eq 1 ]; then
            MON1H=$val
        elif [ $j -eq 2 ]; then
            MON1X=$val
        elif [ $j -eq 3 ]; then
            MON1Y=$val
        fi
    fi
    if [ $i -ge $m2s -a $i -le $m2f ]; then
        j=`expr $i - $m2s`
        if [ $j -eq 0 ]; then
            MON2W=$val
        elif [ $j -eq 1 ]; then
            MON2H=$val
        elif [ $j -eq 2 ]; then
            MON2X=$val
        elif [ $j -eq 3 ]; then
            MON2Y=$val
        fi
    fi
    i=`expr $i + 1`
done

if [ $MON = "left" ]; then
    H=$MON1H
    W=$MON1W
    X=$MON1X
    Y=$MON1Y
else
    H=$MON2H
    W=$MON2W
    X=$MON2X
    Y=$MON2Y
fi

echo "Screen Resolution $W x $H"

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
