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
import argparse
from datetime import datetime, timedelta
import yqd

verbose = False
ameritradeids = []

class Stock:
	name = ''
	date = 0
	iprice = 0.0
	cost = 0.0
	value = 0.0
	price = 0.0
	quantity = 0.0
	ownedfor = 0.0
	transfer = False
	def __init__(self, sym, d, ip):
		self.name = sym
		self.date = d
		self.ownedfor = float((datetime.now()-d).days) / 365.25
		self.iprice = ip
	def getPrice(self):
		global verbose
		if self.name == 'Cash':
			return
		if verbose:
			print("PRICE GET: %s" % (self.name))
		day1 = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
		day2 = datetime.today().strftime('%Y%m%d')
		ret = yqd.load_yahoo_quote(self.name, day1, day2)[-2].split(',')[4]
		self.price = float(ret)
		if verbose:
			print("PRICE RCV: %s $%.2f" % (self.name, self.price))

class Portfolio:
	networth = 0.0
	stocklist = dict()
	def stockTransaction(self, t):
		if not t.symbol:
			return
		if t.symbol not in self.stocklist:
			self.stocklist[t.symbol] = Stock(t.symbol, t.date, t.price)
		stock = self.stocklist[t.symbol]
		if t.action == 'Split':
			stock.iprice *= stock.quantity / (t.quantity + stock.quantity)
		if t.action in ['Dividend Reinvest', 'Buy', 'Sell', 'Split']:
			stock.quantity += t.quantity
		if t.action in ['Buy', 'Sell']:
			stock.value += t.amount
		if t.action == 'Buy':
			stock.cost -= t.amount
		if t.action == 'Transfer':
			if not stock.transfer:
				stock.quantity = t.quantity
			else:
				stock.quantity += t.quantity
			stock.transfer = True
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
			if s == 'Cash' or stock.quantity > 0.0 or stock.cost == 0.0:
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
		div = '-----------------------------------------------------------------------------------------------------'
		print div
		print(' NAME       PDATE      AGE      QTY   PRICE       COST      VALUE     PROFIT  RETURN  AVGRET  CHANGE')
		print div
		profit = cost = value = 0.0
		for s in self.stocklist:
			stock = self.stocklist[s]
			if s == 'Cash' or stock.quantity == 0.0:
				continue
			v = stock.quantity * stock.price
			p = v - stock.cost
			ret = 100.0*((v/stock.cost)-1)
			avgret = ret/stock.ownedfor
			change = 100.0*((stock.price/stock.iprice)-1)
			print("%5s  %10s %5s %8.3f %7s %10s %10s %10s %6.2f%% %6.2f%% %6.2f%%" % \
				(s, stock.date.date(),
				'%.2f yrs' % stock.ownedfor,
				stock.quantity,
				'$%.2f' % stock.price,
				'$%.2f' % stock.cost,
				'$%.2f' % v,
				'$%.2f' % p,
				ret,
				avgret,
				change,
				))
			value += v
			profit += p
			cost += stock.cost
		print div
		print("TOTAL                                       %10s %10s %10s %6.2f%%" % \
			('$%.2f'%cost, '$%.2f'%value, '$%.2f'%profit, 100.0*((value/cost)-1)))
		print('')
		portfolio.networth += value

portfolio = Portfolio()

