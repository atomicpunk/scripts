#!/usr/bin/python

#
#    TimeLapse Maker - processing the images for a timelapse
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
#import numpy

sundatafile = '/home/tebrandt/.sundata'
tagmap = {
	'orientation': 'Exif.Image.Orientation',
	'artist': 'Exif.Image.Artist',
	'copyright': 'Exif.Image.Copyright',
}

tagdef = {
	'orientation': '1',
	'artist': 'Todd E Brandt',
	'copyright': 'Todd E Brandt <tebrandt@frontier.com> 2015',
}

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

class ImageInfo:
	model = ''
	timestamp = ''
	author = ''
	size = ''
	valid = True
	def __init__(self, file):
		import pyexiv2

		meta = pyexiv2.metadata.ImageMetadata(file)
		self.size = ''
		try:
			meta.read()
		except:
			self.model = ''
			self.timestamp = ''
			self.author = ''
			self.size = ''
			self.valid = False
		try:
			tag = meta.__getitem__('Exif.Image.Model')
			self.model = tag.value
		except:
			self.model = ''
		try:
			tag = meta.__getitem__('Exif.Image.DateTime')
			self.timestamp = tag.value
		except:
			self.timestamp = ''
		try:
			tag = meta.__getitem__('Exif.Image.Artist')
			self.author = tag.value
		except:
			self.author = ''
		try:
			tag = meta.__getitem__('Exif.Photo.PixelXDimension')
			width = tag.value
		except:
			width = 0
		try:
			tag = meta.__getitem__('Exif.Photo.PixelYDimension')
			height = tag.value
		except:
			height = 0
		if width or height:
			self.size = "%d x %d" % (width, height)
	def show(self):
		if self.author or self.model or self.timestamp or self.size:
			print("\t  Author: %s\n\t  Camera: %s\n\tDateTime: %s\n\t    Size: %s" % \
				(self.author, self.model, self.timestamp, self.size))

def getInfo(indir):
	for dirname, dirnames, filenames in os.walk(indir):
		for filename in sorted(filenames):
			file = os.path.join(dirname, filename)
			if not os.path.isfile(file):
				continue
			info = ImageInfo(file)
			if(info.valid):
				print file
				info.show()

def rotateImages(indir, outdir, amount):
	valid = ['90', '180', '270']
	if amount not in valid:
		doError("invalid rotation: %s not in %s" % (amount, valid), False)
	angle = int(amount)
	for filename in sorted(os.listdir(indir)):
		file = os.path.join(indir, filename)
		if not os.path.isfile(file):
			continue
		outfile = os.path.join(outdir, filename)
		print("%s rotate by %d: %s" % (filename, angle, outfile))
		img = cv2.imread(file)
		h, w = img.shape[:2]
		center = (h/2,w/2)
		rotmat = cv2.getRotationMatrix2D(center, angle, 1.0)
		o = (h,w)
		if(angle != 180):
			o = (w,h)
		newimg = cv2.warpAffine(img, rotmat, o, flags=cv2.INTER_LINEAR)
		cv2.imwrite(outfile, newimg)

def cropImages(indir, outdir, nw, nh):
	if not nw and not nh:
		return
	for filename in sorted(os.listdir(indir)):
		file = os.path.join(indir, filename)
		if not os.path.isfile(file):
			continue
		outfile = os.path.join(outdir, filename)
		img = cv2.imread(file)
		h, w = img.shape[:2]
		h2 = h
		if(nh):
			h2 = nh
		w2 = w
		if(nw):
			w2 = nw
		print("%s crop to %dx%d: %s" % (filename, w2, h2, outfile))
		y = h - h2
		img = img[y:h, 0:w2]
		cv2.imwrite(outfile, img)

def resizeImages(indir, outdir, nw, nh):
	if not nw and not nh:
		return
	for filename in sorted(os.listdir(indir)):
		file = os.path.join(indir, filename)
		if not os.path.isfile(file):
			continue
		img = cv2.imread(file)
		h, w = img.shape[:2]
		if nw and nh:
			rx = float(nw) / float(w)
			ry = float(nh) / float(h)
			print("%s : %dx%d -> %dx%d" % (filename, w, h, nw, nh))
		elif nw:
			rx = float(nw) / float(w)
			ry = rx
			print("%s : %dx%d -> %dx%d" % (filename, w, h, nw, int(h*ry)))
		elif nh:
			ry = float(nh) / float(h)
			rx = ry
			print("%s : %dx%d -> %dx%d" % (filename, w, h, int(w*rx), nh))
		else:
			continue
		newimg = cv2.resize(img, (0,0), fx=rx, fy=ry)
		cv2.imwrite(os.path.join(outdir, filename), newimg)

