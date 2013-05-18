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

photogoodexts = [".*\.jpg$", ".*\.jpeg$"];
photopath = "/media/fatman/Pictures"
thumbpath = "/media/fatman/thumbPictures"

def isFileType(path, exts):
    for ext in exts:
        check = path.lower()
        if(re.match(ext, check) != None):
            return True
    return False

def genThumbs(inpath, outpath, exts):
    for dirname, dirnames, filenames in os.walk(inpath):
        for filename in filenames:
            srcpath = os.path.join(dirname, filename)
            if(isFileType(filename, exts)):
                srcpath = os.path.join(dirname, filename)
                newdir = string.replace(dirname, inpath, outpath)
                dstpath = os.path.join(newdir, filename)
                if(not os.path.isdir(newdir)):
                    os.makedirs(newdir)
                    print(newdir)
                cmd = "convert -define jpeg:size=50x50 %s -thumbnail 50x50^ -gravity center -extent 50x50 %s" % (srcpath, dstpath)
                print(cmd)

genThumbs(photopath, thumbpath, photogoodexts)

