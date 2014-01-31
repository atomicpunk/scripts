#!/usr/bin/python

#
# Copyright 2012 Todd Brandt <tebrandt@frontier.com>
#
# This program is free software; you may redistribute it and/or modify it
# under the same terms as Perl itself.
#utility to organize media collections
#Copyright (C) 2012 Todd Brandt <tebrandt@frontier.com>
#
#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along
#with this program; if not, write to the Free Software Foundation, Inc.,
#51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import sys
import os
import string
import tempfile
import re
import array
import datetime
import serial

class Celestron:
	devpath = "/dev/ttyUSB0"
	cmdlist = {
		'test'			: 'Kx',
		'cancel-goto'	: 'M',
		'check-goto'	: 'L',
		'check-align'	: 'J',
		'version'		: 'V',
		'tracking'		: '^T(?P<a>[0-3]{1})$',
		'get-az-alt16'	: 'Z',
		'get-az-alt32'	: 'e',
		'set-az-alt16'	: '^B(?P<a>[0-9,A-F]{4}), (?P<b>[0-9,A-F]{4})$',
		'set-az-alt32'	: '^b(?P<a>[0-9,A-F]{8}),(?P<b>[0-9,A-F]{8})$',
		'get-ra-dec16'	: 'E',
		'get-ra-dec32'	: 'z',
		'set-ra-dec16'	: '^R(?P<a>[0-9,A-F]{4}), (?P<b>[0-9,A-F]{4})$',
		'set-ra-dec32'	: '^r(?P<a>[0-9,A-F]{8}),(?P<b>[0-9,A-F]{8})$',
	}

	fp = 0
	def __init__(self):
		self.fp = serial.Serial(
			port=self.devpath,\
			baudrate=9600,\
			parity=serial.PARITY_NONE,\
			stopbits=serial.STOPBITS_ONE,\
			bytesize=serial.EIGHTBITS,\
			timeout=0)
	def cmdName(self, cmd):
		for name in self.cmdlist:
			fmt = self.cmdlist[name]
			if(re.match(fmt, cmd)):
				return name
		return ""
	def cmdExec(self, name, cmd):
		self.fp.write(cmd)
		res = ""
		while True:
			ch = self.fp.read()
			res += ch
			if(ch == "#"):
				break
		return res

celestron = Celestron()

def printHelp():
	global celestron

	print("")
	print("Celestron Controller")
	print("Usage: celestron.py <options>")
	print("")
	print("Description:")
	print("  Controls a celestron telescope via a serial port")
	print("")
	print("Options:")
	print("    -h            Print this help text")
	print("    -cmd rawcmd   Execute a raw command")
	print("")
	return True

def doError(msg, help):
	print("ERROR: %s") % msg
	if(help == True):
		printHelp()
	sys.exit()

# -- script main --
# loop through the command line arguments
args = iter(sys.argv[1:])
for arg in args:
	if(arg == "-h"):
		printHelp()
		sys.exit()
	elif(arg == "-cmd"):
		try:
			cmd = args.next()
		except:
			doError("No cmd supplied", True)
		name = celestron.cmdName(cmd)
		if(name == ""):
			doError("Invalid command (%s)" % cmd, False)
		print("Issuing %s : '%s' ..." % (name, cmd))
		res = celestron.cmdExec(name, cmd)
		print("Result from '%s' = '%s'" % (cmd, res))
		sys.exit()
	else:
		doError("Invalid argument: "+arg, True)
