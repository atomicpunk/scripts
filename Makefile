# SPDX-License-Identifier: GPL-2.0
PREFIX		?= /usr
DESTDIR		?=

all:
	@echo "Nothing to build, sorry"

install :
	install -d  $(DESTDIR)$(PREFIX)/bin
	install ddstat $(DESTDIR)$(PREFIX)/bin/
	install destroy $(DESTDIR)$(PREFIX)/bin/
	install far $(DESTDIR)$(PREFIX)/bin/
	install farif $(DESTDIR)$(PREFIX)/bin/
	install fif $(DESTDIR)$(PREFIX)/bin/
	install kernelbuild.sh $(DESTDIR)$(PREFIX)/bin/
	install kernelclean.sh $(DESTDIR)$(PREFIX)/bin/
	install loop $(DESTDIR)$(PREFIX)/bin/
	install multiterm.py $(DESTDIR)$(PREFIX)/bin/multiterm
	install pi.py $(DESTDIR)$(PREFIX)/bin/pi
	install privacy.sh $(DESTDIR)$(PREFIX)/bin/privacy
	install wgetmask.sh $(DESTDIR)$(PREFIX)/bin/wgetmask
	install mp3make.sh $(DESTDIR)$(PREFIX)/bin/mp3make
	install noproxy $(DESTDIR)$(PREFIX)/bin/noproxy
	install tl.sh $(DESTDIR)$(PREFIX)/bin/timelapse
	install goes.py $(DESTDIR)$(PREFIX)/bin/goes

uninstall :
	rm -f $(DESTDIR)$(PREFIX)/bin/fif
	rm -f $(DESTDIR)$(PREFIX)/bin/ddstat
	rm -f $(DESTDIR)$(PREFIX)/bin/destroy
	rm -f $(DESTDIR)$(PREFIX)/bin/far
	rm -f $(DESTDIR)$(PREFIX)/bin/farif
	rm -f $(DESTDIR)$(PREFIX)/bin/fif
	rm -f $(DESTDIR)$(PREFIX)/bin/kernelbuild.sh
	rm -f $(DESTDIR)$(PREFIX)/bin/kernelclean.sh
	rm -f $(DESTDIR)$(PREFIX)/bin/loop
	rm -f $(DESTDIR)$(PREFIX)/bin/multiterm
	rm -f $(DESTDIR)$(PREFIX)/bin/pi
	rm -f $(DESTDIR)$(PREFIX)/bin/privacy
	rm -f $(DESTDIR)$(PREFIX)/bin/mp3make
	rm -f $(DESTDIR)$(PREFIX)/bin/noproxy
