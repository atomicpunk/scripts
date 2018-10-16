# SPDX-License-Identifier: GPL-2.0
PREFIX		?= /usr
DESTDIR		?=

all:
	@echo "Nothing to build"

install :
	install -d  $(DESTDIR)$(PREFIX)/bin
	install ddstat $(DESTDIR)$(PREFIX)/bin/
	install destroy $(DESTDIR)$(PREFIX)/bin/
	install far $(DESTDIR)$(PREFIX)/bin/
	install farif $(DESTDIR)$(PREFIX)/bin/
	install fif $(DESTDIR)$(PREFIX)/bin/
	install kernelbuild.sh $(DESTDIR)$(PREFIX)/bin/
	install kernelclean.sh $(DESTDIR)$(PREFIX)/bin/
	install kernelinstall.sh $(DESTDIR)$(PREFIX)/bin/
	install loop $(DESTDIR)$(PREFIX)/bin/

uninstall :
	rm -f $(DESTDIR)$(PREFIX)/bin/fif
	rm -f $(DESTDIR)$(PREFIX)/bin/ddstat
	rm -f $(DESTDIR)$(PREFIX)/bin/destroy
	rm -f $(DESTDIR)$(PREFIX)/bin/far
	rm -f $(DESTDIR)$(PREFIX)/bin/farif
	rm -f $(DESTDIR)$(PREFIX)/bin/fif
	rm -f $(DESTDIR)$(PREFIX)/bin/kernelbuild.sh
	rm -f $(DESTDIR)$(PREFIX)/bin/kernelclean.sh
	rm -f $(DESTDIR)$(PREFIX)/bin/kernelinstall.sh
	rm -f $(DESTDIR)$(PREFIX)/bin/loop
