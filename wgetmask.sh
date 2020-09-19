#!/bin/sh

if [ $# -lt 2 ]; then
	echo "Usage: $0 [URL] [FILEMASK]"
	exit
fi

wget -r --no-parent -A $2 -e robots=off $1
