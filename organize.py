#!/usr/bin/python

import sys
import os
import shutil
import string
import re
import psutil
videogoodexts = [".*\.avi$", ".*\.mpg$", ".*\.mkv$", ".*\.mp4$", 
                 ".*\.srt$", ".*\.sub$", ".*\.sfv$", ".*\.divx$",
                 ".*\.iso$", ".*\.m2ts$"];
videobadexts = [".*\.torrent$", ".*\.rar$", ".*\.png$", ".*\.idx$", ".*\.txt$", ".*\.nfo$", ".*\.index$",
                ".*\.db$", ".*\.cc$", ".*\.par2$", ".*\.lnk$", ".*\.gif$", ".*\.rtf$", ".*\.ini$", ".*\.gif$",
                ".*\.smi$", 
                ".*\.rtf$", ".*\.url$", ".*\.jpeg$", ".*\.hlp$", ".*\.ico$", ".*\.md5$", ".*\.r[0-9][0-9]$",
                ".*\.jpg$", ".*sample.avi$", ".*sample.mpg$", ".*sample.mkv$", ".*sample.mp4$"];

applychanges = False
moviepath = "/media/fatman/Movies"
tvpath = "/media/fatman/TV"

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
            elif(isFileType(filename, gexts)):
                srcpath = os.path.join(dirname, filename)
                if(dirname != path):
                    print "MOVE %s" % srcpath
                    if(commit):
                        shutil.move(srcpath, path)
            else:
                print "UNKNOWN FILE %s" % srcpath

def pruneEmptyDirs(path, commit):
    emptyparent = []
    for dirname, dirnames, filenames in os.walk(path):
        if(dirname == path):
            continue
        elif(dirInUse(dirname)):
            print "DIRINUSE: %s" % dirname
            continue
        elif((len(filenames) == 0) and (len(dirnames) == 0)):
            print "RMDIR: %s" % dirname
            if(commit):
                os.rmdir(dirname)
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
    applychanges = False
    print "READ-ONLY MODE, the filesystem will NOT be modified"
elif((len(sys.argv) == 2) and (sys.argv[1].lower() == "applychanges")):
    print "WRITE MODE, the filesystem WILL be modified!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1"
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
    print "Usage: organize.py <applychanges>"
    sys.exit();

print "\nPROCESSING MOVIE FILES IN %s ...\n" % moviepath
filesInUse(moviepath)
processDir(moviepath, videogoodexts, videobadexts, applychanges)
print "\nPRUNING EMPTY DIRECTORIES IN %s ...\n" % moviepath
filesInUse(moviepath)
pruneEmptyDirs(moviepath, applychanges)
