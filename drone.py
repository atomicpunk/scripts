#!/usr/bin/python

#
#    Drone image & video management script
#    Copyright (C) 2015 Todd Brandt <tebrandt@frontier.com>
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
#    required ubuntu packages:
#    sudo apt-get install python-pyexiv2 python-opencv python-matplotlib

import sys
import os
import shutil
import string
import re
import tempfile
from datetime import datetime, timedelta
import time
import cv2
import urllib
import json
import fractions
import geopy
from geopy.distance import vincenty

DISKID = 'drone'

def getTag(indir, tagname):
	import pyexiv2

	for filename in sorted(os.listdir(indir)):
		file = os.path.join(indir, filename)
		if not os.path.isfile(file):
			continue
		meta = pyexiv2.metadata.ImageMetadata(file)
		meta.read()
		try:
			tag = meta.__getitem__(tagname)
		except:
			print("%s: NOT FOUND" % filename)
			continue
		if not tag:
			print("%s: NOT FOUND" % filename)
			continue
		print("%s : %s = %s" % (filename, tagname, tag.value))

def setTag(indir, tagname, tagval):
	import pyexiv2

	for filename in sorted(os.listdir(indir)):
		file = os.path.join(indir, filename)
		if not os.path.isfile(file):
			continue
		meta = pyexiv2.metadata.ImageMetadata(file)
		meta.read()
		try:
			tag = meta.__getitem__(tagname)
		except:
			print("%s: NOT FOUND" % filename)
			continue
		if not tag:
			print("%s: NOT FOUND" % filename)
			continue
		print("%s : %s = %s" % (filename, tagname, tagval))
		if tag.type in ['Short', 'SShort', 'Long']:
			tagval = int(tagval)
		elif tag.type in ['Rational', 'SRational']:
			tagval = float(tagval)
		if tag.value != tagval:
			tag.value = tagval
			meta.__setitem__(tag.key, tag)
			meta.write()

def getFileList(dir, spec, fullpath=True):
	out = []
	for filename in sorted(os.listdir(dir)):
		file = os.path.join(dir, filename)
		if not os.path.isfile(file) or not re.match(spec, filename):
			continue
		if fullpath:
			out.append(file)
		else:
			out.append(filename)
	return out

def fileIndex(dstdir, spec):
	if not os.path.isdir(dstdir):
		return 0
	dstfiles = getFileList(dstdir, spec, False)
	newidx = 0
	for i in dstfiles:
		idx = int(re.match(spec, i).group('idx'))
		if idx >= newidx:
			newidx = idx + 1
	return newidx

def syncVideo(srcdir, dstdir, commit=False):
	spec = '^DJI_(?P<idx>[0-9]*)\.MOV'
	newidx = fileIndex(dstdir, spec)
	srcfiles = getFileList(srcdir, spec, True)
	for srcmov in srcfiles:
		srcsrt = srcmov[:-3]+'SRT'
		dstmov = os.path.join(dstdir, 'DJI_%04d.MOV' % newidx)
		dstsrt = os.path.join(dstdir, 'DJI_%04d.SRT' % newidx)
		if os.path.isfile(dstsrt):
			doError('SRT file collision: %s' % dstsrt)
		if os.path.isfile(dstmov):
			doError('MOV file collision: %s' % dstmov)
		print('Moving: %s -> %s' % (srcmov, dstmov))
		if commit:
			shutil.move(srcmov, dstmov)
		if os.path.isfile(srcsrt):
			print('Moving: %s -> %s' % (srcsrt, dstsrt))
			if commit:
				shutil.move(srcsrt, dstsrt)
		newidx += 1

def syncImages(srcdir, dstdir, commit=False):
	spec = '^DJI_(?P<idx>[0-9]*)\.JPG'
	newidx = fileIndex(dstdir, spec)
	srcfiles = getFileList(srcdir, spec, True)
	for srcjpg in srcfiles:
		dstjpg = os.path.join(dstdir, 'DJI_%04d.JPG' % newidx)
		if os.path.isfile(dstjpg):
			doError('JPG file collision: %s' % dstjpg)
		print('Moving: %s -> %s' % (srcjpg, dstjpg))
		if commit:
			shutil.move(srcjpg, dstjpg)
		newidx += 1

