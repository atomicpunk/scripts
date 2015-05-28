#!/bin/sh

CURR=`cat /proc/cmdline | awk '{print $1}' | sed "s/.*vmlinuz/linux-image/"`

listKernels() {
	KERNELS=`dpkg -l | grep linux-image | grep -v -e linux-image-generic -e extra | awk '{print $2}'`
	for k in $KERNELS; do
		VERSION=`echo $k | sed "s/linux-image-//"`
		echo "$VERSION"
		PACKAGES=`dpkg -l | grep $VERSION | grep -v linux-libc-dev | awk '{print $2}'`
		for p in $PACKAGES; do
			echo "\t$p"
		done
	done
}

cleanKernels() {
	KERNELS=`dpkg -l | grep linux-image | grep -v -e linux-image-generic -e extra | awk '{print $2}'`
	for k in $KERNELS; do
		VERSION=`echo $k | sed "s/linux-image-//"`
		read -r -p "Remove kernel $VERSION? [y/N] " response
		if [ "$response" != 'y' ]; then
			continue
		fi
		echo "Removing packages for kernel $VERSION"
		PACKAGES=`dpkg -l | grep $VERSION | grep -v linux-libc-dev | awk '{print $2}'`
		for p in $PACKAGES; do
			sudo dpkg --purge $p
		done
	done
}

printUsage() {
	echo "USAGE: kernelclean.sh command <args>"
	echo "COMMANDS:"
	echo "  list - list all installed kernel packages"
	echo "  clean - select which kernels to remove"
	exit
}

if [ $# -lt 1 ]; then
	printUsage
else
	if [ "$1" = "list" ]; then
		listKernels
		exit
	elif [ "$1" = "clean" ]; then
		cleanKernels
		exit
	else
		echo "\nUNKNOWN COMMAND: $1\n"
		printUsage
	fi
fi

CHECK=`dpkg -l $CURR`
if [ -z "$CHECK" ]; then
	echo "$CURR not installed"
	exit
fi
