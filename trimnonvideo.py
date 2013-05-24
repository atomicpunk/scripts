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
import psutil
videogoodexts = [".*\.avi$", ".*\.mpg$", ".*\.mkv$", ".*\.mp4$", 
                 ".*\.srt$", ".*\.sub$", ".*\.sfv$", ".*\.divx$",
                 ".*\.asf$", ".*\.rm$", ".*\.mov$", ".*\.vob$",
                 ".*\.3gp$", ".*\.qt$",
                 ".*\.iso$", ".*\.m2ts$", ".*\.m4v$", ".*\.mpeg$"];
videobadexts = [".*\.torrent$", ".*\.rar$", ".*\.png$", ".*\.idx$", ".*\.txt$", ".*\.nfo$", ".*\.index$",
                ".*\.db$", ".*\.cc$", ".*\.par2$", ".*\.lnk$", ".*\.gif$", ".*\.rtf$", ".*\.ini$", ".*\.gif$",
                ".*\.smi$", ".*\.pdf$", ".*\.mp3$",
                ".*\.rtf$", ".*\.url$", ".*\.jpeg$", ".*\.hlp$", ".*\.ico$", ".*\.md5$", ".*\.r[0-9][0-9]$",
                ".*\.jpg$", ".*sample.avi$", ".*sample.mpg$", ".*sample.mkv$", ".*sample.mp4$"];

filesinuse = []

def isFileType(path, exts):
    for ext in exts:
        check = path.lower()
        if(re.match(ext, check) != None):
            return True
    return False

def isFileName(filename, list):
    for name in list:
        if(filename.lower() == name):
            return True
    return False

def filesInUse(dirname):
    global filesinuse
    filesinuse = []
    for proc in psutil.process_iter():
        try:
            flist = proc.get_open_files()
            if flist:
                for nt in flist:
                    if(string.find(nt.path, dirname) == 0):
                        filesinuse.append(nt.path)
        except psutil.NoSuchProcess as err:
            print("****",err)

def isInUse(filepath):
    global filesinuse
    for file in filesinuse:
        if(file == filepath):
            return True
    return False

def processDir(path, gexts, bexts, commit):
    for dirname, dirnames, filenames in os.walk(path):
        for filename in filenames:
            srcpath = os.path.join(dirname, filename)
            if(isInUse(srcpath)):
                continue
            if(isFileType(filename, bexts)):
                srcpath = os.path.join(dirname, filename)
                print "DELETE %s" % srcpath
                if(commit):
                    os.remove(srcpath)
            elif(not isFileType(filename, gexts)):
                print "UNKNOWN FILE %s" % srcpath

apply = False
if(len(sys.argv) == 2):
    apply = False
elif((len(sys.argv) == 3) and (sys.argv[2] == "applychanges")):
    apply = True
else:
    print "Usage: trimnonvideo.py folder <applychanges>"
    sys.exit();

filesInUse(sys.argv[1])
processDir(sys.argv[1], videogoodexts, videobadexts, apply)
