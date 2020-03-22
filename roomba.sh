#!/bin/sh

NODEPATH="/home/tebrandt/workspace/node_modules/dorita980"

printUsage() {
	echo "USAGE: kernelbuild.sh command"
	echo "COMMANDS:"
	echo " status - roomba status info"
	echo "  clean - start a clean cycle"
	echo "  start - start a clean"
	echo "   stop - stop a clean"
	echo "  pause - pause clean"
	echo " resume - resume clean"
	echo "   dock - return home"
	exit
}

if [ $# -lt 1 ]; then
	printUsage
else
	if [ $1 = "status" ]; then
		$NODEPATH/status.js
		exit
	elif [ $1 = "start" -o $1 = "clean" -o $1 = "pause" -o $1 = "stop" -o $1 = "resume" -o $1 = "dock" ]; then
		$NODEPATH/command.js $1
		exit
	else
		echo "\nUNKNOWN COMMAND: $1\n"
		printUsage
	fi
fi
