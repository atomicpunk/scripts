#!/usr/bin/python

#
# Copyright 2018 Todd Brandt <tebrandt@frontier.com>
#
# This program is free software; you may redistribute it and/or modify it
# under the same terms as Perl itself.
#    utility to organize media collections
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

import sys
import os
import shutil
import string
import re
from subprocess import call, Popen, PIPE

def displayGeometry():
	out = []
	fp = Popen(['xrandr', '-q'], stdout=PIPE).stdout
	for line in fp:
		if ' connected' not in line:
			continue
		primary = True if ' primary' in line else False
		for i in line.split():
			m = re.match('^(?P<w>[0-9]*)x(?P<h>[0-9]*)\+(?P<x>[0-9]*)\+(?P<y>[0-9]*)$', i)
			if not m:
				continue
			w, h, x, y = m.groups()
			if primary:
				maxrow = 54.0
			else:
				maxrow = 56.0
			out.append((210.0, maxrow, int(w), int(h), int(x), int(y)))
			break
	fp.close()
	return out

def windowGeometry(info, count):
	out = []
	for dpy in info:
		c, r, w, h, x, y = dpy
		if count == 6:
			out.append(( c, r, w, h, w/3, 8*h/17,         x,       y ))
			out.append(( c, r, w, h, w/3, 8*h/17,   x+(w/3),       y ))
			out.append(( c, r, w, h, w/3, 8*h/17, x+(2*w/3),       y ))
			out.append(( c, r, w, h, w/3, 8*h/17,         x, y+(h/2) ))
			out.append(( c, r, w, h, w/3, 8*h/17,   x+(w/3), y+(h/2) ))
			out.append(( c, r, w, h, w/3, 8*h/17, x+(2*w/3), y+(h/2) ))
		elif count == 5:
			out.append(( c, r, w, h, w/2, 8*h/17,         x,       y ))
			out.append(( c, r, w, h, w/2, 8*h/17,   x+(w/2),       y ))
			out.append(( c, r, w, h, w/3, 8*h/17,         x, y+(h/2) ))
			out.append(( c, r, w, h, w/3, 8*h/17,   x+(w/3), y+(h/2) ))
			out.append(( c, r, w, h, w/3, 8*h/17, x+(2*w/3), y+(h/2) ))
		elif count == 4:
			out.append(( c, r, w, h, w/2, 8*h/17,         x,       y ))
			out.append(( c, r, w, h, w/2, 8*h/17,   x+(w/2),       y ))
			out.append(( c, r, w, h, w/2, 8*h/17,   x+(w/2), y+(h/2) ))
			out.append(( c, r, w, h, w/2, 8*h/17,         x, y+(h/2) ))
		elif count == 3:
			out.append(( c, r, w, h, w/3,      h,         x,       y ))
			out.append(( c, r, w, h, w/3,      h,   x+(w/3),       y ))
			out.append(( c, r, w, h, w/3,      h, x+(2*w/3),       y ))
		elif count == 2:
			out.append(( c, r, w, h, w/2,      h,         x,       y ))
			out.append(( c, r, w, h, w/2,      h,   x+(w/2),       y ))
		else:
			out.append(( c, r, w, h,   w,      h,         x,       y ))
	return out

def termGeometry(info):
	out = []
	for win in info:
		maxcol, maxrow, dw, dh, w, h, x, y = win
		col = int(maxcol * float(w) / float(dw))
		row = int(maxrow * float(h) / float(dh))
		out.append((col, row, x, y))
	return out

def printHelp():
	print('')
	print('Multiterm')
	print('Usage: multiterm <count>')
	print('')
	print('Description:')
	print('  Open multiple terminal windows using maximum screen space.')
	print('  Count is number of windows to open per display.')
	print('  Tool assumes user is running gnome-panel so primary screen is shorter.')
	print('')
	return True

def doError(msg):
	print('ERROR: %s\n') % msg
	sys.exit()

# ----------------- MAIN --------------------
# exec start (skipped if script is loaded as library)
if __name__ == '__main__':

	if len(sys.argv) < 2:
		printHelp()
		sys.exit()

	term_count = 1
	try:
		term_count = int(sys.argv[1])
	except:
		printHelp()
		doError('Invalid count: %s' % sys.argv[1])
	if term_count < 1 or term_count > 6:
		doError('count must be between 1 and 6')

	disp_geom = displayGeometry()
	wind_geom = windowGeometry(disp_geom, term_count)
	term_geom = termGeometry(wind_geom)
	for g in term_geom:
		call(['gnome-terminal', '--geometry=%dx%d+%d+%d' % g])
