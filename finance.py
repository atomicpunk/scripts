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
from datetime import datetime
import ystockquote

# scottrade or other transaction data file in CSV format
target = ''
verbose = False

class Stock:
	name = ''
	cost = 0.0
	value = 0.0
	price = 0.0
	quantity = 0.0
	def __init__(self, sym):
		self.name = sym
	def getPrice(self):
		global verbose
		if self.name == 'Cash':
			return
		if verbose:
			print("PRICE GET: %s" % (self.name))
		ret = ystockquote.get_price(self.name)
		self.price = float(ret)
		if verbose:
			print("PRICE RCV: %s $%.2f" % (self.name, self.price))

class Portfolio:
	stocklist = dict()
	def transaction(self, t):
		if t.symbol not in self.stocklist:
			self.stocklist[t.symbol] = Stock(t.symbol)
		stock = self.stocklist[t.symbol]
		if t.action in ['Dividend Reinvest', 'Buy', 'Sell']:
			stock.quantity += t.quantity
		if t.action in ['Buy', 'Sell']:
			stock.value += t.amount
		if t.action == 'Buy':
			stock.cost -= t.amount
	def getStockPrices(self):
		for s in self.stocklist:
			stock = self.stocklist[s]
			if s == 'Cash' or stock.quantity == 0.0:
				continue
			stock.getPrice()
	def show(self):
		print('')
		print(' COMPLETED TRANSACTIONS')
		print('---------------------------------------------')
		print(' NAME      QTY       COST     PROFIT  RETURN')
		print('---------------------------------------------')
		cost = value = 0.0
		for s in self.stocklist:
			stock = self.stocklist[s]
			if s == 'Cash' or stock.quantity > 0.0:
				continue
			print("%5s %8.3f %10s %10s %6.2f%%" % \
				(s, stock.quantity, 
				'$%.2f'%stock.cost,
				'$%.2f'%stock.value,
				100.0*stock.value/stock.cost
				))
			value += stock.value
			cost += stock.cost
		print('---------------------------------------------')
		print("TOTAL          %10s %10s %6.2f%%" % \
			('$%.2f'%cost, '$%.2f'%value, 100.0*value/cost))
		print('')
		print(' CURRENT INVESTMENTS')
		print('----------------------------------------------------------------')
		print(' NAME      QTY  PRICE        COST      VALUE     PROFIT  RETURN')
		print('----------------------------------------------------------------')
		profit = cost = value = 0.0
		for s in self.stocklist:
			stock = self.stocklist[s]
			if s == 'Cash' or stock.quantity == 0.0:
				continue
			v = stock.quantity*stock.price
			p = (stock.quantity*stock.price)-stock.cost
			print("%5s %8.3f %7s %10s %10s %10s %6.2f%%" % \
				(s, stock.quantity,
				'$%.2f'%stock.price,
				'$%.2f'%stock.cost,
				'$%.2f'%(stock.quantity*stock.price),
				'$%.2f'%((stock.quantity*stock.price)-stock.cost),
				100.0*((v/stock.cost)-1),
				))
			value += v
			profit += p
			cost += stock.cost
		print('---------------------------------------------------------------')
		print("TOTAL                  %10s %10s %10s %6.2f%%" % \
			('$%.2f'%cost, '$%.2f'%value, '$%.2f'%profit, 100.0*((value/cost)-1)))
		print('')

portfolio = Portfolio()

class Transaction:
	first = True
	fields = [
		'Symbol', 'Quantity', 'Price', 'Action', 'TradeDate', 'SettledDate',
		'Interest', 'Amount', 'Commission', 'Fees', 'CUSIP', 'Description',
		'ActionId', 'TradeNumber', 'RecordType', 'TaxLotNumber'
	]
	data = []
	symbol = ''
	quantity = 0.0
	price = 0.0
	action = ''
	date = 0
	amount = 0.0
	comm = 0.0
	fees = 0.0
	def __init__(self, line, count):
		line = line.replace('\r\n', '')
		self.data = line.split(',')
		self.symbol = self.val('Symbol').replace('.', '')
		self.quantity = float(self.val('Quantity'))
		self.price = float(self.val('Price'))
		self.action = self.val('Action')
		ds = self.val('TradeDate')
		m = re.match('(?P<m>[0-9]*)/(?P<d>[0-9]*)/(?P<y>[0-9]*)', ds)
		if not m:
			doError('Bad date format %s' % ds, False)
		self.date = datetime(int(m.group('y')), int(m.group('m')),
			int(m.group('d')), 0, 0, 0, 999999-count)
		self.amount = float(self.val('Amount'))
		self.fees = float(self.val('Fees'))
		self.comm = float(self.val('Commission'))
	def val(self, name):
		if name not in self.fields:
			return ''
		i = self.fields.index(name)
		return self.data[i]
	def show(self):
		if Transaction.first:
			print('-----------------------------------------------------------------------')
			print('    date   name             action      qty   price     amount    comm')
			print('-----------------------------------------------------------------------')
			Transaction.first = False
		print('%s  %5s %18s %8.3f %7s %10s %7s' % \
			(self.date.strftime('%m/%d/%y'), self.symbol, self.action, self.quantity,
			'$%.2f' % (self.price),
			'$%.2f' % (self.amount),
			'$%.2f' % (self.comm)
			))

def parseStockTransactions(file):
	global verbose, target
	count = 0
	list = dict()
	fp = open(file, 'r')
	for line in fp:
		if count == 0:
			count = 1
			continue
		t = Transaction(line, count)
		if target and t.symbol != target:
			continue
		count += 1
		list[t.date] = t
	for d in sorted(list.keys()):
		t = list[d]
		if verbose:
			t.show()
		portfolio.transaction(t)

# Function: printHelp
# Description:
#	 print out the help text
def printHelp():
	print('')
	print('Finance')
	print('Usage: finance <options>')
	print('')
	print('Description:')
	print('  Calculate stock performance')
	print('Options:')
	print('  [general]')
	print('    -h          Print this help text')
	print('    -v          Print verbose output')
	print('    -s <symbol> Focus on one stock')
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
	for arg in args:
		if(arg == '-h'):
			printHelp()
			sys.exit()
		elif(arg == '-v'):
			verbose = True
		elif(arg == '-s'):
			try:
				val = args.next()
			except:
				doError('No stock symbol supplied', True)
			target = val
		else:
			doError('Invalid argument: '+arg, True)

	home = os.environ['HOME']+'/.finance/'
	parseStockTransactions(home+'mystocktransactions.csv')
	portfolio.getStockPrices()
	portfolio.show()
