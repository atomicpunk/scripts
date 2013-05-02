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
                 ".*\.iso$", ".*\.3gp$", ".*\.mov$", ".*\.m2ts$", 
                 ".*\.wmv$", ".*\.ra$", ".*\.asf$", ".*\.mp3$", 
                 ".*\.vob$", ".*\.rm$", ".*\.jpg$", ".*\.mpeg$",
                 ".*\.ram$", ".*\.ogm$", ".*\.qt$"];
videobadexts = [".*\.torrent$", ".*\.rar$", ".*\.png$", ".*\.idx$", 
                ".*\.txt$", ".*\.nfo$", ".*\.index$", ".*\.db$", 
                ".*\.cc$", ".*\.par2$", ".*\.lnk$", ".*\.gif$", 
                ".*\.rtf$", ".*\.ini$", ".*\.gif$", ".*\.smi$", 
                ".*\.m3u$", ".*\.bup$", ".*\.ifo$", ".*\.rtf$", 
                ".*\.url$", ".*\.jpeg$", ".*\.hlp$", ".*\.ico$", 
                ".*\.js$", ".*\.jpe$", ".*\.css$", ".*\.pdf$",
                ".*\.htm$", ".*\.html$", ".*\.ttf$",
                ".*\.md5$", ".*\.r[0-9][0-9]$", ".*\.jpg$", ".*sample.avi$", 
                ".*sample.mpg$", ".*sample.mkv$", ".*sample.mp4$"];

target=""
applychanges = False
lpath="/media/fatman"
rpath="/media/downstairs"

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
                        print "FILE IN USE by %s: %s" % (proc.name, nt.path)
                        filesinuse.append(nt.path)
        except psutil.NoSuchProcess as err:
            print("****",err)

def dirInUse(dirname):
    global filesinuse
    for file in filesinuse:
        if(string.find(file, dirname) == 0):
            return True
    return False

def isInUse(filepath):
    global filesinuse
    for file in filesinuse:
        if(file == filepath):
            return True
    return False

def processDir(path, gexts, bexts, commit):
    for dirname, dirnames, filenames in os.walk(os.path.join(lpath, path)):
        rdirname = string.replace(dirname, lpath, rpath);
        if(os.path.exists(rdirname) == False):
            print "MISSING DIR %s" % rdirname
            if(commit):
                os.mkdir(rdirname)
        for filename in filenames:
            srcpath = os.path.join(dirname, filename)
            if(isInUse(srcpath)):
                continue
            if(isFileType(filename, gexts)):
                srcpath = os.path.join(dirname, filename)
                rsrcpath = string.replace(srcpath, lpath, rpath);
                if(os.path.exists(rsrcpath) == False):
                    print "COPY %s" % srcpath
                    if(commit):
                        shutil.copy(srcpath, rsrcpath)
            elif(isFileType(filename, bexts)):
                srcpath = os.path.join(dirname, filename)
                print "DELETE %s" % srcpath
                if(commit):
                    os.remove(srcpath)
                rsrcpath = string.replace(srcpath, lpath, rpath);
                if(os.path.exists(rsrcpath) == True):
                    print "DELETE %s" % rsrcpath
                    if(commit):
                        os.remove(rsrcpath)
            else:
                print "UNKNOWN FILE %s" % srcpath
                if(commit):
                    sys.exit();

def pruneEmptyDirs(path, commit):
    emptyparent = []
    for dirname, dirnames, filenames in os.walk(os.path.join(lpath, path)):
        if(dirname == path):
            continue
        elif(dirInUse(dirname)):
            print "DIRINUSE: %s" % dirname
            continue
        elif((len(filenames) == 0) and (len(dirnames) == 0)):
            print "RMDIR: %s" % dirname
            if(commit):
                os.rmdir(dirname)
            rdirname = string.replace(dirname, lpath, rpath);
            if(os.path.exists(rdirname) == True):
                print "RMDIR: %s" % rdirname
                if(commit):
                    os.rmdir(rdirname)
        elif(len(filenames) == 0):
            emptyparent.append(dirname)
        elif(len(filenames) > 0):
            falseemptyparent = []
            for parent in emptyparent:
               if(string.find(dirname, parent) == 0):
                   falseemptyparent.append(parent)
            for falseparent in falseemptyparent:
               emptyparent.remove(falseparent)

    if(len(emptyparent) > 0):
        if(commit):
            pruneEmptyDirs(path, commit)
        else:
            for parent in emptyparent:
                print "EMPTY PARENT: %s" % parent

if(len(sys.argv) < 2):
    print "Usage: organize.py target <applychanges>"
    sys.exit();
elif(len(sys.argv) < 3):
    applychanges = False
    target = sys.argv[1];
    print "READ-ONLY MODE, the filesystem will NOT be modified"
elif((len(sys.argv) == 3) and (sys.argv[2].lower() == "applychanges")):
    target = sys.argv[1];
    print "WRITE MODE, the filesystem WILL be modified!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    answer = raw_input('Are you totally, seriously, really sure you want this? ')
    if(answer.lower() == "yes"):
        print "OK then!"
        applychanges = True
    elif(answer.lower() == "no"):
        print "No? SIGH, then why'd you call me damnit! ;) BYE!"
        sys.exit();
    else:
        print "I don't know what %s means, so I\'m quitting just to be safe, BYE!" % answer
        sys.exit();
else:
    print "Usage: organize.py target <applychanges>"
    sys.exit();

print "\nPROCESSING MOVIE FILES IN %s ...\n" % target
filesInUse(target)
processDir(target, videogoodexts, videobadexts, applychanges)
print "\nPRUNING EMPTY DIRECTORIES IN %s ...\n" % target
filesInUse(target)
pruneEmptyDirs(target, applychanges)
