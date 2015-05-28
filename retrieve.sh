#!/bin/sh

ADDR="192.168.1.9"
#FOLDERS="closeup garden"
FOLDERS="garden"

for folder in $FOLDERS; do
	REMOTE=`ssh -X $ADDR "cd Pictures/$folder ; ls -1 $folder-??????-??????.jpg"`
	for file in $REMOTE; do
		if [ $folder = "closeup" ]; then
			DIR=`echo $file | sed -e "s/^........//;s/...........$//"`
		else
			DIR=`echo $file | sed -e "s/^.......//;s/...........$//"`
		fi
		if [ ! -d $folder/$DIR ]; then
			mkdir $folder/$DIR
		fi
		if [ ! -e $folder/$DIR/$file ]; then
			HOUR=`echo $file | sed -e "s/........$//"`
			scp $ADDR:Pictures/$folder/$HOUR????.jpg $folder/$DIR/
		fi
	done
done

ROOT=$PWD
for folder in $FOLDERS; do
	REMOTE=`ssh -X $ADDR "cd Pictures/$folder;ls -1 $folder-??????-??????.jpg" | sed "s/[a-z,-]*//;s/-.*//" | uniq | sort`
	echo -n "$folder: "
	echo $REMOTE
	cd $ROOT/$folder
	NAME=$folder
	if [ $folder = "closeup" ]; then
		NAME="cucumbers"
	fi
	movie.sh -t ${NAME}-1day-per-sec -m hourly
	movie.sh -t ${NAME}-12hours-per-sec -m 30min
	movie.sh -t ${NAME}-4hours-per-sec -m 10min
done
