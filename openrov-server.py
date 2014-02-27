#!/usr/bin/python

#
# Copyright 2012 Todd Brandt <tebrandt@frontier.com>
#
# This program is free software; you may redistribute it and/or modify it
# under the same terms as Perl itself.
# utility to organize media collections
# Copyright (C) 2012 Todd Brandt <tebrandt@frontier.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import sys
import time
import serial
import SocketServer

class OpenROV:
	verbose = False
	devpath = "/dev/ttyO1"
	fp = 0
	def __init__(self):
		self.fp = serial.Serial(
			port=self.devpath,\
			baudrate=115200,\
			parity=serial.PARITY_NONE,\
			stopbits=serial.STOPBITS_ONE,\
			bytesize=serial.EIGHTBITS,\
			timeout=0)
		self.allstop()
		# blink the lights 3 times to announce server start
		for i in [0,1,2]:
			self.cmdExec(";light(255);")
			time.sleep(0.2)
			self.cmdExec(";light(0);")
			time.sleep(0.2)
	def allstop(self):
		self.cmdExec(";tilt(1350);")
		self.cmdExec(";go(1500,1500,1500);")
		self.cmdExec(";light(0);")
	def cmdCheck(self, cmd):
		if(cmd == "allstop"):
			return True
		if(len(cmd) < 3 or cmd[0] != ';' or cmd[-1] != ';'):
			return False
		return True
	def cmdExec(self, cmd):
		if(cmd == "allstop"):
			self.allstop()
		else:
			self.fp.write(cmd)

class MyTCPHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		global openrov

		self.data = self.request.recv(1024).strip()
		if(openrov.verbose):
			print("%s: %s" % (self.client_address[0], self.data))
		ret = "success"
		if(openrov.cmdCheck(self.data)):
			openrov.cmdExec(self.data)
		else:
			ret = "bad command"
		self.request.sendall(ret)

def printHelp():
	print("")
	print("OpenROV Server")
	print("Usage: openrov-server.py <options>")
	print("")
	print("Description:")
	print("  Runs on the OpenROV device and handles commands from the client")
	print("")
	print("Options:")
	print("  -h               Print this help text")
	print("  -v               verbose print")
	print("")
	return True

def doError(msg, help):
	print("ERROR: %s") % msg
	if(help == True):
		printHelp()
	sys.exit()

if __name__ == "__main__":
	args = iter(sys.argv[1:])
	v = False
	for arg in args:
		if(arg == "-h"):
			printHelp()
			sys.exit()
		elif(arg == "-v"):
			v = True
		else:
			doError("Invalid argument: "+arg, True)

	openrov = OpenROV()
	openrov.verbose = v
	server = SocketServer.TCPServer(("0.0.0.0", 2323), MyTCPHandler)
	server.serve_forever()
