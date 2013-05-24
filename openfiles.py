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
import time

def filesInUse(dirname, filesinuse):
    for proc in psutil.process_iter():
        try:
            flist = proc.get_open_files()
            if flist:
                for nt in flist:
                    if(string.find(nt.path, dirname) == 0):
                        fstring = proc.name+": "+nt.path
                        filesinuse.append(fstring)
        except psutil.NoSuchProcess as err:
            print("****",err)

if(len(sys.argv) != 2):
    print "Usage: openfiles.py folder"
    sys.exit();

p_inuse = []
c_inuse = []
while(1):
    filesInUse(sys.argv[1], c_inuse)
    for file in c_inuse:
        if file not in p_inuse:
            p_inuse.append(file)
            print(file)
    time.sleep(1)
