#!/usr/bin/python3

import sys
import os
import os.path as op
import shutil
from tempfile import NamedTemporaryFile, mkdtemp
from datetime import time, datetime, timedelta
from subprocess import call, Popen, PIPE
import argparse

URL="https://cdn.star.nesdis.noaa.gov/GOES17/ABI/SECTOR/pnw"
FOLDER = '/home/tebrandt/workspace/satellite/GOES'
DAYDIR = FOLDER+'/cdn.star.nesdis.noaa.gov/GOES17/ABI/SECTOR/pnw/GEOCOLOR'
NIGHTDIR = FOLDER+'/cdn.star.nesdis.noaa.gov/GOES17/ABI/SECTOR/pnw/07'
DIRS=["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12",
	"13", "14", "15", "16", "AirMass", "DayCloudPhase", "GEOCOLOR",
	"NightMicrophysics", "Sandwich"]

def syncImages():
	for dir in DIRS:
		cmd = 'cd %s; wget -nc -r --no-parent -A \'*1200x1200.jpg\' -e robots=off %s/%s/' % \
			(FOLDER, URL, dir)
		call(cmd, shell=True)

def readImages(dir):
	out = dict()
	for img in os.listdir(dir):
		if len(img) > 30:
			dt = datetime.strptime(img[:11], '%Y%j%H%M') - timedelta(hours=7)
			out[dt] = img
	return out

def sortImages(folder):
	i, sunrise, sunset = 0, time(7, 30, 0, 0), time(18, 26, 0, 0)
	dayhash = readImages(DAYDIR)
	nighthash = readImages(NIGHTDIR)
	for dt in sorted(dayhash):
		t = dt.time()
		if t >= sunrise and t < sunset:
			img = op.join(DAYDIR, dayhash[dt])
			print('  DAY(%s) %s' % (t.strftime('%H:%M'), dayhash[dt]))
		else:
			img = op.join(NIGHTDIR, nighthash[dt])
			print('NIGHT(%s) %s' % (t.strftime('%H:%M'), nighthash[dt]))
		shutil.copy(img, '%s/image%05d.jpg' % (folder, i))
		i += 1

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('video')
	args = parser.parse_args()

	syncImages()
	tmpdir = mkdtemp(prefix='daynight')
	sortImages(tmpdir)
	cmd = 'avconv -y -i %s/image%%05d.jpg -c:v libx264 -r 24 %s' % (tmpdir, args.video)
	call(cmd, shell=True)
	shutil.rmtree(tmpdir)
