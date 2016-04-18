#!/usr/bin/python

#
# Copyright 2012 Todd Brandt <tebrandt@frontier.com>
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
from urllib import quote_plus as urlquote
from urllib import urlopen
import urllib
import urllib2
import cookielib
from datetime import datetime

def numTest():
	html = urlopen('http://www.powerball.com/powerball/winnums-text.txt')
	whiteball = {}
	powerball = {}
	total = 0.0
	for line in html:
		m = re.match('(?P<date>[0-9]*/[0-9]*/[0-9]*) *(?P<p1>[0-9]*) *(?P<p2>[0-9]*) *(?P<p3>[0-9]*) *(?P<p4>[0-9]*) *(?P<p5>[0-9]*) *(?P<pb>[0-9]*).*', line)
		if(not m):
			continue
		total += 1
		date = m.group('date')
		wbnums = [int(m.group('p1')),int(m.group('p2')),int(m.group('p3')),int(m.group('p4')),int(m.group('p5'))]
		for i in wbnums:
			if i not in whiteball:
				whiteball[i] = 1
			else:
				whiteball[i] += 1
		pbnum = int(m.group('pb'))
		if pbnum not in powerball:
			powerball[i] = 1
		else:
			powerball[pbnum] += 1
	print '----- White Ball Frequency -----'
	for i in sorted(whiteball, key=whiteball.get, reverse=True):
		print 'WB %02d = %2.2f%%' % (i, 100*float(whiteball[i])/total)
	print '----- Power Ball Frequency -----'
	for i in sorted(powerball, key=powerball.get, reverse=True):
		print 'PB %02d = %2.2f%%' % (i, 100*float(powerball[i])/total)


def getPowerballNumbers(wb, pb):
	html = urlopen('http://www.powerball.com/powerball/winnums-text.txt')
	total = 0
	wins = 0
	high = 0
	for line in html:
		m = re.match('(?P<date>[0-9]*/[0-9]*/[0-9]*) *(?P<p1>[0-9]*) *(?P<p2>[0-9]*) *(?P<p3>[0-9]*) *(?P<p4>[0-9]*) *(?P<p5>[0-9]*) *(?P<pb>[0-9]*).*', line)
		if(not m):
			continue
		total += 1
		date = m.group('date')
		wbnums = [int(m.group('p1')),int(m.group('p2')),int(m.group('p3')),int(m.group('p4')),int(m.group('p5'))]
		pbnum = int(m.group('pb'))
		w = 0
		p = 0
		if pb == pbnum:
			p = 1
		for i in wb:
			if i in wbnums:
				w += 1

		if (w == 0 or w == 1) and p:
			print('%s: $4' % date)
			if high < 4: high = 4
		elif (w == 2 and p) or (w == 3 and not p):
			print('%s: $7' % date)
			if high < 7: high = 7
		elif (w == 3 and p) or (w == 4 and not p):
			print('%s: $100' % date)
			if high < 100: high = 100
		elif w == 4 and p:
			print('%s: $50000' % date)
			if high < 50000: high = 50000
		elif w == 5 and not p:
			print('%s: $1000000' % date)
			if high < 1000000: high = 1000000
		elif w == 5 and p:
			print('%s: GRAND PRIZE' % date)
			high = 150000000
		else:
			continue
		wins += 1

	print('Won %d of %d drawings (1 in %.2f) Highest win was $%d' % (wins, total, float(total)/float(wins), high))

# Function: printHelp
# Description:
#	 print out the help text
def printHelp():
	print('')
	print('Powerball')
	print('Usage: powerball wb1 wb2 wb3 wb4 wb5 pb')
	print('')
	print('Description:')
	print('  Check out powerball wins for a particular set of numbers')
	print('Options:')
	print('  [general]')
	print('    -h          Print this help text')
	print('    -numtest    Print out which numbers are likeliest')
	print('')
	return True

# Function: doError
# Description:
#    generic error function for catastrphic failures
# Arguments:
#    msg: the error message to print
#    help: True if printHelp should be called after, False otherwise
def doError(msg, help):
	if(help == True):
		printHelp()
	print('ERROR: %s\n') % msg
	sys.exit()

# ----------------- MAIN --------------------
# exec start (skipped if script is loaded as library)
if __name__ == '__main__':
	cmd = ''
	cmdarg = ''
	# loop through the command line arguments
	args = iter(sys.argv[1:])
	nums = []
	for arg in args:
		if(arg == '-h'):
			printHelp()
			sys.exit()
		elif(arg == '-numtest'):
			numTest()
			sys.exit()
		else:
			try:
				num = int(arg)
			except:
				doError('Bad Number', True)
			nums.append(num)

	if len(nums) != 6:
		doError('Please supply 6 numbers', True)

	for i in nums[:5]:
		if i < 1 or i > 69:
			doError('Invalid White Ball Number: %d [1 - 69]' % i, False)

	if nums[5] < 1 or nums[5] > 35:
		doError('Invalid Power Ball Number: %d [1 - 35]' % nums[5], False)

	for i in range(0, 5):
		test = nums[0:i] + nums[i+1:5]
		if nums[i] in test:
			doError('Repeat White Ball Number: %d' % nums[i], False)

	getPowerballNumbers(nums[:5], nums[5])
