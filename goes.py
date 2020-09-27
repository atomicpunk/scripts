#!/usr/bin/python3

import sys
import os
import os.path as op
import shutil
from tempfile import NamedTemporaryFile, mkdtemp
from datetime import time, datetime, timedelta
from subprocess import call, Popen, PIPE
import argparse
import ephem

URL="https://cdn.star.nesdis.noaa.gov/GOES17/ABI/SECTOR/pnw"
IMAGEDIR = '{0}/cdn.star.nesdis.noaa.gov/GOES17/ABI/SECTOR/pnw/{1}'
DIRS=["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12",
	"13", "14", "15", "16", "AirMass", "DayCloudPhase", "GEOCOLOR",
	"NightMicrophysics", "Sandwich"]

def sunRiseSet(date):
	mypos = ephem.Observer()
	mypos.lon = str(-122.902103)
	mypos.lat = str(45.518265)
	mypos.elev = 0
	mypos.pressure = 0
	mypos.horizon = '-0:34'
	mypos.date = date+' 19:00:00'
	fmt = '%Y/%m/%d %H:%M:%S'
	sunrise = datetime.strptime(str(mypos.previous_rising(ephem.Sun())), fmt) + timedelta(minutes=45)
	sunset = datetime.strptime(str(mypos.next_setting(ephem.Sun())), fmt) - timedelta(minutes=55)
	return (sunrise, sunset)

def syncImages(folder):
	for dir in DIRS:
		cmd = 'cd %s; wget -nc -r --no-parent -A \'*1200x1200.jpg\' -e robots=off %s/%s/' % \
			(folder, URL, dir)
		call(cmd, shell=True)

def readImages(dir):
	out = dict()
	for img in os.listdir(dir):
		if len(img) > 30:
			dt = datetime.strptime(img[:11], '%Y%j%H%M')
			out[dt] = img
	return out

def daynightImages(indir, tmpdir):
	daydir = IMAGEDIR.format(indir, 'GEOCOLOR')
	dayhash = readImages(daydir)
	nightdir = IMAGEDIR.format(indir, '07')
	nighthash = readImages(nightdir)
	i, sunrise, sunset = 0, 0, 0

	for dt in sorted(dayhash):
		if not sunrise or not sunset or dt > sunset:
			sunrise, sunset = sunRiseSet(dt.strftime('%Y-%m-%d'))
		if dt >= sunrise and dt < sunset or (dt not in nighthash):
			img = op.join(daydir, dayhash[dt])
			print('VIS(%s) %s' % (dt.strftime('%Y-%m-%d %H:%M'), dayhash[dt]))
		else:
			img = op.join(nightdir, nighthash[dt])
			print(' IR(%s) %s' % (dt.strftime('%Y-%m-%d %H:%M'), nighthash[dt]))
		shutil.copy(img, '%s/image%05d.jpg' % (tmpdir, i))
		i += 1

def sortImages(indir, tmpdir, name):
	i, dir = 0, IMAGEDIR.format(indir, name)
	imgs = readImages(dir)
	for dt in sorted(imgs):
		img = op.join(dir, imgs[dt])
		print('%s %s' % (dt.strftime('%d/%m/%y %H:%M'), imgs[dt]))
		shutil.copy(img, '%s/image%05d.jpg' % (tmpdir, i))
		i += 1

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='GOES Satellite Imagery Utility')
	parser.add_argument('-f', '-folder', metavar='folder', default='.',
		help='local folder where GOES imagery is located (default is current dir)')
	parser.add_argument('-s', '-sync', action='store_true',
		help='synchronize the latest GOES imagery to folder')
	parser.add_argument('-v', '-video', nargs=2, metavar=('imgtype', 'outfile'),
		help='generate a timelapse video from one of the image types')
	args = parser.parse_args()
	if len(sys.argv) < 2:
		parser.print_help()
		sys.exit(1)

	if not op.exists(args.f) or not op.isdir(args.f):
		print('ERROR: %s is not a valid folder' % args.f)
		sys.exit(1)

	if args.s:
		syncImages(args.f)

	if not args.v:
		sys.exit(0)

	imgtype, outfile = args.v
	if imgtype != 'daynight' and imgtype not in DIRS:
		print('ERROR: %s is not a valid image type, use one of these:' % imgtype)
		print(DIRS)
		sys.exit(1)

	tmpdir = mkdtemp(prefix=imgtype)
	if imgtype == 'daynight':
		daynightImages(args.f, tmpdir)
	else:
		sortImages(args.f, tmpdir, imgtype)
	cmd = 'avconv -y -i %s/image%%05d.jpg -c:v libx264 -r 24 %s' % (tmpdir, outfile)
	call(cmd, shell=True)
	shutil.rmtree(tmpdir)