def matchTemplate(img, template, meth):
	methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
		'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']
	if meth not in methods:
		return 0
	method = eval(meth)
	h, w = template.shape[:2]
	# Apply template Matching
	res = cv2.matchTemplate(img, template, method)
	min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
	# If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
	if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
		top_left = min_loc
	else:
		top_left = max_loc
	return (top_left, (w, h))

def showMatch(img, template, x, y, w, h, filename):
	from matplotlib import pyplot as plt

	imgcpy = img.copy()
	cv2.rectangle(imgcpy, (x,y), (x + w, y + h), 255, 5)
	plt.subplot(221),plt.imshow(imgcpy, cmap = 'gray')
	plt.title(filename), plt.xticks([]), plt.yticks([])
	imgnew = img.copy()
	imgnew = imgnew[0:y+h, x:x+w]
	plt.subplot(222), plt.imshow(imgnew, cmap = 'gray')
	plt.title('Cropped Result'), plt.xticks([]), plt.yticks([])
	imgnew = img.copy()
	imgnew = imgnew[y:y+h, x:x+w]
	plt.subplot(223), plt.imshow(template, cmap = 'gray')
	plt.title('template'), plt.xticks([]), plt.yticks([])
	plt.subplot(224), plt.imshow(imgnew, cmap = 'gray')
	plt.title('match'), plt.xticks([]), plt.yticks([])
	mtext = "Match found at x(%d, %d) y(%d, %d)" % (x, x+w, y, y+h)
	plt.suptitle(mtext)
	plt.show()

def findMatches(indir, tfile):
	template = cv2.imread(tfile)
	for filename in sorted(os.listdir(indir)):
		file = os.path.join(indir, filename)
		if not os.path.isfile(file):
			continue
		img = cv2.imread(file)
		m = matchTemplate(img, template, 'cv2.TM_CCOEFF_NORMED')
		if m:
			(x, y), (w, h) = m
			print("%s: MATCH X(%d, %d) Y(%d, %d)" % \
				(filename, x, x+w, y, y+h))
			showMatch(img, template, x, y, w, h, filename)
		else:
			print("%s: NO MATCH")

def cropImageByMatch(indir, outdir, tfile):
	template = cv2.imread(tfile)
	for filename in sorted(os.listdir(indir)):
		file = os.path.join(indir, filename)
		if not os.path.isfile(file):
			continue
		print filename
		outfile = os.path.join(outdir, filename)
		img = cv2.imread(file)
		m = matchTemplate(img, template, 'cv2.TM_CCOEFF_NORMED')
		if not m:
			print("%s: NO MATCH")
			continue
		(x, y), (w, h) = m
		s = y + h - 3000
		if(s < 0):
			s = 0
		t = 3000
		ih, iw = img.shape[:2]
		if(x+t > iw):
			print("Size exceeds: x0=%d, x1=%d, image x1=%d" % (x, x+t, iw))
			t = iw - x
		print("\tMATCH X(%d, %d) Y(%d, %d) W(%d) H(%d)" % (x, x+t, s, y+h, t, y+h-s))
		img = img[s:y+h, x:x+t]
		print("\tWriting %s" % outfile)
		cv2.imwrite(outfile, img)

def createVideo(indir, outfile, slow):
	tempdir = tempfile.mkdtemp(prefix='timelapse')
	num = 0
	for filename in sorted(os.listdir(indir)):
		file = os.path.join(indir, filename)
		if not os.path.isfile(file):
			continue
		tfile = os.path.join(tempdir, "image_%05d.jpg" % num)
		shutil.copy(file, tfile)
		num += 1
	cmd = 'avconv -y -i '+tempdir+\
		'/image_%05d.jpg -c:v libx264 -r 24 -vf "setpts='+\
		'%d'%slow+'.0*PTS" '+outfile
	os.system(cmd)
	shutil.rmtree(tempdir)

def isDay(lvl=''):
	if not lvl:
		lvl = lightLevel()
	if lvl in ['twilight (civil)', 'day']:
		return True
	return False

def lightLevel():
	times = ['atb', 'ntb', 'ctb', 'snr', 'sns', 'cte', 'nte', 'ate']
	cv = {
		'atb' : 'night',
		'ntb' : 'twilight (astro)',
		'ctb' : 'twilight (nautical)',
		'snr' : 'twilight (civil)',
		'sns' : 'day',
		'cte' : 'twlight (civil)',
		'nte' : 'twilight (nautical)',
		'ate' : 'twilight (astro)',
		'def' : 'night',
	}
	table = getSunriseSunset(False)
	now = datetime.now()
	next = 'def'
	for val in times:
		if now < table[val]:
			next = val
			break
	return cv[next]

