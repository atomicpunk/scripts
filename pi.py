#!/usr/bin/python

import math
import time
import sys
import os
import fcntl
import termios
import struct

def getTerminalSize():
	env = os.environ
	def ioctl_GWINSZ(fd):
		try:
			cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
			'1234'))
		except:
			return
		return cr
	cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
	if not cr:
		try:
			fd = os.open(os.ctermid(), os.O_RDONLY)
			cr = ioctl_GWINSZ(fd)
			os.close(fd)
		except:
			pass
	if not cr:
		cr = (env.get('LINES', 25), env.get('COLUMNS', 80))
	return int(cr[1]), int(cr[0])

def make_pi(base):
	q, r, t, k, m, x = 1, 0, 1, 1, 3, 3
	for j in range(1000000):
		if 4 * q + r - t < m * t:
			yield m
			q, r, t, k, m, x = base*q, base*(r-m*t), t, k, (base*(3*q+r))//t - base*m, x
		else:
			q, r, t, k, m, x = q*k, (2*q+r)*x, t*x, k+1, (q*(7*k+2)+r*x)//(t*x), x+2

def doError(msg, help):
	if(help == True):
		printHelp()
	print('ERROR: %s\n') % msg
	sys.exit()

def printHelp():
	print('Usage: pi.py <options>')
	print('Description:')
	print('  Calculate PI forever in dec, hex, oct, or bin')
	print('Options:')
	print('  -h      Print this help text')
	print('  -dec    Decimal (default)')
	print('  -hex    Hexadecimal')
	print('  -oct    Octal')
	print('  -bin    Binary')
	print('  -sep N  Include a separator every N lines with a count')

if __name__ == '__main__':
	args = iter(sys.argv[1:])
	base = 10
	fmt = '{:1d}'
	sep = 0
	for arg in args:
		if(arg == '-h'):
			printHelp()
			sys.exit()
		elif(arg == '-hex'):
			base = 16
			fmt = '{:1X}'
		elif(arg == '-dec'):
			base = 10
			fmt = '{:1d}'
		elif(arg == '-oct'):
			base = 8
			fmt = '{:1o}'
		elif(arg == '-bin'):
			base = 2
			fmt = '{:1b}'
		elif(arg == '-sep'):
			try:
				val = args.next()
			except:
				doError('No separator row number supplied', True)
			try:
				sep = int(val)
			except:
				doError('This isnt an integer: %s' % val, True)
			if sep < 1:
				doError('The separator needs to be at least 1', True)
		else:
			print('What the hell is this? %s' % arg)
			sys.exit()

	(cols, rows) = getTerminalSize()
	cols -= 10

	digit = 0
	my_array = []
	for i in make_pi(base):
		my_array.append(str(fmt.format(i)))
		digit += 1
		if(digit % cols == 0):
			out = "".join(my_array)
			print("%s : %7d" % (out, digit))
			my_array = []
		if((sep > 0) and digit % (cols*sep) == 0):
			print("-------------------- %7d digits" % digit)
