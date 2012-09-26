#!/bin/sh

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

echo "Screen Resolution $MON1W x $MON1H"

TERMH=`expr $MON1H / 18`
TERMW=`expr $MON1W / 24`
TERM1X=`expr 0`
TERM2X=`expr $MON1W / 3 - 50`
TERM3X=`expr 2 \* $MON1W / 3 - 50`

echo "Terminal Dimensions $TERMW"x"$TERMH"

gnome-terminal --geometry="$TERMW"x"$TERMH"+"$TERM1X"+"0"
gnome-terminal --geometry="$TERMW"x"$TERMH"+"$TERM2X"+"0"
gnome-terminal --geometry="$TERMW"x"$TERMH"+"$TERM3X"+"0"