def getSunriseSunset(output=False):
	table = {}
	cv = {
		'astronomical_twilight_begin': 'atb',
		'nautical_twilight_begin': 'ntb',
		'civil_twilight_begin': 'ctb',
		'sunrise': 'snr',
		'sunset': 'sns',
		'civil_twilight_end': 'cte',
		'nautical_twilight_end': 'nte',
		'astronomical_twilight_end': 'ate'
	}

	# if the config file is more than 12 hours old, rewrite it
	if(os.path.exists(sundatafile)):
		mt = time.ctime(os.path.getmtime(sundatafile))
		mt = datetime.now() - datetime.strptime(mt, '%a %b %d %H:%M:%S %Y')
		if mt.seconds < 43200:
			fp = open(sundatafile, 'r')
			for line in fp:
				if output:
					print line[0:-1]
				val = line[0:3]
				s = datetime.today().strftime('%Y-%m-%d ') + line[7:-1]
				table[val] = datetime.strptime(s, '%Y-%m-%d %I:%M:%S %p')
			fp.close()
			return table
	times = {
		'sunset' : '', 'sunrise' : '',
		'civil_twilight_begin' : '', 'civil_twilight_end' : '',
		'nautical_twilight_begin' : '', 'nautical_twilight_end' : '',
		'astronomical_twilight_begin' : '', 'astronomical_twilight_end' : ''
	}
	fp = urllib.urlopen("http://api.sunrise-sunset.org/json?lat=45.518182&lng=-122.902098&date=today")
	data = json.JSONDecoder().decode(fp.read())
	fp.close()
	if 'status' not in data or data['status'] != 'OK' :
		doError('couldnt get sunrise sunset times', False)
		return
	utc = int((datetime.now() - datetime.utcnow()).total_seconds())
	for val in times:
		s = datetime.today().strftime('%Y-%m-%d ') + data['results'][val]
		s = datetime.strptime(s, '%Y-%m-%d %I:%M:%S %p') - timedelta(seconds=-utc)
		table[cv[val]] = s
		times[val] = s.strftime('%I:%M:%S %p')

	out =  'atb : %s\n' % times['astronomical_twilight_begin']
	out += 'ntb : %s\n' % times['nautical_twilight_begin']
	out += 'ctb : %s\n' % times['civil_twilight_begin']
	out += 'snr : %s\n' % times['sunrise']
	out += 'sns : %s\n' % times['sunset']
	out += 'cte : %s\n' % times['civil_twilight_end']
	out += 'nte : %s\n' % times['nautical_twilight_end']
	out +=   'ate : %s' % times['astronomical_twilight_end']

	fp = open(sundatafile, 'w')
	fp.write(out+'\n')
	fp.close()
	if output:
		print out

	return table

# Brightness                128 (50%)       0 - 255
# Contrast                  128 (50%)       0 - 255
# Saturation                128 (50%)       0 - 255
# White Balance Temperature, Auto True      True | False
# Gain                      0 (0%)          0 - 255
# Power Line Frequency      60 Hz           Disabled | 50 Hz | 60 Hz
# White Balance Temperature 6500 (100%)     2000 - 6500
# Sharpness                 128 (50%)       0 - 255
# Backlight Compensation    0               0 - 1
# Exposure, Auto            Aperture Priority Mode Manual Mode | Aperture Priority Mode
# Exposure (Absolute)       250 (12%)       3 - 2047
# Exposure, Auto Priority   True            True | False
# Pan (Absolute)            0 (50%)         -36000 - 36000
# Tilt (Absolute)           0 (50%)         -36000 - 36000
# Focus (absolute)          75 (30%)        0 - 250
# Focus, Auto               False           True | False
# Zoom, Absolute            100 (0%)        100 - 500
def snapShot(device, name):
	now = datetime.now()
	sz = '1920x1080'
	outdir = '/home/tebrandt/Pictures/'+name
	outfile = now.strftime('garden-%m%d%y-%H%M%S.jpg')
	if isDay():
		exp = '-s "White Balance Temperature, Auto=True" '+\
			  '-s "Exposure, Auto=Aperture Priority Mode" '+\
			  '-s "Exposure (Absolute)=250" '+\
			  '-s "Exposure, Auto Priority=True"'
	else:
		exp = '-s "White Balance Temperature, Auto=False" '+\
			  '-s "Exposure, Auto=Manual Mode" '+\
			  '-s "Exposure (Absolute)=250" '+\
			  '-s "Exposure, Auto Priority=False"'
	cmd = 'fswebcam -d %s -r %s --no-banner %s -s "Focus, Auto=False" -s "Focus (absolute)=74" %s/%s' \
			% (device, sz, exp, outdir, outfile)
	print cmd
	os.system(cmd)
	shutil.copyfile(outdir+'/'+outfile, outdir+'/last.jpg')

