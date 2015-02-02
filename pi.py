#!/usr/bin/python

import math
import time
import sys
import os
import fcntl
import termios
import struct

class ColorWheel:
	nc = '\033[0m'
	dc = {
		0: '\033[0;30m',
		1: '\033[0;34m',
		2: '\033[0;32m',
		3: '\033[0;33m',
		4: '\033[0;31m',
		5: '\033[0;35m',
		6: '\033[0;36m',
		7: '\033[0;37m',
		8: '\033[0;31m',
		9: '\033[0;32m',
		10: '\033[0;33m',
		11: '\033[0;31m',
		12: '\033[0;35m',
		13: '\033[0;36m',
		14: '\033[0;37m',
		15: '\033[0;2m'
	}
	def char(self, i, c):
		return '%s%s%s' % (self.dc[int(i)], c, self.nc)
	def line(self, my_array, fmt):
		out = ''
		for i in my_array:
			out += self.char(i, fmt.format(i))
		return out
colorwheel = ColorWheel()

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
	print('\nUsage: pi.py <options>')
	print('Description:')
	print('  Calculate PI forever in any base from bin to hex')
	print('Options:')
	print('  -h        Print this help text')
	print('  -base 10  Decimal (default)')
	print('  -base 16  Hexadecimal')
	print('  -base 8   Octal')
	print('  -base 2   Binary')
	print('  -base N   2 <= N <= 16')
	print('  -sep N    Include a separator every N lines with a count')
	print('  -cnt      Include a digit count after every line')
	print('  -color    Print digits in color\n')

if __name__ == '__main__':
	basename = {
		2: 'Binary',
		8: 'Octal',
		10: 'Decimal',
		16: 'Hexadecimal'
	}
	args = iter(sys.argv[1:])
	base = 10
	fmt = '{:1d}'
	sep = 0
	cnt = False
	color = False
	for arg in args:
		if(arg == '-h'):
			printHelp()
			sys.exit()
		elif(arg == '-base'):
			try:
				val = args.next()
			except:
				doError('No base number supplied', True)
			try:
				base = int(val)
			except:
				doError('This isnt an integer: %s' % val, True)
			if base < 2 or base > 16:
				doError('The base must be between 2 and 16', True)
			if base > 10:
				fmt = '{:1X}'
			elif base > 8:
				fmt = '{:1d}'
			elif base > 2:
				fmt = '{:1o}'
			else:
				fmt = '{:1b}'
		elif(arg == '-cnt'):
			cnt = True
		elif(arg == '-color'):
			color = True
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

	bn = 'BASE%d' % base
	if base in basename:
		bn = basename[base]
	print('Calculating PI in %s' % bn)

	(cols, rows) = getTerminalSize()
	if cnt:
		cols -= 10

	digit = 0
	my_array = []
	for i in make_pi(base):
		if color:
			my_array.append(i)
		else:
			my_array.append(str(fmt.format(i)))
		digit += 1
		if(digit % cols == 0):
			if color:
				out = colorwheel.line(my_array, fmt)
			else:
				out = "".join(my_array)
			if cnt:
				print("%s : %7d" % (out, digit))
			else:
				print("%s" % (out))
			my_array = []
		if((sep > 0) and digit % (cols*sep) == 0):
			print("-------------------- %7d digits" % digit)
