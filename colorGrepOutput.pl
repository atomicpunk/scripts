#!/usr/bin/perl -Ilib
# Author: Joe Grossberg
# Author's Site: http://www.joegrossberg.com/archives/000386.html
# Contributer Todd Brandt <todd.e.brandt@intel.com>


while (<>) {
    if ($_ =~ /^BINARY.*/) {
	; # do nothing
    } elsif ($_ =~ /^([^:]*)(:)([^:]*)(:)(.*)/) {
	print "\033[1;34m"; # start blue
	print $1;           # file name
	print "\033[0m";    # end blue
	print $2;           # first colon
	print "\033[1;36m"; # start aqua
	print $3;           # line number
	print "\033[0m";    # end aqua
	print $4;           # second colon
	print $5;           # matching text
	print "\n";
    }
}

