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

import pygtk
pygtk.require('2.0')
import gtk
import cairo
import sys
import socket
import re

class OpenROV:
	verbose = False
	light = 0
	tilt = 1350
	star = 1500
	vert = 1500
	port = 1500
	vdt = 500
	hdt = 500
	cmdlist = {
		'w' : ';light(255);',
		's' : ';light(128);',
		'x' : ';light(0);',
		'q' : ';tilt(1800);',
		'a' : ';tilt(1350);',
		'z' : ';tilt(1000);',
		'1' : ';thrust(1);',
		'2' : ';thrust(2);',
		'3' : ';thrust(3);',
		'4' : ';thrust(4);',
		'5' : ';thrust(5);',
		'6' : ';thrust(6);',
		'7' : ';thrust(7);',
		'8' : ';thrust(8);',
		'9' : ';thrust(9);',
	}
	arrows = {
		'Up' : False,
		'Down' : False,
		'Left' : False,
		'Right' : False,
		'Page_Up' : False,
		'Page_Down' : False,
	}

	def cmdExec(self, cmd):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			sock.connect(("192.168.1.231", 2323))
			sock.sendall(cmd + "\n")
			ret = sock.recv(1024)
			if(self.verbose):
				print("%s -> %s" % (cmd, ret))
		finally:
			sock.close()
	def update(self, cmd):
		change = False
		m = re.match(r";(?P<name>.*)\((?P<val>.*)\);", cmd)
		n = m.group("name")
		val = int(m.group("val"))
		if(n == "light"):
			if(self.light != val):
				self.light = val
				change = True
		elif(n == "tilt"):
			if(self.tilt != val):
				self.tilt = val
				change = True
		elif(n == "thrust"):
			dT = 64 + pow(2, val);
			dT = max(min(dT, 500), 64);
			self.vdt = self.hdt = dT
		return change
	def key_press_event(self, widget, event):
		key = gtk.gdk.keyval_name(event.keyval)
		if key in self.cmdlist:
			cmd = self.cmdlist[key]
			if(self.update(cmd)):
				self.cmdExec(cmd)
			elif(self.verbose):
				print("%s" % cmd)
		elif key in self.arrows:
			self.arrows[key] = True
			self.thrust()
		return True
	def key_release_event(self, widget, event):
		key = gtk.gdk.keyval_name(event.keyval)
		if key in self.arrows:
			self.arrows[key] = False
			self.thrust()
	def thrust(self):
		f = self.arrows['Up'];
		b = self.arrows['Down'];
		l = self.arrows['Left'];
		r = self.arrows['Right'];
		u = self.arrows['Page_Up'];
		d = self.arrows['Page_Down'];

		# ignore the non-sensical inputs
		if((l+r+f+b > 2) or (l and r) or (f and b) or (u and d)):
			return

		vert = star = port = 1500
		if(u): vert -= self.vdt
		if(d): vert += self.vdt
		if(l and not r and not f and not b):
			port -= self.hdt
			star += self.hdt
		elif(not l and r and not f and not b):
			port += self.hdt
			star -= self.hdt
		elif(l and not r and f and not b):
			star += self.hdt
		elif(not l and r and f and not b):
			port += self.hdt
		elif(l and not r and not f and b):
			star -= self.hdt
		elif(not l and r and not f and b):
			port -= self.hdt
		elif(not l and not r and f and not b):
			port += self.hdt
			star += self.hdt
		elif(not l and not r and not f and b):
			port -= self.hdt
			star -= self.hdt

		if(vert == self.vert and star == self.star and port == self.port):
			return

		self.vert = vert
		self.star = star
		self.port = port
		self.cmdExec(";go(%d,%d,%d);" % (star, vert, port))

openrov = OpenROV()

def quit(widget):
	gtk.main_quit()

def printHelp():
	global celestron

	print("")
	print("OpenROV Client")
	print("Usage: openrov-client.py <options>")
	print("")
	print("Description:")
	print("  Controls an OpenROV device via an ethernet connection")
	print("")
	print("Options:")
	print("  -h           Print this help text")
	print("  -v               Verbose print")
	print("")
	return True

def doError(msg, help):
	print("ERROR: %s") % msg
	if(help == True):
		printHelp()
	sys.exit()

def transparent_expose(widget, event):
	cr = widget.window.cairo_create()
	cr.set_operator(cairo.OPERATOR_CLEAR)
	region = gtk.gdk.region_rectangle(event.area)
	cr.region(region)
	cr.fill()
	return False

if __name__ == "__main__":
	args = iter(sys.argv[1:])
	for arg in args:
		if(arg == "-h"):
			printHelp()
			sys.exit()
	 	elif(arg == "-v"):
			openrov.verbose = True
		else:
			doError("Invalid argument: "+arg, True)

	openrov.cmdExec("allstop")
	window = gtk.Window(gtk.WINDOW_TOPLEVEL)
	window.set_title("OpenROV")
	window.set_resizable(False)
	window.connect("destroy", quit)
	window.connect("key_press_event", openrov.key_press_event)
	window.connect("key_release_event", openrov.key_release_event)
	window.set_flags(gtk.SENSITIVE)
	window.set_border_width(0)
	window.set_size_request(450, 250)
	window.set_keep_above(True)

	screen = window.get_screen()
	rgba = screen.get_rgba_colormap()
	window.set_colormap(rgba)
	window.set_app_paintable(True)
	window.connect("expose-event", transparent_expose)

	window.show()
	gtk.main()