def organizeImages(indir, outdir):
	if not os.path.isdir(outdir):
		doError('%s doesnt exist' % outdir)
	outdir = os.path.join(outdir, 'Pictures')
	if not os.path.isdir(outdir):
		doError('%s doesnt exist' % outdir)
	spec = '^DJI_(?P<idx>[0-9]*)\.JPG'
	jpgfiles = getFileList(indir, spec, True)
	for jpg in jpgfiles:
		info = ImageInfo(jpg)
		if(not info.valid):
			continue
		dstdir = os.path.join(outdir, info.filedir())
		if not os.path.isdir(dstdir):
			os.mkdir(dstdir)
		newidx = fileIndex(dstdir, spec)
		dstjpg = os.path.join(dstdir, 'DJI_%04d.JPG' % newidx)
		print('%s -> %s' % (jpg, dstjpg))
		shutil.move(jpg, dstjpg)

class ImageInfo:
	taginfo = {
		'author' : 'Exif.Image.Artist',
		'model' : 'Exif.Image.Model',
		'timestamp' : 'Exif.Image.DateTime',
		'width' : 'Exif.Photo.PixelXDimension',
		'height' : 'Exif.Photo.PixelYDimension',
		'lat_ref' : 'Exif.GPSInfo.GPSLatitudeRef',
		'lon_ref' : 'Exif.GPSInfo.GPSLongitudeRef',
		'latitude' : 'Exif.GPSInfo.GPSLatitude',
		'longitude' : 'Exif.GPSInfo.GPSLongitude',
		'altitude' : 'Exif.GPSInfo.GPSAltitude',
		'exposure' : 'Exif.Photo.ExposureTime',
		'fnum' : 'Exif.Photo.FNumber',
		'ISO' : 'Exif.Photo.ISOSpeedRatings',
		'focallength' : 'Exif.Photo.FocalLength',
	}
	tagdata = {}
	locations = {
		'toddshouse'	: (45.518269,122.9021689),
		'amberglen'  	: (45.530296,122.884092),
		'skylineblvd'	: (45.520772,122.741428),
		'cpassNskyline'	: (45.605270,122.861583),
	}
	valid = True
	def __init__(self, file):
		import pyexiv2

		meta = pyexiv2.metadata.ImageMetadata(file)
		self.size = ''
		try:
			meta.read()
		except:
			self.tagdata = {}
			self.valid = False

		for name in self.taginfo:
			try:
				tag = meta.__getitem__(self.taginfo[name])
				self.tagdata[name] = tag.value
			except:
				pass

		# calculate image size and ditch the height/width
		if 'height' in self.tagdata and 'width' in self.tagdata:
			self.tagdata['size'] = '%d x %d' % (self.tagdata['width'], self.tagdata['height'])
			del self.tagdata['height']
			del self.tagdata['width']

		# convert these values from fraction to float
		for tag in ['altitude', 'fnum']:
			if tag in self.tagdata:
				val = self.tagdata[tag]
				if type(val) is fractions.Fraction:
					self.tagdata[tag] = float(val)

		if 'latitude' in self.tagdata and 'lat_ref' in self.tagdata and 'longitude' in self.tagdata and 'lon_ref' in self.tagdata:
			lat = self.tagdata['latitude']
			lon = self.tagdata['longitude']
			dirlat = self.tagdata['lat_ref']
			dirlon = self.tagdata['lon_ref']
			self.tagdata['latitude'] = '%ddeg %d\' %f\" %s' % (lat[0], lat[1], lat[2], dirlat)
			self.tagdata['longitude'] = '%ddeg %d\' %f\" %s' % (lon[0], lon[1], lon[2], dirlon)
			del self.tagdata['lat_ref']
			del self.tagdata['lon_ref']
			gps = (float(lat[0] + (lat[1]/60) + (lat[2]/3600)), \
					float(lon[0] + (lon[1]/60) + (lon[2]/3600)))
			self.tagdata['place'] = self.location(gps)

	def show(self):
		for name in sorted(self.tagdata):
			title = name[0].upper()+name[1:]
			print('\t  %12s: %s' % (title, self.tagdata[name]))

	def location(self, gps):
		for name in self.locations:
			dist = vincenty(gps, self.locations[name]).miles
			if dist <= 0.1:
				return name
		return 'unknown'

	def known(self):
		if 'place' not in self.tagdata or self.tagdata['place'] == 'unknown':
			return False
		return True

	def filedir(self):
		if not self.known():
			return ''
		alt = int(round(self.tagdata['altitude']))
		if(alt%10 == 9):
			alt += 1
		exp1 = self.tagdata['exposure'].numerator
		exp2 = self.tagdata['exposure'].denominator
		ratio = float(exp1)/float(exp2)
		if ratio > 0.1:
			exp = '%ds%d' % (exp1, exp2)
		else:
			exp = '%d' % (int(1/ratio))
		name = '%s_%03dm_iso%d_%s' % (self.tagdata['place'], alt, self.tagdata['ISO'], exp)
		return name

