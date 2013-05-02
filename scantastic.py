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
import string
import tempfile
import re
import array
import datetime

def executeScan(filename, res):
    print("Scan resolution = %s") % res
    tiff = tempfile.NamedTemporaryFile(suffix='.tiff').name
    tmp = tempfile.NamedTemporaryFile(suffix='.jpg').name
    print("Scanning image to %s ...") % tiff
    if(res == "highsmall"):
        os.system("scanimage -d kodakaio --resolution=600 -x 130mm -y 130mm --format=tiff --mode=Color > "+tiff)
        args = "convert "+tiff+" -format \"%wx%h%O\" -despeckle -blur 0x15 -fuzz 20% -trim "
    elif(res == "highhuge"):
        os.system("scanimage -d kodakaio --resolution=600 --format=tiff --mode=Color > "+tiff)
        args = "convert "+tiff+" -format \"%wx%h%O\" -despeckle -blur 0x15 -despeckle -fuzz 30% -trim "
    elif(res == "highbig"):
        os.system("scanimage -d kodakaio --resolution=600 -x 200mm -y 200mm --format=tiff --mode=Color > "+tiff)
        args = "convert "+tiff+" -format \"%wx%h%O\" -despeckle -blur 0x15 -despeckle -fuzz 30% -trim "
    elif(res == "minisnap"):
        os.system("scanimage -d kodakaio --resolution=600 -x 140mm -y 140mm --format=tiff --mode=Color > "+tiff)
        args = "convert "+tiff+" -format \"%wx%h%O\" -despeckle -blur 0x15 -fuzz 20% -trim "
    elif(res == "nminisnap"):
        os.system("scanimage -d kodakaio --resolution=300 -x 140mm -y 140mm --format=tiff --mode=Color > "+tiff)
        args = "convert "+tiff+" -format \"%wx%h%O\" -despeckle -blur 0x15 -fuzz 20% -trim "
    elif(res == "normalbig"):
        os.system("scanimage -d kodakaio --resolution=300 --format=tiff --mode=Color > "+tiff)
        args = "convert "+tiff+" -format \"%wx%h%O\" -crop 99%x+0+0 -despeckle -blur 0x2 -fuzz 20% -trim "
    elif(res == "normalhuge"):
        os.system("scanimage -d kodakaio --resolution=300 --format=tiff --mode=Color > "+tiff)
        args = "convert "+tiff+" -format \"%wx%h%O\" -despeckle -blur 0x15 -despeckle -fuzz 30% -trim "
    elif(res == "doc"):
        os.system("scanimage -d kodakaio --resolution=150 --format=tiff --mode=Color > "+tiff)
        args = "convert "+tiff+" -format \"%wx%h%O\" -crop 99%x+0+0 -despeckle -blur 0x2 -fuzz 20% -trim "
    elif(res == "normal"):
        os.system("scanimage -d kodakaio --resolution=300 --format=tiff --mode=Color > "+tiff)
        args = "convert "+tiff+" -format \"%wx%h%O\" -despeckle -trim "
    elif(res == "high"):
        os.system("scanimage -d kodakaio --resolution=600 --format=tiff --mode=Color > "+tiff)
        args = "convert "+tiff+" -format \"%wx%h%O\" -despeckle -trim "
    else:
        os.system("scanimage -d kodakaio --resolution=300 --format=tiff --mode=Color > "+tiff)
        args = "convert "+tiff+" -format \"%wx%h%O\" -crop 90%x+0+0 -despeckle -blur 0x2 -fuzz 20% -trim "
    if(not os.path.isfile(tiff)):
        print("ERROR: %s not found, scan failed") % tiff
        sys.exit()
    size = os.popen(args+"info:").read().strip()
    print("Cropping to %s") % size
    os.system(args+tmp)
    print("Storing image as %s ...") % filename
    os.system("convert "+tiff+" -crop "+size+" "+filename)
    os.remove(tiff)
    os.remove(tmp)

def processDir(outdir, file):
    if(not os.path.isdir(outdir)):
        return -1
    index = 0
    for dirname, dirnames, filenames in os.walk(outdir):
        for filename in filenames:
            m = re.match(r""+file+"(?P<idx>[0-9]*).jpg", filename)
            if(m):
                i = int(m.group("idx"))
                if(i > index):
                    index = i
    return index

imgdir = "/media/tebrandt/fatman2/Pictures/scans/"
docdir = "/media/tebrandt/fatman2/Pictures/docs/"
outdir = imgdir
file = "scan"
cmd = ""
if(len(sys.argv) > 1):
    cmd = sys.argv[1]
    if(cmd == "doc"):
        outdir = docdir
        file = "doc"
index = processDir(outdir, file)
if(index < 0):
    print("ERROR: %s not found") % outdir
    sys.exit()
index += 1
filename = outdir+file+"%d.jpg"%index
executeScan(filename, cmd)