class Transaction:
	first = True
	constants = {
		'scottrade': {
			'fields': [
				'Symbol', 'Quantity', 'Price', 'Action', 'TradeDate', 'SettledDate',
				'Interest', 'Amount', 'Commission', 'Fees', 'ID', 'Description',
				'ActionId', 'TradeNumber', 'RecordType', 'TaxLotNumber'
			],
		},
		'ameritrade': {
			'fields': [
				'TradeDate', 'ID', 'Action', 'Quantity', 'Symbol', 'Price',
				'Commission', 'Amount', 'NetCashBalance', 'Fees', 'ShortTermFee',
				'RedemptionFee', 'SalesCharge'
			]
		}
	}
	data = []
	symbol = ''
	quantity = 0.0
	price = 0.0
	id = ''
	action = ''
	date = 0
	amount = 0.0
	comm = 0.0
	fees = 0.0
	def __init__(self, broker, line, count):
		self.rawline = line.strip()
		self.fields = self.constants[broker]['fields']
		line = line.replace('\r\n', '')
		self.data = line.split(',')
		self.symbol = self.val('Symbol').replace('.', '')
		self.quantity = self.val('Quantity', True)
		self.price = self.val('Price', True)
		self.action = self.val('Action')
		self.id = self.val('ID')
		ds = self.val('TradeDate')
		m = re.match('(?P<m>[0-9]*)/(?P<d>[0-9]*)/(?P<y>[0-9]*)', ds)
		if not m:
			doError('Bad date format %s' % ds)
		self.date = datetime(int(m.group('y')), int(m.group('m')),
			int(m.group('d')), 0, 0, 0, 999999-count)
		self.amount = self.val('Amount', True)
		if self.quantity and self.amount and not self.price:
			self.price = abs(self.amount / self.quantity)
		self.fees = self.val('Fees', True)
		self.comm = self.val('Commission', True)
		if 'ORDINARY DIVIDEND' in self.action and self.quantity > 0:
			self.action = 'Dividend Reinvest'
		elif 'STOCK SPLIT' in self.action and self.quantity > 0:
			self.action = 'Split'
		elif 'TRANSFER OF SECURITY' in self.action and self.quantity > 0:
			self.action = 'Transfer'
		elif 'Bought' in self.action and self.quantity > 0:
			self.action = 'Buy'
		elif 'Sold' in self.action and self.quantity > 0:
			self.action = 'Sell'
	def val(self, name, num=False):
		res = 0 if num else ''
		if name not in self.fields:
			return res
		i = self.fields.index(name)
		if not num:
			return self.data[i]
		if self.data[i]:
			return float(self.data[i])
		return 0
	def show(self):
		if t.action not in ['Dividend Reinvest', 'Buy', 'Sell', 'Split', 'Transfer']:
			return
		if Transaction.first:
			print('----------------------------------------------------------------------------------------')
			print('    date   name                   action                 qty   price     amount    comm')
			print('----------------------------------------------------------------------------------------')
			Transaction.first = False
		print('%s  %5s %35s %8.3f %7s %10s %7s' % \
			(self.date.strftime('%m/%d/%y'), self.symbol, self.action, self.quantity,
			'$%.2f' % (self.price),
			'$%.2f' % (self.amount),
			'$%.2f' % (self.comm)
			))

def parseStockTransactions(list, broker, file):
	changeover = datetime(2018, 2, 2)
	reverse = True if broker == 'ameritrade' else False
	count = 100000 if reverse else 0
	fp = open(file, 'r')
	for line in fp:
		if not line.strip() or 'DATE' in line or 'Symbol' in line or 'END OF FILE' in line:
			continue
		t = Transaction(broker, line, count)
		if broker == 'ameritrade':
			if t.date < changeover:
				continue
			if t.id in ameritradeids:
				continue
			ameritradeids.append(t.id)
		elif broker == 'scottrade':
			if t.date >= changeover:
				continue
		count += -1 if reverse else 1
		list[t.date] = t

def parseBonds(file):
	fp = open(file, 'r')
	value = 0.0
	print('')
	print(' SAVINGS BONDS')
	print('-------------------------------------')
	print('    SERIAL  DENOM    ISSUED    VALUE')
	print('-------------------------------------')
	for line in fp:
		line = line.replace('\n', '')
		f = line.split('\t')
		value += float(f[3])
		print('%s %6s  %8s %8s' % (f[0], f[1], f[2], f[3]))
	print('-------------------------------------')
	print('TOTAL                 %10s' % '$%.2f'%value)
	portfolio.networth += value

def parseOther(file):
	fp = open(file, 'r')
	total = 0.0
	print('')
	print(' %s' % file)
	print('-------------------------------------')
	print('              SOURCE           VALUE')
	print('-------------------------------------')
	for line in fp:
		line = line.replace('\n', '')
		f = line.split('\t')
		value = float(f[1])
		total += value
		print('%20s %15s' % (f[0], '$%.2f'%value))
	print('-------------------------------------')
	print('TOTAL                %10s' % '$%.2f'%total)
	portfolio.networth += total

def doError(msg):
	print('ERROR: %s\n') % msg
	sys.exit()

# ----------------- MAIN --------------------
# exec start (skipped if script is loaded as library)
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Calculate stock performance')
	parser.add_argument('-v', action='store_true',
		help='verbose output')
	parser.add_argument('-d', metavar='date',
		help='date to calculate for')
	args = parser.parse_args()
	date = False
	verbose = args.v
	if args.d:
		try:
			date = datetime.strptime(args.d, '%m/%d/%Y')
		except:
			doError('Invalid date format: %s' % args.d)
	home = os.environ['HOME']+'/.finance/'
	parseBonds(home+'bonds.txt')
	parseOther(home+'cash.txt')
	parseOther(home+'retirement.txt')
	list = dict()
	parseStockTransactions(list, 'scottrade', home+'scottrade.csv')
	for filename in os.listdir(home+'ameritrade'):
		if not re.match('^.*.csv$', filename):
			continue
		file = home+'ameritrade/'+filename
		parseStockTransactions(list, 'ameritrade', file)
	for d in sorted(list.keys()):
		t = list[d]
		if date and t.date > date:
			break
		if verbose:
			t.show()
		portfolio.stockTransaction(t)
	portfolio.getStockPrices()
	portfolio.show()

	print("NET WORTH = $%.2f" % portfolio.networth)
	print('')
