#!/usr/bin/python

import sys
import os
import re
import platform
import string
import struct
from datetime import datetime, timedelta

matchcount = 0
def findPattern(pat, output):
	global matchcount

	matchcount = 0
	fp = open('/media/saturn/bee.fa', 'r')
	patlen = len(pat)
	queue = ''
	l = 0
	start = 0
	for rawline in fp:
 		if 'Group' in rawline:
			continue
		line = rawline.strip()
		while l < patlen:
			queue += line
			l += len(line)
		i = string.find(queue, pat, 0) 
		while i >= 0:
			matchcount += 1
			if output:
				print("%s : %d" % (pat, start+i))
			i = string.find(queue, pat, i+1)
		queue = queue[1-patlen:]
		start += l - patlen + 1
		l = patlen - 1
	fp.close()

def findChar(pat):
	global matchcount

	matchcount = 0
	fp = open('/media/saturn/bee.fa', 'r')
	for rawline in fp:
 		if 'Group' in rawline:
			continue
		line = rawline.strip()
		matchcount += string.count(line, pat[0])
	fp.close()

def compute(val, size):
	i = 0
	pat = ''
	bp = ['A', 'T', 'G', 'C']
	while i < size:
		num = (val >> (2*i)) & 3
		pat += bp[num]
		i += 1
	return pat

def combinations(size):
	global matchcount

	output = dict()
	for i in range(pow(4, size)):
		pat = compute(i, size)
		if len(pat) > 1:
			findPattern(pat, False)
		else:
			findChar(pat)
		line = matchcount*100/1600000
		temp = ''
		for j in range(line):
			temp += '-'
		out = "%s : %9d %s>" % (pat, matchcount, temp)
		output[matchcount] = out
		print '*************************'
		for mc in sorted(output, reverse=True):
			print output[mc]

def doError(msg, help):
	if(help == True):
		printHelp()
	print('ERROR: %s\n') % msg
	sys.exit()

def printHelp():
	print('Usage: bee <options>')
	print('Description:')
	print('  This tool reads the bee genome and finds patterns')
	print('Options:')
	print('  -h                 Print this help text')
	print('  -pattern string    Find a string of ATCGs in the genome')
	print('  -action string     Perform an action on the pattern (find, count)')
	print('  -compute size      Search for every combination of <size> letters')

if __name__ == '__main__':
	args = iter(sys.argv[1:])

	pattern = ''
	action = ''

	for arg in args:
		if(arg == '-h'):
			printHelp()
			sys.exit()
		elif(arg == '-pattern'):
			try:
				val = args.next()
			except:
				doError('No pattern supplied', True)
			pattern = val
		elif(arg == '-action'):
			try:
				val = args.next()
			except:
				doError('No action supplied', True)
			action = val
		elif(arg == '-compute'):
			try:
				val = args.next()
			except:
				doError('No compute supplied', True)
			val = int(val)
			if val < 13:
				combinations(val)
			sys.exit()
		else:
			doError('Invalid argument: '+arg, True)

	if action not in ['find', 'count']:
		doError('bad action', True)
	if pattern != '':
		if len(pattern) > 1:
			findPattern(pattern, action=='find')
		else:
			findChar(pattern)

	if action == 'count':
		print("%s found %d times" % (pattern, matchcount))