# Function: printHelp
# Description:
#	 print out the help text
def printHelp():
	keys = []
	for tag in tagmap: keys.append(tag)
	print('')
	print('Timelapse Maker')
	print('Usage: timelapse.py <options> command')
	print('')
	print('Description:')
	print('   Create timelapse videos from sets of images')
	print('Options:')
	print('   -h             Print this help text')
	print('   -i <dirname>   Input file folder')
	print('   -o <dirname>   Output file folder')
	print('   -temp <file>   Template image for matching')
	print('   -width <int>   Image width')
	print('   -height <int>  Image height')
	print('   -slow <int>    slow video by factor of N')
	print('   -title <str>   output title')
	print('Commands:')
	print('   get-<tag>   : get a tag value in all images (-i)')
	print('   reset-<tag> : reset a tag value in all images (-i)')
	print('               : <tag> = %s' % keys)
	print('               : <tag> = Exif.* (read-only)')
	print('   info      : print basic metadata for image files recursively (-i)')
	print('   resize    : resize all images (-i,-o,-width,-height)')
	print('   crop      : crop all images (-i,-o,-width,-height)')
	print('   matches   : find the template in the images (-i,-temp)')
	print('   align     : crop images to align with match (-i,-o,-temp)')
	print('   video     : make a timelapse mp4 video')
	print('   sunrise   : get the local sunrise/sunset times for portland')
	print('   light     : get the current light level (night, day, twilight, etc)')
	print('   snapshot  : get a snapshot from the attached webcam')
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

	# argument data
	indir = '.'
	outdir = '.'
	imgwidth = 0
	imgheight = 0
	tfile = ''
	title=''
	slow = 1
	cmd = ''

	# loop through the command line arguments
	if len(sys.argv) < 2:
		printHelp()
		sys.exit()
	args = iter(sys.argv[1:])
	for arg in args:
		if(arg == '-h'):
			printHelp()
			sys.exit()
		elif(arg == '-i'):
			indir = getArgStr('-i', args)
		elif(arg == '-o'):
			outdir = getArgStr('-o', args)
		elif(arg == '-temp'):
			tfile = getArgStr('-temp', args)
		elif(arg == '-title'):
			title = getArgStr('-title', args)
		elif(arg == '-width'):
			imgwidth = getArgInt('-width', args)
		elif(arg == '-height'):
			imgheight = getArgInt('-height', args)
		elif(arg == '-slow'):
			slow = getArgInt('-slow', args)
		else:
			if arg == sys.argv[-1] and arg[0] != '-':
				cmd = arg
			else:
				doError('Invalid argument: '+arg, True)

	# command and input/output check
	if not cmd:
		doError('No command given', True)
	if not os.path.isdir(indir):
		doError('Input folder not found - '+indir, True)
	if not os.path.isdir(outdir):
		doError('Input folder not found - '+outdir, True)

	# COMMAND PROCESSING
	# rotate images by 90 degree multiplier
	if(cmd.startswith('rotate')):
		rotateImages(indir, outdir, cmd[6:])
	# get tag value by name or nick
	elif(cmd.startswith('info')):
		getInfo(indir)
	# get tag value by name or nick
	elif(cmd.startswith('get-')):
		tagname = cmd[4:]
		if tagname in tagmap:
			getTag(indir, tagmap[tagname])
		elif tagname.startswith('Exif.'):
			getTag(indir, tagname)
		else:
			doError('Unknown image property/tag - '+tagname, True)
	# reset tag value by nick
	elif(cmd.startswith('reset-')):
		tagname = cmd[6:]
		if tagname in tagmap:
			setTag(indir, tagmap[tagname], tagdef[tagname])
		else:
			doError('Unknown image property/tag - '+tagname, True)
	# resize images by height or width multipler
	elif(cmd == 'resize'):
		if not imgwidth and not imgheight:
			doError('No width or height supplied', True)
		resizeImages(indir, outdir, imgwidth, imgheight)
	# crop images to new height and/or width
	elif(cmd == 'crop'):
		if not imgwidth and not imgheight:
			doError('No width or height supplied', True)
		cropImages(indir, outdir, imgwidth, imgheight)
	# matches for the given template in all the images (GUI)
	elif(cmd == 'matches'):
		print findMatches(indir, tfile)
	# resize/crop all images using the template match as anchor
	elif(cmd == 'align'):
		print cropImageByMatch(indir, outdir, tfile)
	# create the timelapse video
	elif(cmd == 'video'):
		if not title:
			title = 'output.mp4'
		createVideo(indir, title, slow)
	# retrieve the sunset/sunrise times
	elif(cmd == 'sunrise'):
		getSunriseSunset(True)
	# print the current light level
	elif(cmd == 'light'):
		lvl = lightLevel()
		print('Light Level is %s' % lvl)
		print('Daylight = %s' % isDay(lvl))
	# retrieve the sunset/sunrise times
	elif(cmd == 'snapshot'):
		snapShot('/dev/video0', 'garden')
	else:
		doError('Invalid command: '+cmd, True)
