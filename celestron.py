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
import re
import array
import datetime
import struct
import serial

class Celestron:
	devpath = "/dev/ttyUSB0"
	cmdlist = {
		'test'			: 'Kx',
		'cancel'		: 'M',
		'check-goto'	: 'L',
		'check-align'	: 'J',
		'version-hc'	: 'V',
		'version-azi'	: 'P\x01\x10\xfe\x00\x00\x00\x02',
		'version-alt'	: 'P\x01\x11\xfe\x00\x00\x00\x02',
		'tracking'		: '^T(?P<a>[0-3]{1})$',
		'get-az-alt16'	: 'Z',
		'get-az-alt32'	: 'z',
		'set-az-alt16'	: '^B(?P<a>[0-9,A-F]{4}),(?P<b>[0-9,A-F]{4})$',
		'set-az-alt32'	: '^b(?P<a>[0-9,A-F]{8}),(?P<b>[0-9,A-F]{8})$',
		'get-ra-dec16'	: 'E',
		'get-ra-dec32'	: 'e',
		'set-ra-dec16'	: '^R(?P<a>[0-9,A-F]{4}),(?P<b>[0-9,A-F]{4})$',
		'set-ra-dec32'	: '^r(?P<a>[0-9,A-F]{8}),(?P<b>[0-9,A-F]{8})$',
	}
	fp = 0
	online = False
	atrest = False
	aligning = False
	aligned = False
	version = [0.0, 0.0, 0.0]
	altitude = 90.0
	azimuth = 90.0
	def __init__(self):
		self.fp = serial.Serial(
			port=self.devpath,\
			baudrate=9600,\
			parity=serial.PARITY_NONE,\
			stopbits=serial.STOPBITS_ONE,\
			bytesize=serial.EIGHTBITS,\
			timeout=0)
	def status(self, v):
		r = {False: "NO", True: "YES"}
		res = self.cmdExec(self.cmdlist['test'])
		self.online = False
		if(res == "x"): self.online = True
		if(v): print("  Connection on-line: %s" % r[self.online])
		if(not self.online): return False

		res = self.cmdExec(self.cmdlist['version-hc'])
		tmp = struct.unpack("BB", res)
		self.version[0] = float(tmp[0]) + (float(tmp[1]) / 10.0)
		if(v): print("Hand Control version: %.1f" % self.version[0])

		res = self.cmdExec(self.cmdlist['version-azi'])
		tmp = struct.unpack("BB", res)
		self.version[1] = float(tmp[0]) + (float(tmp[1]) / 10.0)
		if(v): print("   Azi Motor version: %.1f" % self.version[1])

		res = self.cmdExec(self.cmdlist['version-alt'])
		tmp = struct.unpack("BB", res)
		self.version[2] = float(tmp[0]) + (float(tmp[1]) / 10.0)
		if(v): print("   Alt Motor version: %.1f" % self.version[2])

		res = self.cmdExec(self.cmdlist['check-goto'])
		self.atrest = False
		if(res == "0"): self.atrest = True
		if(v): print("  Is machine at rest: %s" % r[self.atrest])

		res = self.cmdExec(self.cmdlist['check-align'])
		self.aligned = self.aligning = False
		val = r[False]
		if(res == "1"):
			self.aligned = True
			val = r[True]
		elif(res == "0"):
			self.aligning = True
			val = "In Progress"
		if(v): print("  Is machine aligned: %s" % val)

		self.getAltAzi()
		if(v):
			print("            Altitude: %.2f deg" % self.altitude)
			print("             Azimuth: %.2f deg" % self.azimuth)
		return True
	def getAltAzi(self):
		res = self.cmdExec(self.cmdlist['get-az-alt32'])
		m = re.match('^(?P<alt>[0-9,A-F]{8}),(?P<azi>[0-9,A-F]{8})$', res)
		if(not m):
			doError("Invalid Altitude/Azimuth data from telescope", False)
		self.altitude = (float(int(m.group("alt"), 16)) / 0x100000000) * 360.0
		self.azimuth = (float(int(m.group("azi"), 16)) / 0x100000000) * 360.0
	def gotoAltAzi(self, alt, azi):
		hexalt = int((alt / 360) * 0x100000000)
		hexazi = int((azi / 360) * 0x100000000)
		cmd = "b%08x,%08x" % (hexalt, hexazi)
		res = self.cmdExec(cmd)
	def cmdName(self, cmd):
		for name in self.cmdlist:
			fmt = self.cmdlist[name]
			if(re.match(fmt, cmd)):
				return name
		return ""
	def cmdExec(self, cmd):
		self.fp.write(cmd)
		res = ""
		while True:
			ch = self.fp.read()
			if(ch == "#"):
				break
			res += ch
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
	print("  -h               Print this help text")
	print("  -cmd rawcmd      Execute a raw command")
	print("  -status          Print the telescope status")
	print("  -cancel          Cancel a goto move, stop the telescope")
	print("  -altazi alt azi  Goto altitude azimuth")
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
		res = celestron.cmdExec(cmd)
		print("Result from '%s' = '%s'" % (cmd, res))
		sys.exit()
 	elif(arg == "-status"):
		celestron.status(True)
		sys.exit()
 	elif(arg == "-cancel"):
		celestron.status(False)
		if(celestron.online):
			celestron.cmdExec(celestron.cmdlist['cancel'])
		else:
			doError("Connection off-line", False)
		sys.exit()
	elif(arg == "-altazi"):
		try: alt = args.next()
		except: doError("No altitude supplied", True)
		try: alt = float(alt)
		except:	doError("Bad altitude, what the hell is this? [%s]" % alt, False)
		try: azi = args.next()
		except: doError("No azimuth supplied", True)
		try: azi = float(azi)
		except: doError("Bad azimuth, what the hell is this? [%s]" % azi, False)
		if(alt < 0 or alt > 180):
			doError("Altitude %.2f is not between 0 and 180" % alt, False)
		if(azi < 0 or azi >= 360):
			doError("Azimuth %.2f is not between 0 and 360" % azi, False)
		celestron.status(False)
		if(celestron.online):
			celestron.gotoAltAzi(alt, azi)
		else:
			doError("Connection off-line", False)
		sys.exit()
	else:
		doError("Invalid argument: "+arg, True)
