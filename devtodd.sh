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

POS="all"

getDisplayCount() {
    C=`xrandr | grep "connected.*mm" | sed -e "s/ (.*//;s/.* connected //;s/[x+]/ /g" | awk '{print $3,$4,$1,$2}' | sort | wc -l`
    return $C
}

getDisplay() {
    P=$1
    VALS=`xrandr | grep "connected.*mm" | sed -e "s/ (.*//;s/.* connected //;s/primary//;s/[x+]/ /g" | awk '{print $3,$4,$1,$2}' | sort | head -n$P | tail -n1`
    echo $VALS
    X=`echo $VALS | awk '{print $1}'`
    Y=`echo $VALS | awk '{print $2}'`
    W=`echo $VALS | awk '{print $3}'`
    H=`echo $VALS | awk '{print $4}'`
}

setupDisplay() {
    NUM=$1
    TH=`expr $H / 18`
    TW=`expr $W / 9 / $NUM`
    if [ $NUM -eq 3 ]; then
        TW=`expr $W / 24`
    fi
    TY=$Y
    T1X=`expr $X`
    if [ $NUM -lt 3 ]; then
        T2X=`expr $W / 2 + $X`
    else
        T2X=`expr $W / 3 - 50 + $X`
        T3X=`expr 2 \* $W / 3 - 50 + $X`
    fi

    if [ $NUM -gt 0 ]; then
        gnome-terminal --geometry="$TW"x"$TH"+"$T1X"+"$TY" &
    fi
    if [ $NUM -gt 1 ]; then
        gnome-terminal --geometry="$TW"x"$TH"+"$T2X"+"$TY" &
    fi
    if [ $NUM -gt 2 ]; then
        gnome-terminal --geometry="$TW"x"$TH"+"$T3X"+"$TY" &
    fi
}

TERMS=3
if [ $# -eq 0 -o $# -gt 2 ]; then
    echo "USAGE: $0 \<1/2/3\> \<left/middle/right/all\>"
    exit
elif [ $# -eq 2 ]; then
    if [ "$2" = "left" -o "$2" = "middle" -o "$2" = "right" -o "$2" = "all" ]; then
        POS=$2
    else
        echo "ERROR: left, middle, right, or all displays please"
        exit
    fi
    if [ $1 -eq 1 -o $1 -eq 2 -o $1 -eq 3 ]; then
        TERMS=$1
    else
        echo "ERROR: 1, 2, or 3 terms please"
        exit
    fi
fi

getDisplayCount
DISPLAYS=$?

if [ "$POS" = "left" -o "$POS" = "all" ]; then
    getDisplay 1
    setupDisplay $TERMS
fi
if [ "$POS" = "right" -o "$POS" = "all" ]; then
    getDisplay $DISPLAYS
    setupDisplay $TERMS
fi
if [ $DISPLAYS -gt 2 ]; then
    if [ "$POS" = "middle" -o "$POS" = "all" ]; then
        getDisplay 2
        setupDisplay $TERMS
    fi
fi