def getImageMetadata(indir, full=True):
	jpgfiles = getFileList(indir, '^DJI_(?P<idx>[0-9]*)\.JPG', True)
	for jpg in jpgfiles:
		info = ImageInfo(jpg)
		if(info.valid):
			print('%s -> %s' % (jpg, info.filedir()))
			if full:
				info.show()

def getImageMetadataAll(indir, full=True):
	jpgfiles = getFileList(indir, '.*.JPG', True)
	jpgfiles += getFileList(indir, '.*.jpg', True)
	for jpg in jpgfiles:
		info = ImageInfo(jpg)
		if(info.valid):
			print('%s -> %s' % (jpg, info.filedir()))
			if full:
				info.show()

def getCardPath():
	fp = os.popen('mount')
	out = ''
	for line in fp:
		if line.find(DISKID) < 0:
			continue
		for i in line.split():
			if i.find(DISKID) >= 0:
				fp.close()
				out = os.path.join(i, 'DCIM/100MEDIA')
				break
		break
	fp.close()
	if out and not os.path.isdir(out):
		doError('%s not found' % out)
	return out

# Function: printHelp
# Description:
#	 print out the help text
def printHelp():
	print('')
	print('Drone Utility')
	print('Usage: drone.py <options> command')
	print('')
	print('Description:')
	print('   Utilities for dealing with Drone media')
	print('Options:')
	print('   -h             Print this help text')
	print('   -i <dirname>   Input file folder')
	print('   -o <dirname>   Output file folder')
	print('   -n             dryrun, dont commit changes')
	print('Commands:')
	print('   info      : print basic metadata for drone image files')
	print('   infoall   : print basic metadata for all jpg image files')
	print('   sync      : copy all .MOV, .SRT, and .JPG files from card')
	print('   organize  : distribute the images based on location, exposure, and altitude')
	print('')
	return True

# Function: doError
# Description:
#    generic error function for catastrphic failures
# Arguments:
#    msg: the error message to print
#    help: True if printHelp should be called after, False otherwise
def doError(msg, help=False):
	if(help == True):
		printHelp()
	print('ERROR: %s\n') % msg
	sys.exit()

# Function: getArgInt
# Description:
#    pull out an integer argument from the command line
def getArgInt(name, args):
	try:
		arg = args.next()
	except:
		doError(name+': no argument supplied', True)
	try:
		val = int(arg)
	except:
		doError(name+': non-integer value given', True)
	return val

# Function: getArgStr
# Description:
#    pull out a string argument from the command line
def getArgStr(name, args):
	try:
		arg = args.next()
	except:
		doError(name+': no argument supplied', True)
	return arg

# ----------------- MAIN --------------------
# exec start (skipped if script is loaded as library)
if __name__ == '__main__':

	cmd = ''
	indir = ''
	outdir = '/media/whore/Archimedes/'
	commit = True
	# loop through the command line arguments
	if len(sys.argv) < 2:
		printHelp()
		sys.exit()
	args = iter(sys.argv[1:])
	for arg in args:
		if(arg == '-h'):
			printHelp()
			sys.exit()
		elif(arg == '-n'):
			commit = False
		elif(arg == '-i'):
			indir = getArgStr('-i', args)
		elif(arg == '-o'):
			outdir = getArgStr('-o', args)
		else:
			if arg == sys.argv[-1] and arg[0] != '-':
				cmd = arg
			else:
				doError('Invalid argument: '+arg, True)

	if not cmd:
		doError('No command given', True)

	# COMMAND PROCESSING
	if(cmd == 'sync'):
		if not indir:
			indir = getCardPath()
		if not indir:
			doError('No input path specific (is the card mounted?)')
		syncVideo(indir, outdir, commit)
		syncImages(indir, outdir, commit)
	elif(cmd == 'info'):
		if not indir:
			indir = '.'
		getImageMetadata(indir, commit)
	elif(cmd == 'infoall'):
		if not indir:
			indir = '.'
		getImageMetadataAll(indir, commit)
	elif(cmd == 'organize'):
		if not indir:
			indir = '/media/whore/Archimedes/'
		organizeImages(indir, outdir)
	else:
		doError('Invalid command: '+cmd, True)
